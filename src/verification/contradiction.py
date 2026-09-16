import json
from typing import List, Dict, Any, Optional
from groq import Groq
from src.config import GROQ_API_KEY, GROQ_MODEL
from src.storage.models import Claim, EvidenceSource, SourceTier

class ContradictionDetector:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or GROQ_API_KEY
        self.model = model or GROQ_MODEL
        self.client = Groq(api_key=self.api_key) if self.api_key else None

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
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            result = json.loads(resp.choices[0].message.content)
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
