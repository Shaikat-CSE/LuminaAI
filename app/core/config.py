"""
Application configuration using Pydantic Settings.
"""
import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    app_name: str = "LuminaAI API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Gemini API
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3-flash-preview"
    
    # Vector Store
    vector_store_type: str = "faiss"  # "faiss" or "chroma"
    
    # Embedding Model
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Chunking Configuration
    chunk_size: int = 500
    chunk_overlap: int = 75
    
    # Search Configuration
    top_k_results: int = 5
    
    # Tesseract Path (for Windows)
    tesseract_path: str | None = None
    
    # Data directories
    @property
    def base_dir(self) -> Path:
        return Path(__file__).parent.parent.parent
    
    @property
    def data_dir(self) -> Path:
        return self.base_dir / "data"
    
    @property
    def upload_dir(self) -> Path:
        return self.data_dir / "uploads"
    
    @property
    def faiss_index_dir(self) -> Path:
        return self.data_dir / "faiss_index"
    
    @property
    def chroma_db_dir(self) -> Path:
        return self.data_dir / "chroma_db"
    
    def setup_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.faiss_index_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_db_dir.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.setup_directories()
    return settings
