import httpx
import re
import urllib.parse
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from src.config import TAVILY_API_KEY, USE_LIVE_SEARCH

class SearchClient:
    def __init__(self, tavily_api_key: Optional[str] = None):
        self.api_key = tavily_api_key or TAVILY_API_KEY
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Executes live OSINT web search.
        First tries Tavily if key present; otherwise executes live DuckDuckGo HTML search.
        Raises RuntimeError if live search fails (zero offline mock substitution).
        """
        if not USE_LIVE_SEARCH:
            raise RuntimeError("Live search disabled in configuration. Pure live internet OSINT is required.")

        # Attempt Tavily if API key is provided
        if self.api_key:
            try:
                async with httpx.AsyncClient(timeout=25.0) as client:
                    payload = {
                        "api_key": self.api_key,
                        "query": query,
                        "search_depth": "basic",
                        "include_answer": False,
                        "max_results": max_results
                    }
                    resp = await client.post("https://api.tavily.com/search", json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        results = []
                        for item in data.get("results", []):
                            results.append({
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "snippet": item.get("content", "")
                            })
                        if results:
                            return results
            except Exception:
                pass  # Fallback to live DuckDuckGo HTML search

        # Live DuckDuckGo search fallback
        try:
            return await self._duckduckgo_live_search(query, max_results=max_results)
        except Exception as e:
            raise RuntimeError(f"ERR_LIVE_SEARCH_FAILED: Live OSINT search failed for query '{query}': {str(e)}")

    async def _duckduckgo_live_search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}"
        async with httpx.AsyncClient(timeout=12.0, headers=self.headers, follow_redirects=True) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code} returned by live search gateway.")

            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
            for result in soup.find_all("div", class_=re.compile(r"result\b")):
                title_elem = result.find("a", class_="result__a")
                snippet_elem = result.find("a", class_="result__snippet")
                if not title_elem:
                    continue

                raw_url = title_elem.get("href", "")
                title = title_elem.get_text(strip=True)
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                # Decode DuckDuckGo redirect url if applicable
                actual_url = raw_url
                if "uddg=" in raw_url:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                    if "uddg" in parsed and parsed["uddg"]:
                        actual_url = parsed["uddg"][0]

                if actual_url.startswith("http") and not actual_url.startswith("https://duckduckgo.com"):
                    results.append({
                        "title": title,
                        "url": actual_url,
                        "snippet": snippet
                    })

                if len(results) >= max_results:
                    break

            if not results:
                raise RuntimeError(f"Zero live search results parsed from web response for: {query}")
            return results
