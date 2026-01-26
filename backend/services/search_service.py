"""Multi-provider web search service supporting Serper, SerpApi, Brave, and DuckDuckGo."""
from typing import List, Dict, Any, Optional
import aiohttp
import requests
from utils.config import config
from utils.cache import get_cached_search_results, cache_web_search_result
from services.duckduckgo_search import duckduckgo_search


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
    
    def search(self, query: str, limit: int = 5, ttl: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Perform web search (synchronous).
        Priority: Cache → Paid API (SerpAPI/Serper) → DuckDuckGo (fallback)
        
        Args:
            query: Search query
            limit: Number of results to return
        
        Returns:
            Search results with snippets and source URLs
        """
        # Check cache first
        cached = get_cached_search_results(query)
        if cached:
            return {"results": cached, "from_cache": True, "provider": "cache"}
        
        # Try paid API first if configured (SerpAPI or Serper)
        if self.api_key:
            try:
                print(f"🔍 Using paid API: {self.provider} for: {query}")
                if self.provider == "serper":
                    result = self._search_serper(query, limit, ttl)
                elif self.provider == "serpapi":
                    result = self._search_serpapi(query, limit, ttl)
                elif self.provider == "brave":
                    result = self._search_brave(query, limit, ttl)
                
                if result and result.get('results'):
                    print(f"✅ {self.provider} returned {len(result['results'])} results")
                    # Cache the results
                    cache_web_search_result(query, result['results'], ttl or config.WEB_SEARCH_CACHE_TTL)
                    return result
            except Exception as e:
                print(f"❌ {self.provider} API error: {str(e)}, falling back to DuckDuckGo")
        
        # Fallback to DuckDuckGo (FREE, no API key needed)
        print(f"🦆 Using DuckDuckGo fallback search for: {query}")
        ddg_results = duckduckgo_search.search(query, limit)
        if ddg_results and ddg_results.get('results'):
            print(f"✅ DuckDuckGo returned {len(ddg_results['results'])} results")
            # Cache the results
            cache_web_search_result(query, ddg_results['results'], ttl or config.WEB_SEARCH_CACHE_TTL)
            return ddg_results
        
        print("⚠️ No search results from any provider")
        return {"results": [], "provider": "none"}
    
    def _search_serper(self, query: str, limit: int, ttl: Optional[int] = None) -> Optional[Dict[str, Any]]:
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
            timeout=5  # Reduced from 10 to 5 seconds
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
            
            cache_web_search_result(query, results, ttl or config.WEB_SEARCH_CACHE_TTL)
            
            return {
                "results": results,
                "query": query,
                "from_cache": False,
                "provider": "serper"
            }
        else:
            print(f"Serper API error: {response.status_code}")
            return None
    
    def _search_serpapi(self, query: str, limit: int, ttl: Optional[int] = None) -> Optional[Dict[str, Any]]:
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
            
            cache_web_search_result(query, results, ttl or config.WEB_SEARCH_CACHE_TTL)
            
            return {
                "results": results,
                "query": query,
                "from_cache": False,
                "provider": "serpapi"
            }
        else:
            print(f"SerpApi error: {response.status_code}")
            return None
    
    def _search_brave(self, query: str, limit: int, ttl: Optional[int] = None) -> Optional[Dict[str, Any]]:
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
            
            cache_web_search_result(query, results, ttl or config.WEB_SEARCH_CACHE_TTL)
            
            return {
                "results": results,
                "query": query,
                "from_cache": False,
                "provider": "brave"
            }
        else:
            print(f"Brave API error: {response.status_code}")
            return None
    
    async def async_search(self, query: str, limit: int = 5, ttl: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Perform web search (asynchronous).
        
        Args:
            query: Search query
            limit: Number of results to return
        
        Returns:
            Search results with snippets and source URLs
        """
        # If no paid API key is configured, fall back to DuckDuckGo (free) so search still works
        if not self.api_key:
            try:
                # Use thread to avoid blocking event loop
                import asyncio
                loop = asyncio.get_running_loop()
                ddg_results = await loop.run_in_executor(None, lambda: duckduckgo_search.search(query, limit))
                if ddg_results and ddg_results.get("results"):
                    cache_web_search_result(query, ddg_results["results"], ttl or config.WEB_SEARCH_CACHE_TTL)
                    return ddg_results
            except Exception as e:
                print(f"DuckDuckGo fallback error: {e}")
            return None
        
        # Check cache first
        cached = get_cached_search_results(query)
        if cached:
            return {"results": cached, "from_cache": True}
        
        try:
            if self.provider == "serper":
                return await self._async_search_serper(query, limit, ttl)
            elif self.provider == "serpapi":
                return await self._async_search_serpapi(query, limit, ttl)
            elif self.provider == "brave":
                return await self._async_search_brave(query, limit, ttl)
        
        except Exception as e:
            print(f"Error performing async web search: {str(e)}")
            try:
                import asyncio
                loop = asyncio.get_running_loop()
                ddg_results = await loop.run_in_executor(None, lambda: duckduckgo_search.search(query, limit))
                if ddg_results and ddg_results.get("results"):
                    cache_web_search_result(query, ddg_results["results"])
                    return ddg_results
            except Exception as fallback_error:
                print(f"DuckDuckGo fallback error: {fallback_error}")
            return None
    
    async def _async_search_serper(self, query: str, limit: int, ttl: Optional[int] = None) -> Optional[Dict[str, Any]]:
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
                    
                    cache_web_search_result(query, results, ttl or config.WEB_SEARCH_CACHE_TTL)
                    
                    return {
                        "results": results,
                        "query": query,
                        "from_cache": False,
                        "provider": "serper"
                    }
                else:
                    print(f"Serper API error: {response.status}")
                    return None
    
    async def _async_search_serpapi(self, query: str, limit: int, ttl: Optional[int] = None) -> Optional[Dict[str, Any]]:
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
                    
                    cache_web_search_result(query, results, ttl or config.WEB_SEARCH_CACHE_TTL)
                    
                    return {
                        "results": results,
                        "query": query,
                        "from_cache": False,
                        "provider": "serpapi"
                    }
                else:
                    print(f"SerpApi error: {response.status}")
                    return None
    
    async def _async_search_brave(self, query: str, limit: int, ttl: Optional[int] = None) -> Optional[Dict[str, Any]]:
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
                    
                    cache_web_search_result(query, results, ttl or config.WEB_SEARCH_CACHE_TTL)
                    
                    return {
                        "results": results,
                        "query": query,
                        "from_cache": False,
                        "provider": "brave"
                    }
                else:
                    print(f"Brave API error: {response.status}")
                    return None
    
    def format_search_results_for_context(self, results: List[Dict[str, Any]]) -> str:
        """Format search results into context for AI with numbered citations."""
        if not results:
            return ""
        
        context = "🌐 WEB SEARCH RESULTS:\n\n"
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            snippet = result.get('snippet', 'No description')
            url = result.get('url', '')
            source_domain = result.get('source', url)
            
            # Clean snippet
            snippet = snippet.replace('\n', ' ').strip()
            
            # Add numbered citation
            context += f"[{i}] {title}\n"
            context += f"   Source: {source_domain}\n"
            context += f"   {snippet}\n\n"
        
        context += "\n📌 IMPORTANT: When using information from these sources, cite them using [1], [2], etc. in your response.\n"
        context += "Format citations like: 'According to [1], ...' or 'Recent reports show [2] that...'\n"
        
        return context
    
    def extract_citations(self, results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract citation information from search results for frontend display."""
        citations = []
        from datetime import datetime
        fetched_at = datetime.utcnow().isoformat() + "Z"
        for i, result in enumerate(results, 1):
            citations.append({
                "number": str(i),
                "title": result.get('title', 'Untitled'),
                "url": result.get('url', ''),
                "source": result.get('source', result.get('url', 'Unknown')),
                "fetched_at": fetched_at
            })
        return citations


# Global search service instance (uses config.SEARCH_PROVIDER)
search_service = MultiSearchService()
