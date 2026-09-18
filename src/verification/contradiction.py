import json
from typing import List, Dict, Any, Optional
from src.llm_client import llm_client, UnifiedLLMClient
from src.storage.models import Claim, EvidenceSource, SourceTier

class ContradictionDetector:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        if api_key or model:
            self.client = UnifiedLLMClient(groq_api_key=api_key, groq_model=model)
        else:
            self.client = llm_client

    def evaluate_check2_corroboration(
        self, claim: Claim, sources: List[EvidenceSource], primary_source: Optional[EvidenceSource]
    ) -> Dict[str, Any]:
        """
        Check 2:
        1. Confirms independent source corroboration (domain != primary domain).
        2. Detects any contradictory assertions (differing dates, amounts, or roles).
        """
        primary_domain = primary_source.domain if primary_source else ""
        candidate_sources = [s for s in sources if s.domain != primary_domain and s.source_tier in [SourceTier.TIER_1_PRIMARY, SourceTier.TIER_2_SECONDARY]]

        if not candidate_sources:
            return {
                "corroborated": False,
                "corroborating_source": None,
                "contradiction_detected": False,
                "details": "No independent Tier 1 or Tier 2 source found for corroboration."
            }

        if not self.client:
            return {
                "corroborated": False,
                "corroborating_source": None,
                "contradiction_detected": False,
                "details": "LLM unavailable."
            }

        combined_snippets = "\n\n".join(
            [f"Domain: {s.domain}\nURL: {s.url}\nText: {(s.raw_text_snippet or '')[:1000]}" for s in candidate_sources[:4]]
        )

        prompt = (
            "You are an adversarial fact checker conducting a secondary corroboration check.\n\n"
            f"Factual Claim: \"{claim.claim_text}\"\n\n"
            f"Independent Sources:\n{combined_snippets}\n\n"
            "Task:\n"
            "1. Does any independent source corroborate this claim?\n"
            "2. Does ANY source contradict this claim (e.g. conflicting years, dates, metrics, titles)?\n\n"
            "Return JSON with keys:\n"
            "- 'corroborated': boolean\n"
            "- 'corroborating_url': string (or null)\n"
            "- 'contradiction_detected': boolean\n"
            "- 'contradiction_details': string (or null)"
        )

        try:
            result = self.client.chat_completion_json(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.0
            )
            return {
                "corroborated": result.get("corroborated", False),
                "corroborating_url": result.get("corroborating_url"),
                "contradiction_detected": result.get("contradiction_detected", False),
                "details": result.get("contradiction_details")
            }
        except Exception as e:
            return {
                "corroborated": False,
                "corroborating_source": None,
                "contradiction_detected": False,
                "details": f"Error during contradiction evaluation: {str(e)}"
            }
