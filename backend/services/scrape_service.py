"""Lightweight web page fetch + clean text extraction with caching."""
from typing import Optional, Dict, Any
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import random

from utils.cache import get_cached_page_content, cache_page_content
from utils.config import config


class ScrapeService:
    """Fetch HTML pages, strip boilerplate, and cache cleaned text."""

    def __init__(self, timeout: int = 12):
        self.timeout = timeout

    async def fetch_and_parse(self, url: str, ttl_seconds: int = 21600) -> Optional[Dict[str, Any]]:
        """Fetch a URL, clean to text, cache, and return structured dict."""
        if not url:
            return None

        cached = get_cached_page_content(url)
        if cached:
            return cached

        html = None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=self.timeout, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                    if resp.status != 200:
                        return None
                    html = await resp.text()
        except Exception as e:
            print(f"Scrape error for {url}: {e}")

        # Optional JS render (Playwright) for tough pages, limited by JS_RENDER_PERCENT
        if (not html or len(html) < 800) and config.PLAYWRIGHT_ENABLED:
            if random.randint(1, 100) <= config.JS_RENDER_PERCENT:
                rendered = await self._render_with_playwright(url)
                if rendered:
                    html = rendered
        
        if not html:
            return None

        try:
            soup = BeautifulSoup(html, "html.parser")
            # Remove scripts/styles
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            title = (soup.title.string.strip() if soup.title and soup.title.string else "")[:200]
            text = " ".join(soup.stripped_strings)
            # Trim very long pages to keep prompts lean
            text = text[:20000]

            result = {
                "url": url,
                "title": title,
                "text": text,
                "fetched_at": datetime.utcnow().isoformat() + "Z",
            }
            cache_page_content(url, result, ttl=ttl_seconds)
            return result
        except Exception as e:
            print(f"Parse error for {url}: {e}")
            return None

    async def _render_with_playwright(self, url: str) -> Optional[str]:
        """Render page with Playwright if available."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return None

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle", timeout=config.PLAYWRIGHT_TIMEOUT * 1000)
                content = await page.content()
                await browser.close()
                return content
        except Exception as e:
            print(f"Playwright render failed for {url}: {e}")
            return None


scrape_service = ScrapeService()
