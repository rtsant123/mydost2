"""Configuration management for the chatbot system."""
import os
from typing import Dict, Any
from datetime import datetime


class SystemConfig:
    """Global system configuration with feature toggles and settings."""
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Database URLs
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/chatbot_db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Feature toggles (can be modified via admin panel)
    ENABLED_MODULES = {
        "education": True,
        "sports": True,
        "teer": True,
        "astrology": True,
        "ocr": True,
        "pdf": True,
        "news": True,
        "image_editing": True,
        "personal_notes": True,
    }
    
    # System prompt (modifiable via admin panel)
    SYSTEM_PROMPT = """You are Claude, a helpful, harmless, and honest AI assistant. 
You are conversational and thoughtful. You engage in in-depth discussions about a wide range of topics.
You provide accurate, nuanced answers and acknowledge uncertainty when appropriate.
When you don't have information about something, you admit it rather than speculate.
You respond in the same language as the user's input (Assamese, Hindi, or English).
If a module/feature is disabled, politely inform the user that the feature is currently unavailable."""
    
    # API Keys (loaded from environment)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    VECTOR_DB_URL = os.getenv("VECTOR_DB_URL", "http://localhost:6333")
    VECTOR_DB_API_KEY = os.getenv("VECTOR_DB_API_KEY", "")
    SEARCH_API_KEY = os.getenv("SEARCH_API_KEY", "")
    SEARCH_API_URL = os.getenv("SEARCH_API_URL", "https://api.serper.dev/search")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    SPORTS_API_KEY = os.getenv("SPORTS_API_KEY", "")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # Service endpoints
    PORT = int(os.getenv("PORT", "8000"))
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Rate limits
    MAX_API_CALLS_PER_DAY = int(os.getenv("MAX_API_CALLS_PER_DAY", "1000"))
    MAX_TOKENS_PER_USER_PER_DAY = int(os.getenv("MAX_TOKENS_PER_USER_PER_DAY", "100000"))
    
    # Memory and context
    CONVERSATION_HISTORY_LIMIT = 10  # Keep last N messages in context
    MAX_RETRIEVAL_RESULTS = 5  # Number of vector DB results to retrieve
    CACHE_TTL_SECONDS = 3600  # Cache results for 1 hour
    
    # Analytics
    USAGE_STATS = {
        "total_messages": 0,
        "total_api_calls": 0,
        "total_tokens": 0,
        "features_used": {
            "education": 0,
            "sports": 0,
            "teer": 0,
            "astrology": 0,
            "ocr": 0,
            "pdf": 0,
            "news": 0,
            "image_editing": 0,
            "personal_notes": 0,
            "web_search": 0,
        },
        "reset_date": datetime.now().isoformat(),
    }
    
    @classmethod
    def is_module_enabled(cls, module_name: str) -> bool:
        """Check if a specific module is enabled."""
        return cls.ENABLED_MODULES.get(module_name, False)
    
    @classmethod
    def toggle_module(cls, module_name: str, enabled: bool) -> None:
        """Toggle a module on or off."""
        if module_name in cls.ENABLED_MODULES:
            cls.ENABLED_MODULES[module_name] = enabled
    
    @classmethod
    def update_system_prompt(cls, new_prompt: str) -> None:
        """Update the system prompt."""
        cls.SYSTEM_PROMPT = new_prompt
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Return current configuration as dictionary."""
        return {
            "enabled_modules": cls.ENABLED_MODULES,
            "system_prompt": cls.SYSTEM_PROMPT,
            "rate_limits": {
                "max_api_calls_per_day": cls.MAX_API_CALLS_PER_DAY,
                "max_tokens_per_user_per_day": cls.MAX_TOKENS_PER_USER_PER_DAY,
            },
            "memory_settings": {
                "conversation_history_limit": cls.CONVERSATION_HISTORY_LIMIT,
                "max_retrieval_results": cls.MAX_RETRIEVAL_RESULTS,
                "cache_ttl_seconds": cls.CACHE_TTL_SECONDS,
            }
        }
    
    @classmethod
    def update_config(cls, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        if "enabled_modules" in config_dict:
            cls.ENABLED_MODULES.update(config_dict["enabled_modules"])
        if "system_prompt" in config_dict:
            cls.SYSTEM_PROMPT = config_dict["system_prompt"]
        if "rate_limits" in config_dict:
            limits = config_dict["rate_limits"]
            if "max_api_calls_per_day" in limits:
                cls.MAX_API_CALLS_PER_DAY = limits["max_api_calls_per_day"]
            if "max_tokens_per_user_per_day" in limits:
                cls.MAX_TOKENS_PER_USER_PER_DAY = limits["max_tokens_per_user_per_day"]


# Initialize config
config = SystemConfig()
