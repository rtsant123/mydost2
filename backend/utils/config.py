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
    SYSTEM_PROMPT = """You are MyDost, a helpful and friendly AI assistant. 
You are conversational, warm, and supportive. You help users with multiple domains including education, sports, astrology, news, and more.
You provide accurate, thoughtful answers and admit when you're unsure about something.
You respond in the same language as the user's input (Assamese, Hindi, English, or Hinglish) to make them feel comfortable.
Hinglish (Hindi-English mix) is fully supported - users can mix Hindi and English freely.

⚠️ IMPORTANT RULES:
- Only answer what the user asks. Don't volunteer unrelated information.
- If user asks about education, don't mention sports predictions.
- If user asks about news, don't mention teer results.
- Stay focused on their question. Don't suggest other topics unless relevant.
- Be helpful for THEIR question, not all possible questions.

📰 FOR WEB SEARCH RESPONSES - Format like a news article:
When using web search information, structure your response like this:
1. Start with a brief summary paragraph (2-3 sentences)
2. Break down into clear sections with headers (use bold **headers**)
3. Use bullet points for multiple related items
4. Cite sources immediately after facts using [1], [2], [3]
5. Keep paragraphs short and scannable (2-3 sentences max)
6. End with "Other Details" section if there are minor points
Example format:
**Main Topic**
Brief overview with citation [1].

**Section 1**
- Point with citation [2]
- Another point with citation [3]

**Section 2**
Details here [1].

**Other Details**
- Minor point [2]

If a module/feature is disabled, politely inform the user that the feature is currently unavailable."""
    
    # API Keys (loaded from environment)
    # LLM Provider Selection
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")  # anthropic, openai, gemini
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Model Names (configurable via environment variables)
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")  # Claude Haiku (fast & cheap)
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/chatbot_db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Web Search Provider Selection
    SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "serper")  # serper, serpapi, brave
    SEARCH_API_KEY = os.getenv("SEARCH_API_KEY", "")
    SEARCH_API_URL = os.getenv("SEARCH_API_URL", "https://google.serper.dev/search")
    SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
    BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
    
    # Other APIs
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    SPORTS_API_KEY = os.getenv("SPORTS_API_KEY", "")
    ASTROLOGY_API_KEY = os.getenv("ASTROLOGY_API_KEY", "")
    ASTROLOGY_API_URL = os.getenv("ASTROLOGY_API_URL", "https://json.freeastrologyapi.com/")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # Authentication & Free Limits
    ENABLE_FREE_LIMITS = os.getenv("ENABLE_FREE_LIMITS", "false").lower() == "true"
    FREE_CHAT_LIMIT = int(os.getenv("FREE_CHAT_LIMIT", "3"))
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    
    # Subscription Plans
    SUBSCRIPTION_PLANS = {
        "guest": {
            "name": "Guest",
            "price": 0,
            "messages_total": 3,
            "messages_per_day": None,
            "features": ["basic_chat"]
        },
        "free": {
            "name": "Free (Registered)",
            "price": 0,
            "messages_total": 10,
            "messages_per_day": None,
            "features": ["basic_chat", "memory"]
        },
        "limited": {
            "name": "Limited Plan",
            "price": 399,
            "currency": "INR",
            "messages_total": None,
            "messages_per_day": 50,
            "features": ["basic_chat", "memory", "web_search", "rag"]
        },
        "unlimited": {
            "name": "Unlimited Plan",
            "price": 999,
            "currency": "INR",
            "messages_total": None,
            "messages_per_day": None,
            "features": ["basic_chat", "memory", "web_search", "rag", "priority_support"]
        }
    }
    
    # Razorpay
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
    RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
    
    # NextAuth (for frontend)
    NEXTAUTH_URL = os.getenv("NEXTAUTH_URL", "http://localhost:3000")
    NEXTAUTH_SECRET = os.getenv("NEXTAUTH_SECRET", "")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # Service endpoints
    PORT = int(os.getenv("PORT", "8000"))
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Rate limits
    MAX_API_CALLS_PER_DAY = int(os.getenv("MAX_API_CALLS_PER_DAY", "1000"))
    MAX_TOKENS_PER_USER_PER_DAY = int(os.getenv("MAX_TOKENS_PER_USER_PER_DAY", "100000"))
    
    # Web Search Rate Limits (prevent abuse)
    WEB_SEARCH_LIMIT_GUEST = int(os.getenv("WEB_SEARCH_LIMIT_GUEST", "5"))  # 5 searches per day for guests
    WEB_SEARCH_LIMIT_FREE = int(os.getenv("WEB_SEARCH_LIMIT_FREE", "10"))   # 10 per day for free users
    WEB_SEARCH_LIMIT_PAID = int(os.getenv("WEB_SEARCH_LIMIT_PAID", "50"))   # 50 per day for paid users
    WEB_SEARCH_CACHE_TTL = int(os.getenv("WEB_SEARCH_CACHE_TTL", "3600"))    # Cache for 1 hour (reuse across users)
    
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
    def get_client_fingerprint(cls, user_agent: str, ip: str) -> str:
        """Generate a client fingerprint from IP and user agent."""
        import hashlib
        combined = f"{ip}:{user_agent}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]
    
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
