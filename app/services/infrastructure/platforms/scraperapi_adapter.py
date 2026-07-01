from __future__ import annotations

import httpx
from urllib.parse import urlencode

from app.core.config import get_settings
from app.services.infrastructure.platforms.base import PlatformAdapter
from app.services.infrastructure.platforms.models import UnifiedPost

# Fallback adapter to use ScraperAPI proxy
class ScraperApiAdapter(PlatformAdapter):
    def __init__(self, platform: str):
        self.platform = platform
        self._api_key = get_settings().scraperapi_key

    async def search(self, keyword: str, limit: int = 10, **kwargs) -> list[UnifiedPost]:
        if not self._api_key:
            return []
            
        # Simplified implementation for fallback logic. 
        # In reality, this would hit http://api.scraperapi.com?api_key=...&url=...
        
        # ScraperAPI acts as a proxy for DuckDuckGo
        url = "https://html.duckduckgo.com/html/"
        params = {
            "q": f"{keyword} site:{self.platform}.com",
        }
        
        proxy_params = {
            "api_key": self._api_key,
            "url": f"{url}?{urlencode(params)}",
            "render": "true"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get("http://api.scraperapi.com/", params=proxy_params)
                response.raise_for_status()
                # Dummy parse: ScraperAPI returns raw HTML of DuckDuckGo, would normally parse using bs4
                return []
            except httpx.HTTPError:
                return []
