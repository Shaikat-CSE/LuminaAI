"""
API routes for the LuminaAI application.
"""
import os
import uuid
import aiofiles
import aiofiles.os
import httpx
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.models.schemas import (
    UploadResponse,
    UploadURLRequest,
    QueryRequest,
    QueryResponse,
    HealthResponse,
    ErrorResponse
)
from app.services.rag_pipeline import rag_pipeline
from app.services.extractor import document_extractor


settings = get_settings()
router = APIRouter()


# ==================== Helper Functions ====================

async def save_upload_file(upload_file: UploadFile) -> Path:
    """Save an uploaded file to the upload directory."""
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}_{upload_file.filename}"
    file_path = settings.upload_dir / safe_filename
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await upload_file.read()
        await f.write(content)
    
    return file_path


async def download_file_from_url(url: str) -> tuple[Path, str]:
    """Download a file from a URL."""
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path) or "downloaded_file"
    
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}_{filename}"
    file_path = settings.upload_dir / safe_filename
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(response.content)
    
    return file_path, filename


async def cleanup_file(file_path: Path) -> None:
    """Remove a temporary file."""
    try:
        if file_path.exists():
            await aiofiles.os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up file {file_path}: {e}")


# ==================== Health Check ====================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the API"
)
async def health_check():
    """Check API health and return system status."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        vector_store=settings.vector_store_type,
        embedding_model=settings.embedding_model,
        document_count=rag_pipeline.get_document_count()
    )


# ==================== Upload Endpoints ====================

@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="Upload Document",
    description="Upload a document file for processing. Supports PDF, DOCX, TXT, JPG/PNG, CSV, and SQLite files.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file or unsupported format"},
        500: {"model": ErrorResponse, "description": "Processing error"}
    }
)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Document file to upload")
):
    """
    Upload and process a document file.
    
    The file will be:
    1. Saved temporarily
    2. Text will be extracted
    3. Split into chunks
    4. Embedded using SentenceTransformers
    5. Stored in the vector database
    """
    # Validate file type
    file_type = document_extractor.get_file_type(file.filename)
    if not file_type:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported types: {', '.join(document_extractor.SUPPORTED_EXTENSIONS.keys())}"
        )
    
    # Save the uploaded file
    file_path = await save_upload_file(file)
    
    try:
        # Process the file
        result = await rag_pipeline.process_file(file_path, file.filename)
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_file, file_path)
        
        if result.status == "error":
            raise HTTPException(status_code=500, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        background_tasks.add_task(cleanup_file, file_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/upload/url",
    response_model=UploadResponse,
    summary="Upload from URL",
    description="Download and process a document from a URL.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid URL or unsupported format"},
        500: {"model": ErrorResponse, "description": "Download or processing error"}
    }
)
async def upload_from_url(
    request: UploadURLRequest,
    background_tasks: BackgroundTasks
):
    """
    Download a document from a URL and process it.
    """
    try:
        file_path, filename = await download_file_from_url(request.url)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Failed to download file: {str(e)}")
    
    # Validate file type
    file_type = document_extractor.get_file_type(filename)
    if not file_type:
        background_tasks.add_task(cleanup_file, file_path)
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported types: {', '.join(document_extractor.SUPPORTED_EXTENSIONS.keys())}"
        )
    
    try:
        result = await rag_pipeline.process_file(file_path, filename)
        background_tasks.add_task(cleanup_file, file_path)
        
        if result.status == "error":
            raise HTTPException(status_code=500, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        background_tasks.add_task(cleanup_file, file_path)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Query Endpoint ====================

@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Query Documents",
    description="Ask a question about your uploaded documents. Optionally include an image for OCR.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid query"},
        500: {"model": ErrorResponse, "description": "Query processing error"}
    }
)
async def query_documents(request: QueryRequest):
    """
    Query the RAG system with a question.
    
    The query will:
    1. OCR the image if provided
    2. Search for relevant document chunks
    3. Build context from top results
    4. Generate answer using Gemini
    5. Return answer with source metadata
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = await rag_pipeline.query(
            question=request.question,
            image_base64=request.image_base64,
            top_k=request.top_k
        )
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Management Endpoints ====================

@router.delete(
    "/documents/{file_id}",
    summary="Delete Document",
    description="Delete all chunks for a specific document by file ID."
)
async def delete_document(file_id: str):
    """Delete a document and all its chunks from the vector store."""
    deleted_count = rag_pipeline.delete_file(file_id)
    
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "status": "success",
        "file_id": file_id,
        "deleted_chunks": deleted_count
    }


@router.delete(
    "/documents",
    summary="Clear All Documents",
    description="Delete all documents from the vector store."
)
async def clear_all_documents():
    """Clear all documents from the vector store."""
    count_before = rag_pipeline.get_document_count()
    rag_pipeline.clear_all()
    
    return {
        "status": "success",
        "deleted_chunks": count_before
    }


@router.get(
    "/stats",
    summary="Get Statistics",
    description="Get statistics about the document store."
)
async def get_stats():
    """Get statistics about the document store."""
    return {
        "document_count": rag_pipeline.get_document_count(),
        "vector_store": settings.vector_store_type,
        "embedding_model": settings.embedding_model,
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap
    }
