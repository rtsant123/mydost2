"""Admin API routes for system management."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from utils.config import config
from utils.cache import get_cache_stats, clear_all_caches
from services.astrology_service import astrology_service
from services.news_service import news_service

router = APIRouter()

# Models
class AdminLoginRequest(BaseModel):
    password: str


class AdminLoginResponse(BaseModel):
    success: bool
    token: str
    message: str


class FeatureToggle(BaseModel):
    feature: str
    enabled: bool


class ConfigUpdate(BaseModel):
    enabled_modules: Optional[Dict[str, bool]] = None
    system_prompt: Optional[str] = None
    rate_limits: Optional[Dict[str, int]] = None


# Dependency for admin authentication
async def verify_admin_password(password: str) -> bool:
    """Verify admin password."""
    return password == config.ADMIN_PASSWORD


@router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest):
    """
    Admin login endpoint.
    Returns a token if password is correct.
    """
    if await verify_admin_password(request.password):
        # In production, generate a JWT token
        return AdminLoginResponse(
            success=True,
            token="admin_token_" + config.ADMIN_PASSWORD[:8],
            message="Login successful"
        )
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin password"
        )


@router.get("/admin/config")
async def get_config():
    """Get current system configuration."""
    return {
        "enabled_modules": config.ENABLED_MODULES,
        "system_prompt": config.SYSTEM_PROMPT,
        "rate_limits": {
            "max_api_calls_per_day": config.MAX_API_CALLS_PER_DAY,
            "max_tokens_per_user_per_day": config.MAX_TOKENS_PER_USER_PER_DAY,
        },
        "memory_settings": {
            "conversation_history_limit": config.CONVERSATION_HISTORY_LIMIT,
            "max_retrieval_results": config.MAX_RETRIEVAL_RESULTS,
            "cache_ttl_seconds": config.CACHE_TTL_SECONDS,
        }
    }


@router.post("/admin/config")
async def update_config(update: ConfigUpdate):
    """Update system configuration."""
    try:
        if update.enabled_modules:
            for module, enabled in update.enabled_modules.items():
                config.toggle_module(module, enabled)
        
        if update.system_prompt:
            config.update_system_prompt(update.system_prompt)
        
        if update.rate_limits:
            if "max_api_calls_per_day" in update.rate_limits:
                config.MAX_API_CALLS_PER_DAY = update.rate_limits["max_api_calls_per_day"]
            if "max_tokens_per_user_per_day" in update.rate_limits:
                config.MAX_TOKENS_PER_USER_PER_DAY = update.rate_limits["max_tokens_per_user_per_day"]
        
        return {
            "success": True,
            "message": "Configuration updated",
            "config": config.get_config_dict()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/module/toggle")
async def toggle_module(toggle: FeatureToggle):
    """Toggle a feature module on or off."""
    try:
        if toggle.feature not in config.ENABLED_MODULES:
            raise HTTPException(status_code=404, detail=f"Module {toggle.feature} not found")
        
        config.toggle_module(toggle.feature, toggle.enabled)
        
        return {
            "success": True,
            "module": toggle.feature,
            "enabled": toggle.enabled,
            "message": f"Module {toggle.feature} is now {'enabled' if toggle.enabled else 'disabled'}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/stats")
async def get_stats():
    """Get usage statistics."""
    return {
        "usage_stats": config.USAGE_STATS,
        "cache_stats": get_cache_stats(),
        "timestamp": config.USAGE_STATS.get("reset_date"),
    }


@router.post("/admin/cache/clear")
async def clear_cache():
    """Clear all caches."""
    try:
        clear_all_caches()
        return {"success": True, "message": "All caches cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/reindex")
async def reindex_vectors():
    """Trigger vector database reindexing."""
    try:
        # This is a placeholder - actual implementation depends on vector DB
        return {
            "success": True,
            "message": "Reindexing initiated",
            "status": "This feature requires vector DB support"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/modules")
async def list_modules():
    """List all available modules with current status."""
    return {
        "modules": [
            {
                "name": module,
                "enabled": enabled,
                "description": f"Module: {module}"
            }
            for module, enabled in config.ENABLED_MODULES.items()
        ]
    }


@router.post("/admin/system-prompt/update")
async def update_system_prompt(prompt: Dict[str, str]):
    """Update the system prompt."""
    try:
        new_prompt = prompt.get("prompt")
        if not new_prompt:
            raise HTTPException(status_code=400, detail="prompt field is required")
        
        config.update_system_prompt(new_prompt)
        
        return {
            "success": True,
            "message": "System prompt updated",
            "prompt": config.SYSTEM_PROMPT
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/system-prompt")
async def get_system_prompt():
    """Get current system prompt."""
    return {
        "system_prompt": config.SYSTEM_PROMPT
    }


@router.post("/admin/api-keys/update")
async def update_api_keys(keys: Dict[str, str]):
    """Update API keys (stored in memory for this session)."""
    try:
        # Update configuration with provided keys
        for key_name, key_value in keys.items():
            if key_name == "openai_api_key":
                config.OPENAI_API_KEY = key_value
            elif key_name == "search_api_key":
                config.SEARCH_API_KEY = key_value
            elif key_name == "news_api_key":
                config.NEWS_API_KEY = key_value
            elif key_name == "sports_api_key":
                config.SPORTS_API_KEY = key_value
        
        return {
            "success": True,
            "message": "API keys updated for this session",
            "note": "Keys are not persisted. Update environment variables for permanent changes."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/health")
async def admin_health():
    """Admin panel health check."""
    return {
        "status": "healthy",
        "admin_panel_version": "1.0.0",
        "enabled_modules": list(m for m, e in config.ENABLED_MODULES.items() if e),
        "disabled_modules": list(m for m, e in config.ENABLED_MODULES.items() if not e),
    }


@router.post("/admin/data/add-teer-result")
async def add_teer_result(result: Dict[str, Any]):
    """Add a Teer result for prediction analysis."""
    try:
        success = teer_service.add_result(
            date=result.get("date"),
            first_round=result.get("first_round"),
            second_round=result.get("second_round"),
            house=result.get("house", "Shillong")
        )
        
        if success:
            return {"success": True, "message": "Teer result added"}
        else:
            raise HTTPException(status_code=400, detail="Failed to add result")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/data/teer-stats")
async def get_teer_stats(days: int = 30):
    """Get Teer analysis statistics."""
    try:
        stats = teer_service.get_statistics(days=days)
        return {"stats": stats, "days_analyzed": days}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
