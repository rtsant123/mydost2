"""User database models and operations."""
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
from utils.config import config


class UserDatabase:
    """Database operations for user management."""
    
    def __init__(self):
        self.connection_string = config.DATABASE_URL
        self._ensure_tables()
    
    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(self.connection_string)
    
    def _ensure_tables(self):
        """Create users and usage_limits tables if they don't exist."""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id UUID PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    image TEXT,
                    google_id VARCHAR(255) UNIQUE NOT NULL,
                    preferences JSONB DEFAULT '{}',
                    has_preferences BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create usage_limits table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_limits (
                    id SERIAL PRIMARY KEY,
                    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
                    date DATE DEFAULT CURRENT_DATE,
                    api_calls INTEGER DEFAULT 0,
                    tokens_used INTEGER DEFAULT 0,
                    web_searches INTEGER DEFAULT 0,
                    ocr_requests INTEGER DEFAULT 0,
                    pdf_uploads INTEGER DEFAULT 0,
                    UNIQUE(user_id, date)
                );
            """)
            
            # Create index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_usage_limits_user_date 
                ON usage_limits(user_id, date);
            """)
            
            conn.commit()
            print("User database tables initialized successfully")
        except Exception as e:
            print(f"Error creating user tables: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def create_or_get_user(self, email: str, name: str, google_id: str, image: Optional[str] = None) -> Dict[str, Any]:
        """Create new user or get existing user."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Check if user exists
            cursor.execute(
                "SELECT * FROM users WHERE email = %s OR google_id = %s",
                (email, google_id)
            )
            user = cursor.fetchone()
            
            if user:
                # Update last login
                cursor.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = %s",
                    (user['user_id'],)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return dict(user)
            else:
                # Create new user
                import uuid
                user_id = str(uuid.uuid4())
                
                cursor.execute("""
                    INSERT INTO users (user_id, email, name, google_id, image)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                """, (user_id, email, name, google_id, image))
                
                new_user = cursor.fetchone()
                conn.commit()
                cursor.close()
                conn.close()
                return dict(new_user)
        
        except Exception as e:
            print(f"Error creating/getting user: {str(e)}")
            raise
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return dict(user) if user else None
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None
    
    def save_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Save user preferences."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET preferences = %s, has_preferences = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """, (json.dumps(preferences), user_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving preferences: {str(e)}")
            return False
    
    def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT preferences, has_preferences FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result:
                return {
                    "preferences": result['preferences'] or {},
                    "has_preferences": result['has_preferences']
                }
            return {"preferences": {}, "has_preferences": False}
        except Exception as e:
            print(f"Error getting preferences: {str(e)}")
            return {"preferences": {}, "has_preferences": False}
    
    def increment_usage(self, user_id: str, api_calls: int = 0, tokens: int = 0, 
                       web_searches: int = 0, ocr_requests: int = 0, pdf_uploads: int = 0) -> bool:
        """Increment usage counters for user."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Insert or update today's usage
            cursor.execute("""
                INSERT INTO usage_limits (user_id, api_calls, tokens_used, web_searches, ocr_requests, pdf_uploads)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, date)
                DO UPDATE SET
                    api_calls = usage_limits.api_calls + EXCLUDED.api_calls,
                    tokens_used = usage_limits.tokens_used + EXCLUDED.tokens_used,
                    web_searches = usage_limits.web_searches + EXCLUDED.web_searches,
                    ocr_requests = usage_limits.ocr_requests + EXCLUDED.ocr_requests,
                    pdf_uploads = usage_limits.pdf_uploads + EXCLUDED.pdf_uploads
            """, (user_id, api_calls, tokens, web_searches, ocr_requests, pdf_uploads))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error incrementing usage: {str(e)}")
            return False
    
    def get_today_usage(self, user_id: str) -> Dict[str, int]:
        """Get today's usage for user."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT api_calls, tokens_used, web_searches, ocr_requests, pdf_uploads
                FROM usage_limits
                WHERE user_id = %s AND date = CURRENT_DATE
            """, (user_id,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return dict(result)
            return {
                "api_calls": 0,
                "tokens_used": 0,
                "web_searches": 0,
                "ocr_requests": 0,
                "pdf_uploads": 0
            }
        except Exception as e:
            print(f"Error getting usage: {str(e)}")
            return {
                "api_calls": 0,
                "tokens_used": 0,
                "web_searches": 0,
                "ocr_requests": 0,
                "pdf_uploads": 0
            }
    
    def check_limit(self, user_id: str, limit_type: str, max_limit: int) -> bool:
        """Check if user has exceeded limit for today."""
        usage = self.get_today_usage(user_id)
        current = usage.get(limit_type, 0)
        return current < max_limit
    
    def get_user_stats(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get user statistics for last N days."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    SUM(api_calls) as total_api_calls,
                    SUM(tokens_used) as total_tokens,
                    SUM(web_searches) as total_searches,
                    SUM(ocr_requests) as total_ocr,
                    SUM(pdf_uploads) as total_pdfs
                FROM usage_limits
                WHERE user_id = %s AND date >= CURRENT_DATE - INTERVAL '%s days'
            """, (user_id, days))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return dict(result) if result else {}
        except Exception as e:
            print(f"Error getting stats: {str(e)}")
            return {}


# Global instance
user_db = UserDatabase()
