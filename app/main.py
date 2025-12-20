"""
LuminaAI API - Main Application Entry Point

A FastAPI-based LuminaAI API that uses local document processing
and Gemini for answer generation.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.api.routes import router


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    print(f"\n{'='*50}")
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"{'='*50}")
    print(f"Vector Store: {settings.vector_store_type}")
    print(f"Embedding Model: {settings.embedding_model}")
    print(f"Chunk Size: {settings.chunk_size} tokens")
    print(f"Chunk Overlap: {settings.chunk_overlap} tokens")
    print(f"{'='*50}\n")
    
    yield
    
    # Shutdown
    print(f"\n{'='*50}")
    print(f"👋 Shutting down {settings.app_name}")
    print(f"{'='*50}\n")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## LuminaAI API

A Retrieval-Augmented Generation API (LuminaAI) for document-based question answering.

### Features:
- **Document Upload**: Support for PDF, DOCX, TXT, Images (JPG/PNG), CSV, and SQLite files
- **Local Processing**: Text extraction, chunking, and embedding are done locally
- **Vector Search**: FAISS or ChromaDB for fast similarity search
- **Gemini Integration**: Final answer generation using Google Gemini
- **OCR Support**: Automatic OCR for scanned documents and images

### Workflow:
1. Upload documents via `/upload` endpoint
2. Query documents via `/query` endpoint
3. Receive AI-generated answers with source references
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["LuminaAI API"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "error_type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
