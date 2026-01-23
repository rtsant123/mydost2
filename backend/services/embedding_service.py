"""Embedding service for text vectorization."""
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import openai
from utils.config import config


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self, model_choice: str = "sentence-transformer"):
        """
        Initialize embedding service.
        
        Args:
            model_choice: 'sentence-transformer' or 'openai'
        """
        self.model_choice = model_choice
        
        if model_choice == "sentence-transformer":
            # Use SentenceTransformer for local embeddings
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.dimension = 384
        elif model_choice == "openai":
            # Use OpenAI embeddings
            openai.api_key = config.OPENAI_API_KEY
            self.model = None
            self.dimension = 1536  # text-embedding-3-small
        else:
            raise ValueError(f"Unknown model choice: {model_choice}")
    
    def embed_text(self, text: str) -> Optional[List[float]]:
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
            
            if self.model_choice == "sentence-transformer":
                embedding = self.model.encode(text, convert_to_tensor=False)
                return embedding.tolist()
            
            elif self.model_choice == "openai":
                response = openai.Embedding.create(
                    input=text,
                    model="text-embedding-3-small"
                )
                return response['data'][0]['embedding']
        
        except Exception as e:
            print(f"Error embedding text: {str(e)}")
            return None
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[Optional[List[float]]]:
        """
        Convert multiple texts to embeddings.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process at once
        
        Returns:
            List of embeddings
        """
        try:
            if self.model_choice == "sentence-transformer":
                embeddings = self.model.encode(texts, convert_to_tensor=False, batch_size=batch_size)
                return [emb.tolist() for emb in embeddings]
            
            elif self.model_choice == "openai":
                # OpenAI API has batch limits, so we need to chunk
                embeddings = []
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i+batch_size]
                    response = openai.Embedding.create(
                        input=batch,
                        model="text-embedding-3-small"
                    )
                    for data in response['data']:
                        embeddings.append(data['embedding'])
                return embeddings
        
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
            "model_choice": self.model_choice,
            "dimension": self.dimension,
            "model_name": "all-MiniLM-L6-v2" if self.model_choice == "sentence-transformer" else "text-embedding-3-small",
        }


# Global embedding service instance
embedding_service = EmbeddingService(model_choice="sentence-transformer")
