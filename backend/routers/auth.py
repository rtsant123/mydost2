"""Authentication API routes."""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from models.user import user_db
import jwt
from datetime import datetime, timedelta
from utils.config import config

router = APIRouter()


class GoogleSignInRequest(BaseModel):
    """Google sign-in request model."""
    email: str
    name: str
    image: Optional[str] = None
    google_id: str


class UserPreferencesRequest(BaseModel):
    """User preferences model."""
    language: str
    tone: str
    interests: list[str]
    response_style: str


@router.post("/auth/google-signin")
async def google_signin(request: GoogleSignInRequest):
    """
    Handle Google OAuth sign-in.
    Creates or retrieves user from PostgreSQL database.
    """
    try:
        user = user_db.create_or_get_user(
            email=request.email,
            name=request.name,
            google_id=request.google_id,
            image=request.image
        )
        
        is_new_user = user.get("has_preferences") == False
        
        return {
            "user_id": str(user["user_id"]),
            "has_preferences": user.get("has_preferences", False),
            "preferences": user.get("preferences", {}),
            "is_new_user": is_new_user,
        }
    
    except Exception as e:
        print(f"Error in Google sign-in: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to sign in")


@router.post("/users/{user_id}/preferences")
async def save_user_preferences(user_id: str, preferences: UserPreferencesRequest):
    """Save user preferences to database."""
    try:
        success = user_db.save_preferences(user_id, preferences.dict())
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save preferences")
        
        return {
            "success": True,
            "message": "Preferences saved successfully",
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save preferences")


@router.get("/users/{user_id}/preferences")
async def get_user_preferences(user_id: str):
    """Get user preferences from database."""
    try:
        result = user_db.get_preferences(user_id)
        return result
    
    except Exception as e:
        print(f"Error retrieving preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve preferences")


@router.get("/users/{user_id}")
async def get_user_info(user_id: str):
    """Get user information from database."""
    try:
        user = user_db.get_user(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user_id": str(user["user_id"]),
            "name": user.get("name"),
            "email": user.get("email"),
            "image": user.get("image"),
            "has_preferences": user.get("has_preferences", False),
            "preferences": user.get("preferences", {}),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user")


@router.get("/users/{user_id}/stats")
async def get_user_stats(user_id: str, days: int = 7):
    """Get user usage statistics."""
    try:
        today_usage = user_db.get_today_usage(user_id)
        period_stats = user_db.get_user_stats(user_id, days)
        
        return {
            "today": today_usage,
            f"last_{days}_days": period_stats,
        }
    
    except Exception as e:
        print(f"Error retrieving stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve stats")


# ============= NEW EMAIL/PASSWORD AUTH =============

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    referred_by: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[dict] = None
    token: Optional[str] = None

def create_jwt_token(user_id: str, email: str) -> str:
    """Create JWT token for user."""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")

@router.post("/auth/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    """Sign up with email and password."""
    try:
        # Check if user exists
        conn = user_db._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE email = %s", (request.email,))
        existing = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        user = user_db.create_user_with_password(
            email=request.email,
            name=request.name,
            password=request.password,
            referred_by=request.referred_by
        )
        
        if not user:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        # Generate token
        token = create_jwt_token(str(user['user_id']), user['email'])
        
        # Remove sensitive data
        user_safe = {
            "user_id": str(user['user_id']),
            "email": user['email'],
            "name": user['name'],
            "referral_code": user['referral_code']
        }
        
        return AuthResponse(
            success=True,
            message="Account created successfully",
            user=user_safe,
            token=token
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login with email and password."""
    try:
        user = user_db.verify_password(request.email, request.password)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Generate token
        token = create_jwt_token(str(user['user_id']), user['email'])
        
        # Remove sensitive data
        user_safe = {
            "user_id": str(user['user_id']),
            "email": user['email'],
            "name": user['name'],
            "referral_code": user.get('referral_code')
        }
        
        return AuthResponse(
            success=True,
            message="Login successful",
            user=user_safe,
            token=token
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auth/me")
async def get_current_user(request: Request):
    """Get current user from token."""
    try:
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        token = auth_header.split(" ")[1]
        
        # Decode token
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        
        # Get user
        user = user_db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Remove sensitive data
        user_safe = {
            "user_id": str(user['user_id']),
            "email": user['email'],
            "name": user['name'],
            "referral_code": user.get('referral_code'),
            "preferences": user.get('preferences', {})
        }
        
        return {"success": True, "user": user_safe}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/guest/check-limit")
async def check_guest_limit(request: Request):
    """Check if guest has exceeded free message limit."""
    try:
        # Get client info
        user_agent = request.headers.get("user-agent", "unknown")
        # Try to get real IP (considering proxies)
        ip = request.headers.get("x-forwarded-for", request.client.host).split(",")[0]
        
        # Generate fingerprint
        fingerprint = config.get_client_fingerprint(user_agent, ip)
        
        # Get usage count
        count = user_db.get_guest_usage(fingerprint)
        
        # Check limit
        limit_enabled = config.ENABLE_FREE_LIMITS
        limit = config.FREE_CHAT_LIMIT
        exceeded = limit_enabled and count >= limit
        
        return {
            "fingerprint": fingerprint,
            "message_count": count,
            "limit": limit,
            "limit_enabled": limit_enabled,
            "exceeded": exceeded,
            "remaining": max(0, limit - count) if limit_enabled else -1
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
