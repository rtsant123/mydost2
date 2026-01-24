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
                    password_hash VARCHAR(255),
                    image TEXT,
                    google_id VARCHAR(255) UNIQUE,
                    auth_provider VARCHAR(50) DEFAULT 'email',
                    preferences JSONB DEFAULT '{}',
                    has_preferences BOOLEAN DEFAULT FALSE,
                    referred_by VARCHAR(255),
                    referral_code VARCHAR(50) UNIQUE,
                    subscription_tier VARCHAR(50) DEFAULT 'free',
                    subscription_status VARCHAR(50) DEFAULT 'active',
                    subscription_expires_at TIMESTAMP,
                    razorpay_subscription_id VARCHAR(255),
                    messages_lifetime INTEGER DEFAULT 0,
                    messages_today INTEGER DEFAULT 0,
                    daily_reset_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create guest tracking table for free limits
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS guest_usage (
                    id SERIAL PRIMARY KEY,
                    fingerprint VARCHAR(64) UNIQUE NOT NULL,
                    ip_address VARCHAR(45) NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    first_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    def create_user_with_password(self, email: str, name: str, password: str, referred_by: Optional[str] = None) -> Dict[str, Any]:
        """Create user with email/password."""
        import uuid
        import bcrypt
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Generate referral code
            referral_code = str(uuid.uuid4())[:8].upper()
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create user
            user_id = uuid.uuid4()
            cursor.execute("""
                INSERT INTO users (user_id, email, name, password_hash, auth_provider, referred_by, referral_code)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (user_id, email, name, password_hash, 'email', referred_by, referral_code))
            
            user = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            return dict(user)
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return None
    
    def verify_password(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify email/password and return user."""
        import bcrypt
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT * FROM users WHERE email = %s AND auth_provider = 'email'", (email,))
            user = cursor.fetchone()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                # Update last login
                cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = %s", (user['user_id'],))
                conn.commit()
                cursor.close()
                conn.close()
                return dict(user)
            
            cursor.close()
            conn.close()
            return None
        except Exception as e:
            print(f"Error verifying password: {str(e)}")
            return None
    
    def track_guest_usage(self, fingerprint: str, ip_address: str) -> Dict[str, Any]:
        """Track guest user message count for free limit."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Check existing
            cursor.execute("SELECT * FROM guest_usage WHERE fingerprint = %s", (fingerprint,))
            guest = cursor.fetchone()
            
            if guest:
                # Increment count
                cursor.execute("""
                    UPDATE guest_usage 
                    SET message_count = message_count + 1, last_message_at = CURRENT_TIMESTAMP
                    WHERE fingerprint = %s
                    RETURNING *
                """, (fingerprint,))
            else:
                # Create new
                cursor.execute("""
                    INSERT INTO guest_usage (fingerprint, ip_address, message_count)
                    VALUES (%s, %s, 1)
                    RETURNING *
                """, (fingerprint, ip_address))
            
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            return dict(result)
        except Exception as e:
            print(f"Error tracking guest: {str(e)}")
            return {"message_count": 0}
    
    def get_guest_usage(self, fingerprint: str) -> int:
        """Get guest message count."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT message_count FROM guest_usage WHERE fingerprint = %s", (fingerprint,))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return result['message_count'] if result else 0
        except Exception as e:
            print(f"Error getting guest usage: {str(e)}")
            return 0
    
    def check_and_increment_message(self, user_id: str) -> Dict[str, Any]:
        """Check limits and increment message count. Returns status and remaining."""
        from datetime import datetime, timedelta
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                conn.close()
                return {"allowed": False, "error": "User not found"}
            
            tier = user.get('subscription_tier', 'free')
            messages_lifetime = user.get('messages_lifetime', 0)
            messages_today = user.get('messages_today', 0)
            daily_reset_at = user.get('daily_reset_at')
            
            # Check if daily reset needed
            now = datetime.now()
            if daily_reset_at and now >= daily_reset_at:
                messages_today = 0
                daily_reset_at = now + timedelta(days=1)
                cursor.execute("""
                    UPDATE users 
                    SET messages_today = 0, daily_reset_at = %s 
                    WHERE user_id = %s
                """, (daily_reset_at, user_id))
                conn.commit()
            
            from utils.config import config
            plan = config.SUBSCRIPTION_PLANS.get(tier, config.SUBSCRIPTION_PLANS['free'])
            
            # Check limits
            if plan['messages_total'] is not None and messages_lifetime >= plan['messages_total']:
                cursor.close()
                conn.close()
                return {
                    "allowed": False,
                    "tier": tier,
                    "reason": "lifetime_limit",
                    "used": messages_lifetime,
                    "limit": plan['messages_total']
                }
            
            if plan['messages_per_day'] is not None and messages_today >= plan['messages_per_day']:
                cursor.close()
                conn.close()
                return {
                    "allowed": False,
                    "tier": tier,
                    "reason": "daily_limit",
                    "used": messages_today,
                    "limit": plan['messages_per_day'],
                    "reset_at": daily_reset_at.isoformat() if daily_reset_at else None
                }
            
            # Increment counters
            cursor.execute("""
                UPDATE users 
                SET messages_lifetime = messages_lifetime + 1, 
                    messages_today = messages_today + 1
                WHERE user_id = %s
                RETURNING messages_lifetime, messages_today
            """, (user_id,))
            
            updated = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                "allowed": True,
                "tier": tier,
                "messages_lifetime": updated['messages_lifetime'],
                "messages_today": updated['messages_today'],
                "limit_total": plan['messages_total'],
                "limit_daily": plan['messages_per_day']
            }
            
        except Exception as e:
            print(f"Error checking message limit: {str(e)}")
            return {"allowed": True}  # Default to allowing on error
    
    def upgrade_subscription(self, user_id: str, tier: str, subscription_id: str = None) -> bool:
        """Upgrade user subscription tier."""
        from datetime import datetime, timedelta
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Calculate expiry (30 days from now for paid plans)
            if tier in ['limited', 'unlimited']:
                expires_at = datetime.now() + timedelta(days=30)
            else:
                expires_at = None
            
            cursor.execute("""
                UPDATE users 
                SET subscription_tier = %s,
                    subscription_status = 'active',
                    subscription_expires_at = %s,
                    razorpay_subscription_id = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """, (tier, expires_at, subscription_id, user_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error upgrading subscription: {str(e)}")
            return False


# Global instance
user_db = UserDatabase()
