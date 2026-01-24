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
        self.store: Dict[str, tuple] = {}  # Fallback: {key: (value, expiry_time)}
        
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
        if full_key not in self.store:
            return None
        
        value, expiry = self.store[full_key]
        if time.time() > expiry:
            del self.store[full_key]
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
        self.store[full_key] = (value, expiry)
    
    def get_or_set(self, key: str, compute_func, ttl: Optional[int] = None) -> Any:
        """Get value from cache or compute and cache if not present."""
        cached = self.get(key)
        if cached is not None:
            return cached
        
        value = compute_func()
        self.set(key, value, ttl)
        return value
    
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
        keys_to_delete = [k for k in self.store.keys() if k.startswith(self.prefix)]
        for key in keys_to_delete:
            del self.store[key]
    
    def clear_expired(self) -> None:
        """Remove expired entries from memory store."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry) in self.store.items()
            if current_time > expiry
        ]
        for key in expired_keys:
            del self.store[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        self.clear_expired()
        total_entries = len(self.store)
        memory_estimate = sum(len(str(v[0])) for v in self.store.values())
        
        # Try to get Redis stats
        if self.redis_client:
            try:
                keys = self.redis_client.keys(f"{self.prefix}:*")
                total_entries += len(keys)
            except:
                pass
        
        return {
            "total_entries": total_entries,
            "memory_estimate": memory_estimate,
        }


# Create cache instances for different purposes
query_response_cache = Cache(default_ttl=3600, prefix="query")          # 1 hour
web_search_cache = Cache(default_ttl=3600, prefix="search")             # 1 hour (shared across users)
news_cache = Cache(default_ttl=1800, prefix="news")                     # 30 minutes
horoscope_cache = Cache(default_ttl=86400, prefix="horoscope")          # 24 hours
sports_data_cache = Cache(default_ttl=3600, prefix="sports")            # 1 hour
web_search_rate_limit_cache = Cache(default_ttl=86400, prefix="ws_rate") # 24 hours for rate limiting


def cache_query_response(query: str, response: str, ttl: int = 3600) -> None:
    """Cache a query-response pair."""
    key = query_response_cache._generate_key(query)
    query_response_cache.set(key, response, ttl)


def get_cached_response(query: str) -> Optional[str]:
    """Get cached response for a query."""
    key = query_response_cache._generate_key(query)
    return query_response_cache.get(key)


def cache_web_search_result(query: str, results: list, ttl: int = 1800) -> None:
    """Cache web search results."""
    key = web_search_cache._generate_key(query)
    web_search_cache.set(key, results, ttl)


def get_cached_search_results(query: str) -> Optional[list]:
    """Get cached web search results."""
    key = web_search_cache._generate_key(query)
    return web_search_cache.get(key)


def cache_news(category: str, articles: list, ttl: int = 1800) -> None:
    """Cache news articles."""
    key = news_cache._generate_key(category)
    news_cache.set(key, articles, ttl)


def get_cached_news(category: str) -> Optional[list]:
    """Get cached news articles."""
    key = news_cache._generate_key(category)
    return news_cache.get(key)


def cache_horoscope(sign: str, text: str, ttl: int = 86400) -> None:
    """Cache horoscope prediction."""
    key = horoscope_cache._generate_key(sign)
    horoscope_cache.set(key, text, ttl)


def get_cached_horoscope(sign: str) -> Optional[str]:
    """Get cached horoscope prediction."""
    key = horoscope_cache._generate_key(sign)
    return horoscope_cache.get(key)


def increment_web_search_count(user_id: str) -> int:
    """Increment and return web search count for user (resets daily)."""
    key = f"ws_count:{user_id}"
    current_count = web_search_rate_limit_cache.get(key) or 0
    new_count = current_count + 1
    web_search_rate_limit_cache.set(key, new_count, ttl=86400)  # Reset after 24 hours
    return new_count


def get_web_search_count(user_id: str) -> int:
    """Get current web search count for user."""
    key = f"ws_count:{user_id}"
    return web_search_rate_limit_cache.get(key) or 0


def cache_sports_data(key: str, data: dict, ttl: int = 3600) -> None:
    """Cache sports data with custom key."""
    sports_data_cache.set(key, data, ttl)


def get_cached_sports_data(key: str) -> Optional[dict]:
    """Get cached sports data by key."""
    return sports_data_cache.get(key)


def clear_all_caches() -> None:
    """Clear all cache instances."""
    query_response_cache.clear()
    web_search_cache.clear()
    news_cache.clear()
    horoscope_cache.clear()
    sports_data_cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """Get statistics for all caches."""
    return {
        "query_response": query_response_cache.get_stats(),
        "web_search": web_search_cache.get_stats(),
        "news": news_cache.get_stats(),
        "horoscope": horoscope_cache.get_stats(),
        "sports_data": sports_data_cache.get_stats(),
    }
