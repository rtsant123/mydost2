"""Authentication API routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from models.user import user_db

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
