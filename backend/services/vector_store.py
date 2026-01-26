"""PostgreSQL vector store service using pgvector extension."""
import os
import json
from typing import List, Dict, Optional, Any
import psycopg2
from psycopg2 import errors
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
                self.conn.autocommit = True  # avoid aborted transaction state
                # Try to enable pgvector extension first
                try:
                    with self.conn.cursor() as cur:
                        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
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
            
            # Create user profiles table to track preferences over time
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) UNIQUE NOT NULL,
                    preferences JSONB DEFAULT '{}',
                    interests JSONB DEFAULT '[]',
                    conversation_count INTEGER DEFAULT 0,
                    total_messages INTEGER DEFAULT 0,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'
                );
            """)
            
            # Create index for user_id lookup
            cur.execute("""
                CREATE INDEX IF NOT EXISTS user_profiles_user_idx 
                ON user_profiles(user_id);
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
            else:
                print(f"Warning: Database interface error during table creation: {e}")
        except Exception as e:
            print(f"Warning: Could not create tables (may already exist): {e}")

    def _ensure_tables_exist(self):
        """Best-effort ensure tables exist when operations fail."""
        try:
            self._create_tables()
        except Exception as e:
            print(f"Schema ensure failed: {e}")
    
    def add_memory(
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
                return True
        
        except Exception as e:
            print(f"Error adding memory: {e}")
            # If table missing, try to create and retry once
            if isinstance(e, errors.UndefinedTable):
                self._ensure_tables_exist()
                try:
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
                    return True
                except Exception as e2:
                    print(f"Retry add_memory failed: {e2}")
            return False
    
    def search_similar(
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
            if isinstance(e, errors.UndefinedTable):
                self._ensure_tables_exist()
                return self.search_similar(user_id, query_embedding, limit, similarity_threshold, memory_type)
            return []
    
    def add_pdf_content(
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
    
    def search_pdf_content(
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
            if isinstance(e, errors.UndefinedTable):
                self._ensure_tables_exist()
                return self.search_pdf_content(user_id, query_embedding, limit)
            return []
    
    def get_conversation_history(
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
    
    def delete_user_data(self, user_id: str) -> bool:
        """Delete all data for a specific user."""
        try:
            self._ensure_connection()
            
            with self.conn.cursor() as cur:
                # Delete all vectors for this user
                cur.execute("DELETE FROM chat_vectors WHERE user_id = %s", (user_id,))
                # Delete user profile
                cur.execute("DELETE FROM user_profiles WHERE user_id = %s", (user_id,))
                self.conn.commit()
            
            return True
        except Exception as e:
            print(f"Error deleting user data: {e}")
            try:
                self.conn.rollback()
            except:
                pass
            return False
    
    def update_user_profile(
        self,
        user_id: str,
        preferences: Optional[Dict] = None,
        interests: Optional[List[str]] = None,
        increment_messages: bool = True
    ) -> bool:
        """
        Update or create user profile with learned preferences.
        
        Args:
            user_id: User identifier
            preferences: Dict of preferences like {"favorite_sport": "cricket", "language": "hindi"}
            interests: List of detected interests like ["cricket", "technology", "movies"]
            increment_messages: Whether to increment message count
        """
        try:
            self._ensure_connection()
            
            with self.conn.cursor() as cur:
                # Check if profile exists
                cur.execute("SELECT id FROM user_profiles WHERE user_id = %s", (user_id,))
                exists = cur.fetchone()
                
                if exists:
                    # Update existing profile
                    updates = ["last_active = CURRENT_TIMESTAMP"]
                    params = []
                    
                    if preferences:
                        # Merge new preferences with existing ones
                        updates.append("preferences = preferences || %s::jsonb")
                        params.append(json.dumps(preferences))
                    
                    if interests:
                        # Add new interests (avoiding duplicates)
                        updates.append("""
                            interests = (
                                SELECT jsonb_agg(DISTINCT value)
                                FROM jsonb_array_elements(interests || %s::jsonb)
                            )
                        """)
                        params.append(json.dumps(interests))
                    
                    if increment_messages:
                        updates.append("total_messages = total_messages + 1")
                    
                    params.append(user_id)
                    query = f"UPDATE user_profiles SET {', '.join(updates)} WHERE user_id = %s"
                    cur.execute(query, params)
                else:
                    # Create new profile
                    cur.execute("""
                        INSERT INTO user_profiles 
                        (user_id, preferences, interests, total_messages, conversation_count)
                        VALUES (%s, %s, %s, 1, 1)
                    """, (
                        user_id,
                        json.dumps(preferences or {}),
                        json.dumps(interests or [])
                    ))
                
                self.conn.commit()
                return True
        
        except Exception as e:
            print(f"Error updating user profile: {e}")
            try:
                self.conn.rollback()
            except:
                pass
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile with all learned preferences and interests."""
        try:
            self._ensure_connection()
            
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        user_id,
                        preferences,
                        interests,
                        conversation_count,
                        total_messages,
                        first_seen,
                        last_active,
                        metadata
                    FROM user_profiles
                    WHERE user_id = %s
                """, (user_id,))
                
                result = cur.fetchone()
                return dict(result) if result else None
        
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return None

    def delete_user_data(self, user_id: str) -> bool:
        """Delete all data for a specific user (vectors, PDFs, profiles)."""
        try:
            self._ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM chat_vectors WHERE user_id = %s", (user_id,))
                cur.execute("DELETE FROM pdf_documents WHERE user_id = %s", (user_id,))
                cur.execute("DELETE FROM user_profiles WHERE user_id = %s", (user_id,))
            return True
        except Exception as e:
            print(f"Error deleting user data: {e}")
            if isinstance(e, errors.UndefinedTable):
                self._ensure_tables_exist()
            return False
    
    def close(self):
        """Close database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()


# Global vector store instance
vector_store = VectorStoreService()
