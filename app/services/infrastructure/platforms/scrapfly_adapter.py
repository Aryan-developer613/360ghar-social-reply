from __future__ import annotations

import httpx
from urllib.parse import urlencode

from app.core.config import get_settings
from app.services.infrastructure.platforms.base import PlatformAdapter
from app.services.infrastructure.platforms.models import UnifiedPost

# Fallback adapter to use Scrapfly proxy for Twitter/X
class ScrapFlyAdapter(PlatformAdapter):
    def __init__(self, platform: str):
        self.platform = platform
        self._api_key = get_settings().scrapfly_key

    async def search(self, keyword: str, limit: int = 10, **kwargs) -> list[UnifiedPost]:
        if not self._api_key or self.platform not in ["twitter", "x"]:
            return []
            
        # Target specific URL based on keyword
        target_url = f"https://x.com/search?q={keyword}"
        
        proxy_params = {
            "key": self._api_key,
            "url": target_url,
            "asp": "true", # Anti-Scraping Protection
            "render_js": "true"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get("https://api.scrapfly.io/scrape", params=proxy_params)
                response.raise_for_status()
                # Dummy parse: Scrapfly returns JSON payload containing raw HTML
                return []
            except httpx.HTTPError:
                return []
