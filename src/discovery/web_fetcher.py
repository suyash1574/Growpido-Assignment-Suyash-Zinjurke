import httpx
import hashlib
import re
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup

class WebFetcher:
    def __init__(self, timeout_seconds: float = 8.0, user_agent: str = "Growpido-Intelligence-Engine/1.0 (OSINT Research; Passive-Index)"):
        self.timeout = timeout_seconds
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    async def fetch_and_clean(self, url: str) -> Dict[str, Any]:
        """
        Fetches web page asynchronously, strips markup/scripts, and computes SHA-256 hash.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, headers=self.headers) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    return {
                        "url": url,
                        "status_code": resp.status_code,
                        "text": "",
                        "content_hash": hashlib.sha256(b"").hexdigest(),
                        "error": f"HTTP {resp.status_code}"
                    }
                
                html = resp.text
                soup = BeautifulSoup(html, "html.parser")
                
                # Remove unwanted script, style, and navigation noise
                for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                    tag.decompose()
                    
                raw_text = soup.get_text(separator=" ", strip=True)
                cleaned_text = re.sub(r"\s+", " ", raw_text).strip()
                
                # Truncate to reasonable context window for OSINT snippet analysis (max 50,000 chars)
                truncated_text = cleaned_text[:50000]
                content_hash = hashlib.sha256(truncated_text.encode("utf-8")).hexdigest()
                
                return {
                    "url": url,
                    "status_code": resp.status_code,
                    "text": truncated_text,
                    "content_hash": content_hash,
                    "error": None
                }
        except Exception as e:
            return {
                "url": url,
                "status_code": 0,
                "text": "",
                "content_hash": hashlib.sha256(b"").hexdigest(),
                "error": str(e)
            }
