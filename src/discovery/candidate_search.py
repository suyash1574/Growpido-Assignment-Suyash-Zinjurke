import re
import urllib.parse
from typing import List, Dict, Any, Optional
from src.discovery.search_client import SearchClient
from src.storage.models import CandidateMatch

class CandidateSearchEngine:
    """
    Performs public OSINT discovery to resolve an executive name into candidate LinkedIn profiles
    for the Sovereign Human Candidate Confirmation Gate.
    """

    def __init__(self, search_client: Optional[SearchClient] = None, use_live_search: bool = True):
        self.search_client = search_client or SearchClient()
        self.use_live_search = use_live_search

    def build_search_query(self, name: str, context_keywords: Optional[str] = None) -> str:
        clean_name = name.strip()
        keywords = f" {context_keywords.strip()}" if context_keywords and context_keywords.strip() else ""
        return f'site:linkedin.com/in/ "{clean_name}"{keywords}'

    def _canonicalize_linkedin_url(self, raw_url: str) -> Optional[str]:
        if "linkedin.com/in/" not in raw_url:
            return None
        # Extract path slug
        match = re.search(r"linkedin\.com/in/([^/?#&]+)", raw_url)
        if match:
            slug = match.group(1).rstrip("/")
            return f"https://www.linkedin.com/in/{slug}"
        return None

    def _parse_candidate_result(self, title: str, raw_url: str, snippet: str) -> Optional[CandidateMatch]:
        canonical_url = self._canonicalize_linkedin_url(raw_url)
        if not canonical_url:
            return None

        # Clean title
        # e.g., "Ronaldo Mouchawar - Vice President - Amazon | LinkedIn"
        # or "Narendra Modi - Prime Minister of India | LinkedIn"
        cleaned_title = re.sub(r"\s*\|\s*LinkedIn.*$", "", title, flags=re.IGNORECASE).strip()
        cleaned_title = re.sub(r"\s*-\s*LinkedIn.*$", "", cleaned_title, flags=re.IGNORECASE).strip()

        parts = [p.strip() for p in re.split(r"\s*[-–—|]\s*", cleaned_title) if p.strip()]
        full_name = parts[0] if parts else "Executive Candidate"
        headline = " - ".join(parts[1:]) if len(parts) > 1 else snippet[:120]

        # Extract company from headline or snippet if possible
        current_company = None
        if " at " in headline:
            current_company = headline.split(" at ")[-1].strip()
        elif parts and len(parts) >= 3:
            current_company = parts[-1]

        # Extract location hints from snippet
        location = None
        loc_match = re.search(r"(?:in|based in|located in|from)\s+([A-Z][a-zA-Z\s]+(?:,\s*[A-Z][a-zA-Z\s]+)?)", snippet)
        if loc_match:
            location = loc_match.group(1).strip(" .")

        return CandidateMatch(
            full_name=full_name,
            headline=headline or "Executive Profile",
            current_company=current_company,
            location=location,
            linkedin_url=canonical_url,
            snippet=snippet
        )

    async def search_candidates(
        self,
        name: str,
        context_keywords: Optional[str] = None,
        max_results: int = 5,
        max_candidates: Optional[int] = None
    ) -> List[CandidateMatch]:
        if not name or not name.strip():
            return []

        limit = max_candidates if max_candidates is not None else max_results
        query = self.build_search_query(name, context_keywords)
        try:
            raw_results = await self.search_client.search(query, max_results=limit + 3)
        except Exception as e:
            # Fallback query without quotes if strict quote query yielded zero results or failed
            fallback_query = f"site:linkedin.com/in/ {name.strip()} {context_keywords or ''}".strip()
            try:
                raw_results = await self.search_client.search(fallback_query, max_results=limit + 3)
            except Exception:
                raw_results = []

        candidates: List[CandidateMatch] = []
        seen_urls = set()

        for item in raw_results:
            cand = self._parse_candidate_result(
                title=item.get("title", ""),
                raw_url=item.get("url", ""),
                snippet=item.get("snippet", "")
            )
            if cand and cand.linkedin_url not in seen_urls:
                seen_urls.add(cand.linkedin_url)
                candidates.append(cand)

        return candidates[:max_results]
