"""News aggregation and summarization service."""
from typing import List, Dict, Any, Optional
import aiohttp
import requests
from utils.config import config
from utils.cache import cache_news, get_cached_news


class NewsService:
    """Service for fetching and summarizing news."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize news service.
        
        Args:
            api_key: NewsAPI key
        """
        self.api_key = api_key or config.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
    
    def get_top_headlines(
        self,
        category: Optional[str] = None,
        country: str = "us",
        limit: int = 5
    ) -> Optional[Dict[str, Any]]:
        """
        Get top headlines.
        
        Args:
            category: News category (business, technology, sports, etc.)
            country: ISO country code
            limit: Number of articles
        
        Returns:
            List of headline articles
        """
        if not self.api_key:
            return None
        
        # Check cache
        cache_key = f"{country}_{category}_{limit}"
        cached = get_cached_news(cache_key)
        if cached:
            return {"articles": cached, "from_cache": True}
        
        try:
            params = {
                "apiKey": self.api_key,
                "country": country,
                "pageSize": limit,
            }
            
            if category:
                params["category"] = category
            
            response = requests.get(
                f"{self.base_url}/top-headlines",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                
                # Extract relevant fields
                headlines = []
                for article in articles[:limit]:
                    headlines.append({
                        "title": article.get("title"),
                        "description": article.get("description"),
                        "url": article.get("url"),
                        "image": article.get("urlToImage"),
                        "source": article.get("source", {}).get("name"),
                        "published_at": article.get("publishedAt"),
                    })
                
                cache_news(cache_key, headlines)
                
                return {
                    "articles": headlines,
                    "total_results": data.get("totalResults"),
                    "from_cache": False,
                }
            else:
                print(f"NewsAPI error: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
            return None
    
    def get_categories(self) -> List[str]:
        """Get available news categories."""
        return [
            "business",
            "entertainment",
            "general",
            "health",
            "science",
            "sports",
            "technology",
        ]


# Global news service instance
news_service = NewsService()
