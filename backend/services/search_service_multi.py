"""Multi-provider web search service supporting Serper, SerpApi, and Brave."""
from typing import List, Dict, Any, Optional
import aiohttp
import requests
from utils.config import config
from utils.cache import get_cached_search_results, cache_web_search_result


class MultiSearchService:
    """Service for multi-provider web search integration."""
    
    def __init__(self, provider: str = None):
        """
        Initialize search service with specified provider.
        
        Args:
            provider: Search provider ('serper', 'serpapi', 'brave')
        """
        self.provider = provider or config.SEARCH_PROVIDER
        
        # Set API key and URL based on provider
        if self.provider == "serper":
            self.api_key = config.SEARCH_API_KEY
            self.api_url = config.SEARCH_API_URL or "https://google.serper.dev/search"
        elif self.provider == "serpapi":
            self.api_key = config.SERPAPI_KEY
            self.api_url = "https://serpapi.com/search"
        elif self.provider == "brave":
            self.api_key = config.BRAVE_API_KEY
            self.api_url = "https://api.search.brave.com/res/v1/web/search"
        else:
            raise ValueError(f"Unknown search provider: {self.provider}")
    
    def search(self, query: str, limit: int = 5) -> Optional[Dict[str, Any]]:
        """
        Perform web search (synchronous).
        
        Args:
            query: Search query
            limit: Number of results to return
        
        Returns:
            Search results with snippets and source URLs
        """
        if not self.api_key:
            return None
        
        # Check cache first
        cached = get_cached_search_results(query)
        if cached:
            return {"results": cached, "from_cache": True}
        
        try:
            if self.provider == "serper":
                return self._search_serper(query, limit)
            elif self.provider == "serpapi":
                return self._search_serpapi(query, limit)
            elif self.provider == "brave":
                return self._search_brave(query, limit)
        
        except Exception as e:
            print(f"Error performing web search: {str(e)}")
            return None
    
    def _search_serper(self, query: str, limit: int) -> Optional[Dict[str, Any]]:
        """Search using Serper API."""
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "num": limit,
            "autocorrect": True,
            "page": 1,
        }
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            results = []
            for result in data.get("organic", [])[:limit]:
                results.append({
                    "title": result.get("title"),
                    "url": result.get("link"),
                    "snippet": result.get("snippet"),
                    "source": result.get("source"),
                })
            
            cache_web_search_result(query, results)
            
            return {
                "results": results,
                "query": query,
                "from_cache": False,
                "provider": "serper"
            }
        else:
            print(f"Serper API error: {response.status_code}")
            return None
    
    def _search_serpapi(self, query: str, limit: int) -> Optional[Dict[str, Any]]:
        """Search using SerpApi."""
        params = {
            "q": query,
            "api_key": self.api_key,
            "num": limit,
            "engine": "google"
        }
        
        response = requests.get(
            self.api_url,
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            results = []
            for result in data.get("organic_results", [])[:limit]:
                results.append({
                    "title": result.get("title"),
                    "url": result.get("link"),
                    "snippet": result.get("snippet"),
                    "source": result.get("displayed_link"),
                })
            
            cache_web_search_result(query, results)
            
            return {
                "results": results,
                "query": query,
                "from_cache": False,
                "provider": "serpapi"
            }
        else:
            print(f"SerpApi error: {response.status_code}")
            return None
    
    def _search_brave(self, query: str, limit: int) -> Optional[Dict[str, Any]]:
        """Search using Brave Search API."""
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }
        
        params = {
            "q": query,
            "count": limit
        }
        
        response = requests.get(
            self.api_url,
            headers=headers,
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            results = []
            for result in data.get("web", {}).get("results", [])[:limit]:
                results.append({
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "snippet": result.get("description"),
                    "source": result.get("url"),
                })
            
            cache_web_search_result(query, results)
            
            return {
                "results": results,
                "query": query,
                "from_cache": False,
                "provider": "brave"
            }
        else:
            print(f"Brave API error: {response.status_code}")
            return None
    
    async def async_search(self, query: str, limit: int = 5) -> Optional[Dict[str, Any]]:
        """
        Perform web search (asynchronous).
        
        Args:
            query: Search query
            limit: Number of results to return
        
        Returns:
            Search results with snippets and source URLs
        """
        if not self.api_key:
            return None
        
        # Check cache first
        cached = get_cached_search_results(query)
        if cached:
            return {"results": cached, "from_cache": True}
        
        try:
            if self.provider == "serper":
                return await self._async_search_serper(query, limit)
            elif self.provider == "serpapi":
                return await self._async_search_serpapi(query, limit)
            elif self.provider == "brave":
                return await self._async_search_brave(query, limit)
        
        except Exception as e:
            print(f"Error performing async web search: {str(e)}")
            return None
    
    async def _async_search_serper(self, query: str, limit: int) -> Optional[Dict[str, Any]]:
        """Async search using Serper API."""
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "num": limit,
            "autocorrect": True,
            "page": 1,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, headers=headers, json=payload, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    results = []
                    for result in data.get("organic", [])[:limit]:
                        results.append({
                            "title": result.get("title"),
                            "url": result.get("link"),
                            "snippet": result.get("snippet"),
                            "source": result.get("source"),
                        })
                    
                    cache_web_search_result(query, results)
                    
                    return {
                        "results": results,
                        "query": query,
                        "from_cache": False,
                        "provider": "serper"
                    }
                else:
                    print(f"Serper API error: {response.status}")
                    return None
    
    async def _async_search_serpapi(self, query: str, limit: int) -> Optional[Dict[str, Any]]:
        """Async search using SerpApi."""
        params = {
            "q": query,
            "api_key": self.api_key,
            "num": limit,
            "engine": "google"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    results = []
                    for result in data.get("organic_results", [])[:limit]:
                        results.append({
                            "title": result.get("title"),
                            "url": result.get("link"),
                            "snippet": result.get("snippet"),
                            "source": result.get("displayed_link"),
                        })
                    
                    cache_web_search_result(query, results)
                    
                    return {
                        "results": results,
                        "query": query,
                        "from_cache": False,
                        "provider": "serpapi"
                    }
                else:
                    print(f"SerpApi error: {response.status}")
                    return None
    
    async def _async_search_brave(self, query: str, limit: int) -> Optional[Dict[str, Any]]:
        """Async search using Brave Search API."""
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }
        
        params = {
            "q": query,
            "count": limit
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url, headers=headers, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    results = []
                    for result in data.get("web", {}).get("results", [])[:limit]:
                        results.append({
                            "title": result.get("title"),
                            "url": result.get("url"),
                            "snippet": result.get("description"),
                            "source": result.get("url"),
                        })
                    
                    cache_web_search_result(query, results)
                    
                    return {
                        "results": results,
                        "query": query,
                        "from_cache": False,
                        "provider": "brave"
                    }
                else:
                    print(f"Brave API error: {response.status}")
                    return None


# Global search service instance (uses config.SEARCH_PROVIDER)
search_service = MultiSearchService()
