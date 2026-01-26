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
                
                # If no results, bail (avoid returning search-engine URL)
                if not results:
                    return None
                
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


# Singleton instance
duckduckgo_search = DuckDuckGoSearch()
