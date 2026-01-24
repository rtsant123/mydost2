"""PostgreSQL vector store service using pgvector extension."""
import os
import json
from typing import List, Dict, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from pgvector.psycopg2 import register_vector
from datetime import datetime


class VectorStoreService:
    """PostgreSQL + pgvector for vector storage and semantic search."""
    
    def __init__(self):
        self.connection_string = os.getenv(
            "DATABASE_URL",
            "postgresql://user:password@localhost:5432/chatbot_db"
        )
        self.conn = None
        self._ensure_connection()
    
    def _ensure_connection(self):
        """Ensure database connection is active."""
        try:
            if not self.conn or self.conn.closed:
                self.conn = psycopg2.connect(self.connection_string)
                # Try to enable pgvector extension first
                try:
                    with self.conn.cursor() as cur:
                        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                        self.conn.commit()
                    # Now register vector type
                    register_vector(self.conn)
                except Exception as e:
                    print(f"Warning: Could not enable pgvector: {e}")
                    print("Vector operations will be disabled. Enable pgvector extension manually.")
                    # Don't fail - continue without vector support
                self._create_tables()
        except Exception as e:
            print(f"Database connection error: {e}")
            # Don't raise - allow app to start without vector DB
            self.conn = None
    
    def _create_tables(self):
        """Create required tables with pgvector extension."""
        if not self.conn:
            return
        try:
            with self.conn.cursor() as cur:
                # Enable pgvector extension (if not already done)
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                
                # Create vectors table for RAG memory
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chat_vectors (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        conversation_id VARCHAR(255),
                        content TEXT NOT NULL,
                        embedding vector(768),
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        type VARCHAR(50) DEFAULT 'conversation'
                    );
                """)
            
            # Create index for vector similarity search
            cur.execute("""
                CREATE INDEX IF NOT EXISTS chat_vectors_embedding_idx 
                ON chat_vectors USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """)
            
            # Create index for user_id filtering
            cur.execute("""
                CREATE INDEX IF NOT EXISTS chat_vectors_user_idx 
                ON chat_vectors(user_id);
            """)
            
            # Create table for PDF documents
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pdf_documents (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    filename VARCHAR(500) NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector(768),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create index for PDF vectors
            cur.execute("""
                CREATE INDEX IF NOT EXISTS pdf_documents_embedding_idx 
                ON pdf_documents USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """)
            
            self.conn.commit()
        except psycopg2.InterfaceError as e:
            # Handle cursor/connection closed errors gracefully
            if "cursor already closed" in str(e).lower() or "connection closed" in str(e).lower():
                print(f"Info: Database connection closed during table creation (likely tables already exist)")
                try:
                    self.conn.rollback()
                except:
                    pass
            else:
                print(f"Warning: Database interface error during table creation: {e}")
                try:
                    self.conn.rollback()
                except:
                    pass
        except Exception as e:
            print(f"Warning: Could not create tables (may already exist): {e}")
            try:
                self.conn.rollback()
            except:
                pass
    
    async def add_memory(
        self,
        user_id: str,
        content: str,
        embedding: List[float],
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        memory_type: str = "conversation"
    ) -> bool:
        """
        Add a memory/vector to the database.
        
        Args:
            user_id: User identifier
            content: Text content
            embedding: Vector embedding (384-dim for all-MiniLM-L6-v2)
            conversation_id: Optional conversation ID
            metadata: Optional metadata dict
            memory_type: Type of memory (conversation, pdf, note, etc.)
        
        Returns:
            Success boolean
        """
        if not self.conn:
            print("Database not connected, skipping memory storage")
            return False
        
        try:
            self._ensure_connection()
            
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO chat_vectors 
                    (user_id, conversation_id, content, embedding, metadata, type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    user_id,
                    conversation_id,
                    content,
                    embedding,
                    json.dumps(metadata) if metadata else None,
                    memory_type
                ))
                self.conn.commit()
                return True
        
        except Exception as e:
            print(f"Error adding memory: {e}")
            self.conn.rollback()
            return False
    
    async def search_similar(
        self,
        user_id: str,
        query_embedding: List[float],
        limit: int = 5,
        similarity_threshold: float = 0.7,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors using cosine similarity.
        
        Args:
            user_id: User identifier to filter results
            query_embedding: Query vector
            limit: Max number of results
            similarity_threshold: Minimum similarity score (0-1)
            memory_type: Optional filter by memory type
        
        Returns:
            List of similar memory dicts with content and similarity scores
        """
        try:
            self._ensure_connection()
            
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                if memory_type:
                    cur.execute("""
                        SELECT 
                            id,
                            user_id,
                            conversation_id,
                            content,
                            metadata,
                            type,
                            created_at,
                            1 - (embedding <=> %s::vector) as similarity
                        FROM chat_vectors
                        WHERE user_id = %s 
                        AND type = %s
                        AND (1 - (embedding <=> %s::vector)) >= %s
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """, (query_embedding, user_id, memory_type, query_embedding, similarity_threshold, query_embedding, limit))
                else:
                    cur.execute("""
                        SELECT 
                            id,
                            user_id,
                            conversation_id,
                            content,
                            metadata,
                            type,
                            created_at,
                            1 - (embedding <=> %s::vector) as similarity
                        FROM chat_vectors
                        WHERE user_id = %s 
                        AND (1 - (embedding <=> %s::vector)) >= %s
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """, (query_embedding, user_id, query_embedding, similarity_threshold, query_embedding, limit))
                
                results = cur.fetchall()
                return [dict(row) for row in results]
        
        except Exception as e:
            print(f"Error searching vectors: {e}")
            return []
    
    async def add_pdf_content(
        self,
        user_id: str,
        filename: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict] = None
    ) -> bool:
        """Add PDF content to vector database."""
        try:
            self._ensure_connection()
            
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO pdf_documents 
                    (user_id, filename, content, embedding, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    user_id,
                    filename,
                    content,
                    embedding,
                    json.dumps(metadata) if metadata else None
                ))
                self.conn.commit()
                return True
        
        except Exception as e:
            print(f"Error adding PDF content: {e}")
            self.conn.rollback()
            return False
    
    async def search_pdf_content(
        self,
        user_id: str,
        query_embedding: List[float],
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Search PDF documents for similar content."""
        try:
            self._ensure_connection()
            
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        id,
                        filename,
                        content,
                        metadata,
                        1 - (embedding <=> %s::vector) as similarity
                    FROM pdf_documents
                    WHERE user_id = %s
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (query_embedding, user_id, query_embedding, limit))
                
                results = cur.fetchall()
                return [dict(row) for row in results]
        
        except Exception as e:
            print(f"Error searching PDF content: {e}")
            return []
    
    async def get_conversation_history(
        self,
        user_id: str,
        conversation_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a specific conversation."""
        try:
            self._ensure_connection()
            
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT content, metadata, created_at
                    FROM chat_vectors
                    WHERE user_id = %s 
                    AND conversation_id = %s
                    AND type = 'conversation'
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (user_id, conversation_id, limit))
                
                results = cur.fetchall()
                return [dict(row) for row in reversed(results)]
        
        except Exception as e:
            print(f"Error fetching conversation history: {e}")
            return []
    
    async def delete_user_data(self, user_id: str) -> bool:
        """Delete all data for a specific user."""
        try:
            self._ensure_connection()
            
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM chat_vectors WHERE user_id = %s", (user_id,))
                cur.execute("DELETE FROM pdf_documents WHERE user_id = %s", (user_id,))
                self.conn.commit()
                return True
        
        except Exception as e:
            print(f"Error deleting user data: {e}")
            self.conn.rollback()
            return False
    
    def close(self):
        """Close database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()


# Global vector store instance
vector_store = VectorStoreService()
