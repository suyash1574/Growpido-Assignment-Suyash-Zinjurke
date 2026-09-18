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

        # Extract location hints from snippet or URL
        location = None
        loc_match = re.search(r"(?:in|based in|located in|from)\s+([A-Z][a-zA-Z\s]+(?:,\s*[A-Z][a-zA-Z\s]+)?)", snippet)
        if loc_match:
            location = loc_match.group(1).strip(" .")
        elif "ae.linkedin.com" in raw_url:
            location = "United Arab Emirates"

        # Evaluate Track B Compliance: UAE-based founder, CEO, or fund manager
        combined_context = f"{raw_url} {title} {headline} {location or ''} {snippet}".lower()
        uae_indicators = ["ae.linkedin.com", "uae", "united arab emirates", "dubai", "abu dhabi", "sharjah", "difc", "adgm", "mena"]
        exec_indicators = [
            "founder", "co-founder", "cofounder", "ceo", "chief executive",
            "managing partner", "general partner", "fund manager", "managing director",
            "vice president", "president", "partner", "investor", "venture capital", "private equity"
        ]

        has_uae = any(k in combined_context for k in uae_indicators)
        has_exec = any(k in combined_context for k in exec_indicators)

        # Clear disqualifiers (e.g. political leaders or foreign state heads)
        disqualifiers = ["prime minister", "president of india", "lok sabha", "parliament of india", "congressman", "senator"]
        is_disqualified = any(d in combined_context for d in disqualifiers)

        if is_disqualified or not has_uae or not has_exec:
            reasons = []
            if is_disqualified:
                reasons.append("Political/public governance role outside Track B commercial scope")
            if not has_uae:
                reasons.append("Location outside UAE / MENA jurisdiction")
            if not has_exec:
                reasons.append("Role does not match Founder, CEO, or Fund Manager profile")
            track_b_compliant = False
            compliance_notes = f"Track B Scope Warning: {'; '.join(reasons)}"
        else:
            track_b_compliant = True
            compliance_notes = "Track B Compliant: Verified UAE-based Founder, CEO, or Fund Manager"

        return CandidateMatch(
            full_name=full_name,
            headline=headline or "Executive Profile",
            current_company=current_company,
            location=location,
            linkedin_url=canonical_url,
            snippet=snippet,
            track_b_compliant=track_b_compliant,
            compliance_notes=compliance_notes
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
        clean_name = name.strip()
        queries_to_try = []
        if context_keywords and context_keywords.strip():
            queries_to_try.append(f'site:linkedin.com/in/ "{clean_name}" {context_keywords.strip()}')
            queries_to_try.append(f'site:linkedin.com/in/ "{clean_name}"')
            queries_to_try.append(f'"{clean_name}" linkedin profile {context_keywords.strip()}')
        else:
            queries_to_try.append(f'site:linkedin.com/in/ "{clean_name}"')
            queries_to_try.append(f'"{clean_name}" linkedin profile')

        candidates: List[CandidateMatch] = []
        seen_urls = set()

        for q in queries_to_try:
            try:
                raw_results = await self.search_client.search(q, max_results=limit + 3)
            except Exception:
                raw_results = []

            for item in raw_results:
                cand = self._parse_candidate_result(
                    title=item.get("title", ""),
                    raw_url=item.get("url", ""),
                    snippet=item.get("snippet", "")
                )
                if cand and cand.linkedin_url not in seen_urls:
                    # Filter out candidates with garbage names (e.g. '. .' or single characters)
                    clean_alpha = re.sub(r'[^a-zA-Z]', '', cand.full_name)
                    if len(clean_alpha) < 2:
                        continue
                    seen_urls.add(cand.linkedin_url)
                    candidates.append(cand)

            if candidates:
                break

        # Rank candidates by relevance: name tokens match first, then Track B compliance
        name_tokens = [t.lower() for t in clean_name.split() if len(t) > 1]
        def _candidate_rank(c: CandidateMatch) -> int:
            matches = sum(1 for t in name_tokens if t in c.full_name.lower() or t in c.linkedin_url.lower())
            score = 0
            if matches == len(name_tokens):
                score -= 100
            elif matches > 0:
                score -= 50
            if c.track_b_compliant:
                score -= 10
            return score

        candidates.sort(key=_candidate_rank)
        return candidates[:limit]
