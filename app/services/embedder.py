"""
Embedding service using SentenceTransformers.
Generates embeddings locally without external API calls.
"""
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings


settings = get_settings()


class EmbeddingService:
    """Generate embeddings using SentenceTransformers."""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        self._model = None
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the model."""
        if self._model is None:
            print(f"Loading embedding model: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name)
            print(f"Embedding model loaded. Dimension: {self.embedding_dimension}")
        return self._model
    
    @property
    def embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.model.get_sentence_embedding_dimension()
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)
    
    def embed_texts(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for multiple texts."""
        if not texts:
            return np.array([])
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 10
        )
        return embeddings.astype(np.float32)
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings."""
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(embedding1, embedding2) / (norm1 * norm2))


# Singleton instance
embedding_service = EmbeddingService()
