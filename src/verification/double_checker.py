import json
from typing import List, Dict, Any, Optional
from src.llm_client import llm_client, UnifiedLLMClient
from src.storage.models import Claim, EvidenceSource, SourceTier

class DoubleChecker:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        if api_key or model:
            self.client = UnifiedLLMClient(groq_api_key=api_key, groq_model=model)
        else:
            self.client = llm_client

    def evaluate_check1_primary(self, claim: Claim, sources: List[EvidenceSource]) -> Dict[str, Any]:
        """
        Check 1: Checks if any Tier-1 Primary source explicitly entails the claim.
        Returns {'passed': bool, 'primary_source': EvidenceSource or None, 'reason': str}
        """
        tier1_sources = [s for s in sources if s.source_tier == SourceTier.TIER_1_PRIMARY]
        if not tier1_sources:
            return {
                "passed": False,
                "primary_source": None,
                "reason": "No Tier-1 primary source exists in evidence set."
            }

        # Evaluate entailment against Tier 1 sources
        for src in tier1_sources:
            snippet = src.raw_text_snippet or ""
            if not snippet:
                continue

            # Quick token/string check first (relaxed to check for key entities)
            words = [w.lower() for w in claim.claim_text.replace(",", "").replace(".", "").split() if len(w) > 3]
            match_count = sum(1 for w in words if w in snippet.lower())
            if len(words) > 0 and match_count == 0:
                continue

            prompt = (
                "You are an adversarial fact verification auditor. "
                "Determine if the Source Passage strictly entails the Claim.\n"
                "Note: Treat standard date formats (e.g. '26 May 2014' vs 'May 26, 2014'), honorifics (e.g. 'Shri Narendra Modi' vs 'Narendra Modi'), "
                "and role synonyms ('sworn in as', 'took oath as', 'assumed office as', 'served as') as semantically entailed if they state the same core fact.\n\n"
                f"Claim: \"{claim.claim_text}\"\n"
                f"Source URL: {src.url}\n"
                f"Source Snippet: {snippet[:2000]}\n\n"
                "Return JSON with keys: 'entailed' (true/false) and 'explanation'."
            )

            try:
                res = self.client.chat_completion_json(
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.0
                )
                if res.get("entailed") is True:
                    return {
                        "passed": True,
                        "primary_source": src,
                        "reason": res.get("explanation", "Tier-1 source entails claim.")
                    }
            except Exception:
                continue

        return {
            "passed": False,
            "primary_source": None,
            "reason": "Tier-1 sources found but none semantically entailed the claim."
        }
