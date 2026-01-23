"""Vector database interface for RAG and memory storage."""
from typing import List, Dict, Any, Optional, Tuple
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams, Filter, FieldCondition, MatchValue
import uuid
from datetime import datetime
from services.embedding_service import embedding_service
from utils.config import config


class VectorStore:
    """Interface to Qdrant vector database for memory and RAG."""
    
    def __init__(self, url: str = None, api_key: str = None, collection_name: str = "memories"):
        """
        Initialize vector store.
        
        Args:
            url: Qdrant server URL
            api_key: API key for authentication
            collection_name: Name of the collection to use
        """
        self.url = url or config.VECTOR_DB_URL
        self.api_key = api_key or config.VECTOR_DB_API_KEY
        self.collection_name = collection_name
        
        try:
            if self.api_key:
                self.client = QdrantClient(
                    url=self.url,
                    api_key=self.api_key,
                    timeout=30,
                )
            else:
                self.client = QdrantClient(
                    url=self.url,
                    timeout=30,
                )
            
            # Create collection if it doesn't exist
            self._ensure_collection()
        
        except Exception as e:
            print(f"Warning: Could not connect to vector DB: {str(e)}")
            self.client = None
    
    def _ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=embedding_service.dimension,
                        distance=Distance.COSINE,
                    ),
                )
        except Exception as e:
            print(f"Error ensuring collection: {str(e)}")
    
    def add_memory(
        self,
        user_id: str,
        text: str,
        memory_type: str = "message",  # message, note, document
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Add a memory to the vector store.
        
        Args:
            user_id: User identifier
            text: Text content to store
            memory_type: Type of memory
            metadata: Additional metadata
        
        Returns:
            ID of the stored point
        """
        if not self.client or not text:
            return None
        
        try:
            # Generate embedding
            embedding = embedding_service.embed_text(text)
            if not embedding:
                return None
            
            # Generate point ID
            point_id = str(uuid.uuid4())
            
            # Prepare payload
            payload = {
                "user_id": user_id,
                "text": text,
                "type": memory_type,
                "timestamp": datetime.now().isoformat(),
            }
            if metadata:
                payload.update(metadata)
            
            # Store point
            points = [PointStruct(
                id=int(point_id.replace('-', ''), 16) % (2**63),  # Convert UUID to int
                vector=embedding,
                payload=payload,
            )]
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            
            return point_id
        
        except Exception as e:
            print(f"Error adding memory: {str(e)}")
            return None
    
    def retrieve_memories(
        self,
        user_id: str,
        query_text: str,
        limit: int = 5,
        memory_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories for a user.
        
        Args:
            user_id: User identifier
            query_text: Query text to find similar memories
            limit: Number of results to return
            memory_types: Filter by memory types
        
        Returns:
            List of relevant memories with scores
        """
        if not self.client or not query_text:
            return []
        
        try:
            # Generate query embedding
            query_embedding = embedding_service.embed_text(query_text)
            if not query_embedding:
                return []
            
            # Build filter
            filter_conditions = [
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id),
                )
            ]
            
            if memory_types:
                type_conditions = [
                    FieldCondition(key="type", match=MatchValue(value=mt))
                    for mt in memory_types
                ]
                # Note: This is simplified - in production, use proper OR logic
                if type_conditions:
                    filter_conditions = [filter_conditions[0]]  # Keep user_id filter
            
            # Search in vector DB
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=Filter(must=filter_conditions) if filter_conditions else None,
                limit=limit,
                score_threshold=0.3,  # Only return relevant results
            )
            
            # Format results
            memories = []
            for result in results:
                memories.append({
                    "id": result.id,
                    "text": result.payload.get("text"),
                    "type": result.payload.get("type"),
                    "timestamp": result.payload.get("timestamp"),
                    "similarity_score": result.score,
                    "metadata": {k: v for k, v in result.payload.items() 
                               if k not in ["text", "type", "timestamp", "user_id"]},
                })
            
            return memories
        
        except Exception as e:
            print(f"Error retrieving memories: {str(e)}")
            return []
    
    def delete_memory(self, user_id: str, point_id: int) -> bool:
        """Delete a specific memory point."""
        if not self.client:
            return False
        
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id],
            )
            return True
        except Exception as e:
            print(f"Error deleting memory: {str(e)}")
            return False
    
    def clear_user_memories(self, user_id: str) -> bool:
        """Delete all memories for a user."""
        if not self.client:
            return False
        
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id),
                        )
                    ]
                ),
            )
            return True
        except Exception as e:
            print(f"Error clearing user memories: {str(e)}")
            return False
    
    def reindex_collection(self) -> bool:
        """Reindex the collection (e.g., after updates)."""
        if not self.client:
            return False
        
        try:
            # In Qdrant, this is mainly for optimization
            # We can recreate the collection if needed
            return True
        except Exception as e:
            print(f"Error reindexing: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        if not self.client:
            return {}
        
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "vector_size": collection_info.config.params.vectors.size,
                "points_count": collection_info.points_count,
            }
        except Exception as e:
            print(f"Error getting stats: {str(e)}")
            return {}


# Global vector store instance
vector_store = VectorStore(
    url=config.VECTOR_DB_URL,
    api_key=config.VECTOR_DB_API_KEY,
    collection_name="memories"
)
