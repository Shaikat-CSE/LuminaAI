"""
Pydantic schemas for API request/response models.
"""
from typing import Optional
from pydantic import BaseModel, Field


# ==================== Upload Schemas ====================

class UploadResponse(BaseModel):
    """Response model for file upload endpoint."""
    file_id: str = Field(..., description="Unique identifier for the uploaded file")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="Detected file type")
    chunk_count: int = Field(..., description="Number of chunks created")
    status: str = Field(..., description="Processing status")
    message: str = Field(default="", description="Additional status message")


class UploadURLRequest(BaseModel):
    """Request model for URL-based upload."""
    url: str = Field(..., description="URL to download and process")


# ==================== Query Schemas ====================

class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    question: str = Field(..., description="Question to answer")
    image_base64: Optional[str] = Field(
        default=None, 
        description="Optional base64-encoded image for OCR"
    )
    top_k: Optional[int] = Field(
        default=None, 
        description="Number of top results to retrieve"
    )


class SourceMetadata(BaseModel):
    """Metadata about a source chunk."""
    file_id: str = Field(..., description="Source file ID")
    filename: str = Field(..., description="Source filename")
    chunk_id: int = Field(..., description="Chunk index within the file")
    score: float = Field(..., description="Similarity score")
    text_preview: str = Field(..., description="Preview of the chunk text")


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    answer: str = Field(..., description="Generated answer")
    sources: list[SourceMetadata] = Field(
        default_factory=list, 
        description="Source document metadata"
    )
    ocr_text: Optional[str] = Field(
        default=None, 
        description="OCR text extracted from provided image"
    )


# ==================== Health Check ====================

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(default="healthy")
    version: str
    vector_store: str
    embedding_model: str
    document_count: int = Field(default=0)


# ==================== Error Schemas ====================

class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(..., description="Error message")
    error_type: str = Field(default="error", description="Type of error")
