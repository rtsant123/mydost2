"""Web search service for retrieving external information."""
from typing import List, Dict, Any, Optional
import aiohttp
import requests
from utils.config import config
from utils.cache import get_cached_search_results, cache_web_search_result


class SearchService:
    """Service for web search integration."""
    
    def __init__(self, api_key: str = None, api_url: str = None):
        """
        Initialize search service.
        
        Args:
            api_key: API key for search service (e.g., Serper)
            api_url: API endpoint URL
        """
        self.api_key = api_key or config.SEARCH_API_KEY
        self.api_url = api_url or config.SEARCH_API_URL
    
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
            # Using Serper API format
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
                
                # Extract relevant results
                results = []
                for result in data.get("organic", [])[:limit]:
                    results.append({
                        "title": result.get("title"),
                        "url": result.get("link"),
                        "snippet": result.get("snippet"),
                        "source": result.get("source"),
                    })
                
                # Cache results
                cache_web_search_result(query, results)
                
                return {
                    "results": results,
                    "query": query,
                    "from_cache": False,
                }
            else:
                print(f"Search API error: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"Error performing web search: {str(e)}")
            return None
    
    async def async_search(self, query: str, limit: int = 5) -> Optional[Dict[str, Any]]:
        """
        Perform web search (asynchronous).
        
        Args:
            query: Search query
            limit: Number of results to return
        
        Returns:
            Search results
        """
        if not self.api_key:
            return None
        
        # Check cache first
        cached = get_cached_search_results(query)
        if cached:
            return {"results": cached, "from_cache": True}
        
        try:
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
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
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
                        }
                    else:
                        print(f"Search API error: {response.status}")
                        return None
        
        except Exception as e:
            print(f"Error performing async web search: {str(e)}")
            return None
    
    def format_search_results_for_context(self, results: List[Dict[str, str]]) -> str:
        """
        Format search results for use as LLM context.
        
        Args:
            results: List of search results
        
        Returns:
            Formatted string for LLM context
        """
        if not results:
            return ""
        
        formatted = "Web Search Results:\n"
        for i, result in enumerate(results, 1):
            formatted += f"\n[{i}] {result.get('title', 'No title')}\n"
            formatted += f"Source: {result.get('url', 'Unknown')}\n"
            formatted += f"Snippet: {result.get('snippet', 'No snippet available')}\n"
        
        return formatted
    
    def extract_citations(self, results: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Extract citations from search results for display in UI.
        
        Args:
            results: List of search results
        
        Returns:
            List of citations with URLs
        """
        citations = []
        for i, result in enumerate(results, 1):
            citations.append({
                "number": str(i),
                "title": result.get("title", "Unknown"),
                "url": result.get("url", ""),
                "source": result.get("source", "Unknown"),
            })
        
        return citations


# Global search service instance
search_service = SearchService()
