"""Redis-based caching with fallback to in-memory for the chatbot."""
import os
import time
import json
from typing import Any, Dict, Optional
from hashlib import md5

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Redis not available, using in-memory cache")


class Cache:
    """Cache with Redis support and in-memory fallback."""
    
    def __init__(self, default_ttl: int = 3600, prefix: str = "chatbot"):
        """
        Initialize cache with default TTL in seconds.
        
        Args:
            default_ttl: Default time-to-live in seconds
            prefix: Key prefix for namespacing
        """
        self.default_ttl = default_ttl
        self.prefix = prefix
        self.redis_client = None
        self.memory_store: Dict[str, tuple] = {}  # Fallback: {key: (value, expiry_time)}
        
        # Try to connect to Redis
        if REDIS_AVAILABLE:
            try:
                redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                print(f"Connected to Redis for {prefix} cache")
            except Exception as e:
                print(f"Redis connection failed: {e}. Using in-memory cache.")
                self.redis_client = None
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
        key_string = "|".join(key_parts)
        hash_key = md5(key_string.encode()).hexdigest()
        return f"{self.prefix}:{hash_key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        full_key = f"{self.prefix}:{key}" if not key.startswith(self.prefix) else key
        
        # Try Redis first
        if self.redis_client:
            try:
                value = self.redis_client.get(full_key)
                if value:
                    return json.loads(value)
                return None
            except Exception as e:
                print(f"Redis get error: {e}")
        
        # Fallback to memory
        if full_key not in self.memory_store:
            return None
        
        value, expiry = self.memory_store[full_key]
        if time.time() > expiry:
            del self.memory_store[full_key]
            return None
        
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        if ttl is None:
            ttl = self.default_ttl
        
        full_key = f"{self.prefix}:{key}" if not key.startswith(self.prefix) else key
        
        # Try Redis first
        if self.redis_client:
            try:
                self.redis_client.setex(
                    full_key,
                    ttl,
                    json.dumps(value)
                )
                return
            except Exception as e:
                print(f"Redis set error: {e}")
        
        # Fallback to memory
        expiry = time.time() + ttl
        self.memory_store[full_key] = (value, expiry)
    
    def get_or_set(self, key: str, compute_func, ttl: Optional[int] = None) -> Any:
        """Get value from cache or compute and cache if not present."""
        cached = self.get(key)
        if cached is not None:
            return cached
        
        value = compute_func()
        self.set(key, value, ttl)
        return value
    
    def delete(self, key: str) -> None:
        """Delete key from cache."""
        full_key = f"{self.prefix}:{key}" if not key.startswith(self.prefix) else key
        
        if self.redis_client:
            try:
                self.redis_client.delete(full_key)
            except Exception as e:
                print(f"Redis delete error: {e}")
        
        if full_key in self.memory_store:
            del self.memory_store[full_key]
    
    def clear(self) -> None:
        """Clear all cached data for this prefix."""
        if self.redis_client:
            try:
                # Delete all keys with this prefix
                keys = self.redis_client.keys(f"{self.prefix}:*")
                if keys:
                    self.redis_client.delete(*keys)
            except Exception as e:
                print(f"Redis clear error: {e}")
        
        # Clear memory store
        keys_to_delete = [k for k in self.memory_store.keys() if k.startswith(self.prefix)]
        for key in keys_to_delete:
            del self.memory_store[key]
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        full_key = f"{self.prefix}:{key}" if not key.startswith(self.prefix) else key
        
        if self.redis_client:
            try:
                return self.redis_client.exists(full_key) > 0
            except Exception as e:
                print(f"Redis exists error: {e}")
        
        if full_key in self.memory_store:
            _, expiry = self.memory_store[full_key]
            if time.time() <= expiry:
                return True
            del self.memory_store[full_key]
        
        return False


# Create cache instances for different purposes
query_response_cache = Cache(default_ttl=3600, prefix="query")          # 1 hour
web_search_cache = Cache(default_ttl=7200, prefix="search")            # 2 hours
news_cache = Cache(default_ttl=1800, prefix="news")                    # 30 minutes
horoscope_cache = Cache(default_ttl=86400, prefix="horoscope")         # 24 hours
sports_data_cache = Cache(default_ttl=3600, prefix="sports")           # 1 hour
