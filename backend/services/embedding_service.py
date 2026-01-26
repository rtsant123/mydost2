"""Embedding service for text vectorization."""
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from utils.config import config


class EmbeddingService:
    """Service for generating text embeddings using SentenceTransformer."""
    
    def __init__(self):
        """Initialize embedding service with SentenceTransformer."""
        # Use SentenceTransformer for local embeddings (no API needed)
        # Options:
        # 'all-MiniLM-L6-v2' (384 dim) - Fast, good quality
        # 'all-mpnet-base-v2' (768 dim) - BEST quality, slower
        # 'paraphrase-multilingual-mpnet-base-v2' (768 dim) - BEST for multilingual
        self.model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')  # BEST for Hindi/Assamese/English
        self.dimension = 768
    
    async def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Convert text to embedding vector.
        
        Args:
            text: Text to embed
        
        Returns:
            List of floats representing the embedding
        """
        try:
            if not text or len(text.strip()) == 0:
                return None
            # Run blocking model.encode in a thread to avoid blocking the event loop
            import asyncio
            loop = asyncio.get_running_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: self.model.encode(text, convert_to_tensor=False)
            )
            return embedding.tolist() if embedding is not None else None
        
        except Exception as e:
            print(f"Error embedding text: {str(e)}")
            return None
    
    async def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[Optional[List[float]]]:
        """
        Convert multiple texts to embeddings.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process at once
        
        Returns:
            List of embeddings
        """
        try:
            import asyncio
            loop = asyncio.get_running_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self.model.encode(texts, convert_to_tensor=False, batch_size=batch_size)
            )
            return [emb.tolist() for emb in embeddings]
        
        except Exception as e:
            print(f"Error embedding texts: {str(e)}")
            return [None] * len(texts)
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
        
        Returns:
            Cosine similarity score (0-1)
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the embedding service."""
        return {
            "model": "paraphrase-multilingual-mpnet-base-v2",
            "dimension": self.dimension,
            "type": "SentenceTransformer",
        }


# Global embedding service instance
embedding_service = EmbeddingService()
