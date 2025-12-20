"""
RAG Pipeline service that orchestrates document processing and query handling.
"""
import uuid
import aiofiles
import aiofiles.os
from pathlib import Path
from typing import Optional

from app.core.config import get_settings
from app.services.extractor import document_extractor
from app.services.chunker import text_chunker, TextChunk
from app.services.embedder import embedding_service
from app.services.vector_store import vector_store, DocumentChunk, SearchResult
from app.services.gemini import gemini_service
from app.models.schemas import (
    UploadResponse,
    QueryResponse,
    SourceMetadata
)


settings = get_settings()


class RAGPipeline:
    """Orchestrates the RAG pipeline for document processing and querying."""
    
    def __init__(self):
        self.extractor = document_extractor
        self.chunker = text_chunker
        self.embedder = embedding_service
        self.vector_store = vector_store
        self.gemini = gemini_service
        self.settings = get_settings()
    
    async def process_file(
        self,
        file_path: Path,
        original_filename: str
    ) -> UploadResponse:
        """
        Process an uploaded file through the RAG pipeline.
        
        Steps:
        1. Extract text from the file
        2. Chunk the text
        3. Generate embeddings
        4. Store in vector database
        """
        file_id = str(uuid.uuid4())
        
        try:
            # Step 1: Extract text
            file_type = self.extractor.get_file_type(original_filename)
            if not file_type:
                return UploadResponse(
                    file_id=file_id,
                    filename=original_filename,
                    file_type="unknown",
                    chunk_count=0,
                    status="error",
                    message=f"Unsupported file type: {Path(original_filename).suffix}"
                )
            
            text = self.extractor.extract(file_path)
            
            if not text or not text.strip():
                return UploadResponse(
                    file_id=file_id,
                    filename=original_filename,
                    file_type=file_type,
                    chunk_count=0,
                    status="error",
                    message="No text could be extracted from the file"
                )
            
            # Step 2: Chunk the text
            text_chunks = self.chunker.chunk_text(text)
            
            if not text_chunks:
                return UploadResponse(
                    file_id=file_id,
                    filename=original_filename,
                    file_type=file_type,
                    chunk_count=0,
                    status="error",
                    message="Could not create text chunks from the document"
                )
            
            # Step 3: Generate embeddings
            chunk_texts = [chunk.text for chunk in text_chunks]
            embeddings = self.embedder.embed_texts(chunk_texts)
            
            # Step 4: Create document chunks with metadata
            doc_chunks = [
                DocumentChunk(
                    chunk_id=f"{file_id}_{chunk.chunk_id}",
                    file_id=file_id,
                    filename=original_filename,
                    text=chunk.text,
                    chunk_index=chunk.chunk_id
                )
                for chunk in text_chunks
            ]
            
            # Step 5: Store in vector database
            self.vector_store.add_documents(doc_chunks, embeddings)
            
            return UploadResponse(
                file_id=file_id,
                filename=original_filename,
                file_type=file_type,
                chunk_count=len(text_chunks),
                status="success",
                message=f"Successfully processed {len(text_chunks)} chunks"
            )
            
        except Exception as e:
            print(f"Error processing file: {e}")
            return UploadResponse(
                file_id=file_id,
                filename=original_filename,
                file_type=self.extractor.get_file_type(original_filename) or "unknown",
                chunk_count=0,
                status="error",
                message=str(e)
            )
    
    async def query(
        self,
        question: str,
        image_base64: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> QueryResponse:
        """
        Query the RAG system.
        
        Steps:
        1. OCR image if provided
        2. Perform vector search
        3. Build context
        4. Generate answer with Gemini
        """
        k = top_k or self.settings.top_k_results
        ocr_text = None
        
        try:
            # Step 1: OCR image if provided
            if image_base64:
                try:
                    ocr_text = self.extractor.extract_image_from_base64(image_base64)
                except Exception as e:
                    print(f"OCR error: {e}")
                    ocr_text = None
            
            # Step 2: Generate query embedding
            # Combine question with OCR text if available
            query_text = question
            if ocr_text:
                query_text = f"{question}\n\nAdditional context from image:\n{ocr_text}"
            
            query_embedding = self.embedder.embed_text(query_text)
            
            # Step 3: Vector search
            search_results = self.vector_store.search(query_embedding, top_k=k)
            
            # Step 4: Build context and sources
            context_chunks = []
            sources = []
            
            for result in search_results:
                context_chunks.append(result.chunk.text)
                sources.append(SourceMetadata(
                    file_id=result.chunk.file_id,
                    filename=result.chunk.filename,
                    chunk_id=result.chunk.chunk_index,
                    score=round(result.score, 4),
                    text_preview=result.chunk.text[:200] + "..." if len(result.chunk.text) > 200 else result.chunk.text
                ))
            
            # Step 5: Generate answer with Gemini
            if not self.gemini.is_configured():
                return QueryResponse(
                    answer="Error: Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file.",
                    sources=sources,
                    ocr_text=ocr_text
                )
            
            # Pass a placeholder if no context found
            if not context_chunks:
                context_for_gemini = "[NO DOCUMENTS UPLOADED OR NO RELEVANT CONTEXT FOUND]"
            else:
                context_for_gemini = context_chunks

            answer = self.gemini.generate_answer(
                question=question,
                context_chunks=context_for_gemini if isinstance(context_for_gemini, list) else [],
                additional_context=ocr_text if ocr_text else (context_for_gemini if isinstance(context_for_gemini, str) else None)
            )
            
            return QueryResponse(
                answer=answer,
                sources=sources,
                ocr_text=ocr_text
            )
            
        except Exception as e:
            print(f"Query error: {e}")
            return QueryResponse(
                answer=f"An error occurred while processing your query: {str(e)}",
                sources=[],
                ocr_text=ocr_text
            )
    
    def get_document_count(self) -> int:
        """Get the total number of document chunks in the store."""
        return self.vector_store.get_document_count()
    
    def delete_file(self, file_id: str) -> int:
        """Delete all chunks for a given file ID."""
        return self.vector_store.delete_by_file_id(file_id)
    
    def clear_all(self) -> None:
        """Clear all documents from the store."""
        self.vector_store.clear()


# Singleton instance
rag_pipeline = RAGPipeline()
