"""
Vector store service supporting FAISS and ChromaDB.
Handles storage, retrieval, and search of document embeddings.
"""
import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import numpy as np
import faiss

from app.core.config import get_settings
from app.services.embedder import embedding_service


settings = get_settings()


@dataclass
class DocumentChunk:
    """Represents a stored document chunk with metadata."""
    chunk_id: str
    file_id: str
    filename: str
    text: str
    chunk_index: int
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "DocumentChunk":
        return cls(**data)


@dataclass
class SearchResult:
    """Search result with score and metadata."""
    chunk: DocumentChunk
    score: float


class BaseVectorStore(ABC):
    """Abstract base class for vector stores."""
    
    @abstractmethod
    def add_documents(self, chunks: list[DocumentChunk], embeddings: np.ndarray) -> None:
        """Add documents with their embeddings to the store."""
        pass
    
    @abstractmethod
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[SearchResult]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    def delete_by_file_id(self, file_id: str) -> int:
        """Delete all chunks for a given file ID."""
        pass
    
    @abstractmethod
    def get_document_count(self) -> int:
        """Get total number of documents in the store."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all documents from the store."""
        pass


class FAISSVectorStore(BaseVectorStore):
    """FAISS-based vector store implementation."""
    
    def __init__(self, index_dir: Path = None):
        self.index_dir = index_dir or settings.faiss_index_dir
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_path = self.index_dir / "index.faiss"
        self.metadata_path = self.index_dir / "metadata.json"
        
        self.dimension = embedding_service.embedding_dimension
        self.index: Optional[faiss.IndexFlatIP] = None
        self.metadata: list[DocumentChunk] = []
        
        self._load_or_create()
    
    def _load_or_create(self) -> None:
        """Load existing index or create new one."""
        if self.index_path.exists() and self.metadata_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    metadata_list = json.load(f)
                    self.metadata = [DocumentChunk.from_dict(m) for m in metadata_list]
                print(f"Loaded FAISS index with {len(self.metadata)} documents")
            except Exception as e:
                print(f"Error loading FAISS index: {e}, creating new...")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self) -> None:
        """Create a new FAISS index."""
        # Using Inner Product (cosine similarity after normalization)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        print(f"Created new FAISS index with dimension {self.dimension}")
    
    def _save(self) -> None:
        """Save index and metadata to disk."""
        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump([m.to_dict() for m in self.metadata], f, ensure_ascii=False, indent=2)
    
    def _normalize(self, embeddings: np.ndarray) -> np.ndarray:
        """L2 normalize embeddings for cosine similarity."""
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)  # Avoid division by zero
        return embeddings / norms
    
    def add_documents(self, chunks: list[DocumentChunk], embeddings: np.ndarray) -> None:
        """Add documents with their embeddings."""
        if len(chunks) == 0:
            return
        
        # Normalize embeddings for cosine similarity
        normalized = self._normalize(embeddings)
        
        # Add to index
        self.index.add(normalized)
        self.metadata.extend(chunks)
        
        # Save to disk
        self._save()
        print(f"Added {len(chunks)} documents to FAISS index")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[SearchResult]:
        """Search for similar documents."""
        if self.index.ntotal == 0:
            return []
        
        # Normalize query
        query_normalized = self._normalize(query_embedding.reshape(1, -1))
        
        # Search
        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_normalized, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.metadata):
                results.append(SearchResult(
                    chunk=self.metadata[idx],
                    score=float(score)
                ))
        
        return results
    
    def delete_by_file_id(self, file_id: str) -> int:
        """Delete all chunks for a given file ID (requires rebuilding index)."""
        # Find indices to keep
        keep_indices = [i for i, m in enumerate(self.metadata) if m.file_id != file_id]
        deleted_count = len(self.metadata) - len(keep_indices)
        
        if deleted_count == 0:
            return 0
        
        # Rebuild index with remaining documents
        if keep_indices:
            # Get embeddings to keep
            all_embeddings = faiss.rev_swig_ptr(
                self.index.get_xb(), self.index.ntotal * self.dimension
            ).reshape(self.index.ntotal, self.dimension).copy()
            
            keep_embeddings = all_embeddings[keep_indices]
            keep_metadata = [self.metadata[i] for i in keep_indices]
            
            # Create new index
            self._create_new_index()
            self.index.add(keep_embeddings)
            self.metadata = keep_metadata
        else:
            self._create_new_index()
        
        self._save()
        return deleted_count
    
    def get_document_count(self) -> int:
        """Get total number of documents."""
        return len(self.metadata)
    
    def clear(self) -> None:
        """Clear all documents."""
        self._create_new_index()
        self._save()


class ChromaVectorStore(BaseVectorStore):
    """ChromaDB-based vector store implementation."""
    
    def __init__(self, persist_dir: Path = None):
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        
        self.persist_dir = persist_dir or settings.chroma_db_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="rag_documents",
            metadata={"hnsw:space": "cosine"}
        )
        print(f"ChromaDB initialized with {self.collection.count()} documents")
    
    def add_documents(self, chunks: list[DocumentChunk], embeddings: np.ndarray) -> None:
        """Add documents with their embeddings."""
        if len(chunks) == 0:
            return
        
        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [
            {
                "file_id": chunk.file_id,
                "filename": chunk.filename,
                "chunk_index": chunk.chunk_index
            }
            for chunk in chunks
        ]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas
        )
        print(f"Added {len(chunks)} documents to ChromaDB")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[SearchResult]:
        """Search for similar documents."""
        if self.collection.count() == 0:
            return []
        
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"]
        )
        
        search_results = []
        if results['ids'] and results['ids'][0]:
            for i, chunk_id in enumerate(results['ids'][0]):
                metadata = results['metadatas'][0][i]
                # ChromaDB returns distance, convert to similarity
                distance = results['distances'][0][i]
                score = 1 - distance  # For cosine distance
                
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    file_id=metadata['file_id'],
                    filename=metadata['filename'],
                    text=results['documents'][0][i],
                    chunk_index=metadata['chunk_index']
                )
                search_results.append(SearchResult(chunk=chunk, score=score))
        
        return search_results
    
    def delete_by_file_id(self, file_id: str) -> int:
        """Delete all chunks for a given file ID."""
        # Get all chunks with this file_id
        results = self.collection.get(
            where={"file_id": file_id},
            include=[]
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            return len(results['ids'])
        return 0
    
    def get_document_count(self) -> int:
        """Get total number of documents."""
        return self.collection.count()
    
    def clear(self) -> None:
        """Clear all documents."""
        # Delete and recreate collection
        self.client.delete_collection("rag_documents")
        self.collection = self.client.get_or_create_collection(
            name="rag_documents",
            metadata={"hnsw:space": "cosine"}
        )


def get_vector_store() -> BaseVectorStore:
    """Factory function to get the configured vector store."""
    if settings.vector_store_type.lower() == "chroma":
        return ChromaVectorStore()
    else:
        return FAISSVectorStore()


# Singleton instance
vector_store = get_vector_store()
