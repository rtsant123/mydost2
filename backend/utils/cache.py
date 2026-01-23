"""Simple caching mechanism for the chatbot."""
import time
from typing import Any, Dict, Optional
from hashlib import md5


class Cache:
    """In-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 3600):
        """Initialize cache with default TTL in seconds."""
        self.store: Dict[str, tuple] = {}  # {key: (value, expiry_time)}
        self.default_ttl = default_ttl
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
        key_string = "|".join(key_parts)
        return md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key not in self.store:
            return None
        
        value, expiry = self.store[key]
        if time.time() > expiry:
            del self.store[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        if ttl is None:
            ttl = self.default_ttl
        
        expiry = time.time() + ttl
        self.store[key] = (value, expiry)
    
    def get_or_set(self, key: str, compute_func, ttl: Optional[int] = None) -> Any:
        """Get value from cache or compute and cache if not present."""
        cached = self.get(key)
        if cached is not None:
            return cached
        
        value = compute_func()
        self.set(key, value, ttl)
        return value
    
    def clear(self) -> None:
        """Clear all cache."""
        self.store.clear()
    
    def clear_expired(self) -> None:
        """Remove expired entries."""
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
        return {
            "total_entries": len(self.store),
            "memory_estimate": sum(
                len(str(v[0])) for v in self.store.values()
            ),  # Rough estimate
        }


# Global cache instances
query_response_cache = Cache(default_ttl=3600)  # 1 hour
web_search_cache = Cache(default_ttl=1800)      # 30 minutes
news_cache = Cache(default_ttl=1800)             # 30 minutes
horoscope_cache = Cache(default_ttl=86400)       # 24 hours
sports_data_cache = Cache(default_ttl=3600)      # 1 hour


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
    """Cache horoscope for a zodiac sign."""
    key = horoscope_cache._generate_key(sign)
    horoscope_cache.set(key, text, ttl)


def get_cached_horoscope(sign: str) -> Optional[str]:
    """Get cached horoscope for a zodiac sign."""
    key = horoscope_cache._generate_key(sign)
    return horoscope_cache.get(key)


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
