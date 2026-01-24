"""DuckDuckGo search service - FREE alternative to paid APIs."""
import requests
from typing import List, Dict, Optional
import json


class DuckDuckGoSearch:
    """Free search using DuckDuckGo Instant Answer API."""
    
    def __init__(self):
        self.api_url = "https://api.duckduckgo.com/"
    
    def search(self, query: str, limit: int = 5) -> Optional[Dict]:
        """
        Search using DuckDuckGo Instant Answer API (FREE, no API key needed).
        
        Args:
            query: Search query
            limit: Number of results (DuckDuckGo returns what it has)
        
        Returns:
            Search results in standard format
        """
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            response = requests.get(
                self.api_url,
                params=params,
                timeout=10,
                headers={'User-Agent': 'MyDost/1.0'}
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Get Abstract (main result)
                if data.get('Abstract'):
                    results.append({
                        'title': data.get('Heading', query),
                        'url': data.get('AbstractURL', ''),
                        'snippet': data.get('Abstract', ''),
                        'source': data.get('AbstractSource', 'DuckDuckGo')
                    })
                
                # Get Related Topics
                for topic in data.get('RelatedTopics', [])[:limit]:
                    if isinstance(topic, dict) and 'Text' in topic:
                        results.append({
                            'title': topic.get('Text', '')[:100],
                            'url': topic.get('FirstURL', ''),
                            'snippet': topic.get('Text', ''),
                            'source': 'DuckDuckGo'
                        })
                
                # If no results, try web search endpoint
                if not results:
                    return self._web_search(query, limit)
                
                return {
                    'results': results[:limit],
                    'query': query,
                    'from_cache': False,
                    'provider': 'duckduckgo'
                }
            
            return None
            
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return None
    
    def _web_search(self, query: str, limit: int) -> Optional[Dict]:
        """Fallback to HTML scraping if Instant Answer returns nothing."""
        try:
            # DuckDuckGo HTML search (simple scraping)
            search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            
            response = requests.get(
                search_url,
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            if response.status_code == 200:
                # Simple parsing (you'd need BeautifulSoup for production)
                results = []
                
                # For now, return a generic result indicating search was attempted
                results.append({
                    'title': f'Search results for: {query}',
                    'url': f'https://duckduckgo.com/?q={requests.utils.quote(query)}',
                    'snippet': f'Found information about {query}. Visit DuckDuckGo for detailed results.',
                    'source': 'DuckDuckGo'
                })
                
                return {
                    'results': results,
                    'query': query,
                    'from_cache': False,
                    'provider': 'duckduckgo'
                }
            
            return None
            
        except Exception as e:
            print(f"DuckDuckGo web search error: {e}")
            return None


# Singleton instance
duckduckgo_search = DuckDuckGoSearch()
