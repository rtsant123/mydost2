"""DuckDuckGo search service - FREE alternative to paid APIs."""
import requests
from typing import List, Dict, Optional
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote


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
                
                # If no results, try lightweight HTML scraping
                if not results:
                    html_fallback = self._web_search(query, limit)
                    if html_fallback:
                        return html_fallback
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

    def _web_search(self, query: str, limit: int) -> Optional[Dict]:
        """Fallback to HTML scraping; extracts real article links (not search-engine URLs)."""
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            resp = requests.get(
                search_url,
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            if resp.status_code != 200:
                return None

            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
            for a in soup.select('a.result__a'):
                href = a.get('href', '')
                # DuckDuckGo uses redirect links like /l/?uddg=<url>
                if '/l/?uddg=' in href:
                    parsed = urlparse(href)
                    uddg = parse_qs(parsed.query).get('uddg', [''])[0]
                    real_url = unquote(uddg)
                else:
                    real_url = href

                host = urlparse(real_url).hostname or ""
                # Skip search-engine domains
                if any(engine in host for engine in ["duckduckgo.com", "google.", "bing.", "yahoo."]):
                    continue

                title = a.get_text(strip=True)
                if not real_url or not title:
                    continue

                results.append({
                    "title": title,
                    "url": real_url,
                    "snippet": title,
                    "source": host,
                })
                if len(results) >= limit:
                    break

            if not results:
                return None

            return {
                "results": results,
                "query": query,
                "from_cache": False,
                "provider": "duckduckgo_html"
            }
        except Exception as e:
            print(f"DuckDuckGo web search error: {e}")
            return None


# Singleton instance
duckduckgo_search = DuckDuckGoSearch()
