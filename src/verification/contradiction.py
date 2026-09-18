import json
from uuid import UUID
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

        matching_sources = []
        words = [w.lower() for w in claim.claim_text.replace(",", "").replace(".", "").split() if len(w) > 3]
        for s in candidate_sources:
            snippet = s.raw_text_snippet or ""
            if not snippet:
                continue
            match_count = sum(1 for w in words if w in snippet.lower())
            if len(words) == 0 or match_count > 0:
                matching_sources.append(s)

        if not matching_sources:
            return {
                "corroborated": False,
                "corroborating_source": None,
                "contradiction_detected": False,
                "details": "No independent Tier 1 or Tier 2 source contained relevant keyword entities."
            }

        combined_snippets = "\n\n".join(
            [f"Domain: {s.domain}\nURL: {s.url}\nText: {(s.raw_text_snippet or '')[:1000]}" for s in matching_sources[:3]]
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

    def evaluate_check2_batch(
        self, claims: List[Claim], sources: List[EvidenceSource]
    ) -> Dict[UUID, Dict[str, Any]]:
        """
        Check 2 (High-Performance Batch Mode): Evaluates independent corroboration and contradiction detection for all claims in a single LLM call.
        Returns dict mapping claim_id -> {'corroborated': bool, 'corroborating_url': str or None, 'contradiction_detected': bool, 'details': str or None}
        """
        results = {}
        if not claims:
            return results

        candidate_sources = [
            s for s in sources 
            if s.source_tier in [SourceTier.TIER_1_PRIMARY, SourceTier.TIER_2_SECONDARY] 
            and (s.raw_text_snippet or "").strip()
        ]

        if not candidate_sources:
            for c in claims:
                results[c.claim_id] = {
                    "corroborated": False,
                    "corroborating_url": None,
                    "contradiction_detected": False,
                    "details": "No independent Tier 1 or Tier 2 source found for corroboration."
                }
            return results

        passages_text = "\n\n".join([
            f"[Source {idx+1} Domain: {s.domain} | URL: {s.url}]\n{(s.raw_text_snippet or '')[:1500]}"
            for idx, s in enumerate(candidate_sources[:5])
        ])

        claims_text = "\n".join([
            f"[{i+1}] (Primary URL: {c.primary_source_url or 'None'}) {c.claim_text}"
            for i, c in enumerate(claims)
        ])

        prompt = (
            "You are an adversarial fact checker conducting secondary corroboration and contradiction detection.\n"
            "For each of the following claims:\n"
            "1. Does ANY candidate source corroborate this claim (state or confirm that this factual claim is true)? "
            "Set 'corroborated': true and provide 'corroborating_url' with that source URL (if a Primary URL is given, the corroborating source should have an independent domain).\n"
            "2. Does ANY source contradict the claim (e.g. conflicting years, dates, metrics, titles, or numbers)?\n\n"
            f"Candidate Independent Sources:\n{passages_text}\n\n"
            f"Factual Claims to Corroborate:\n{claims_text}\n\n"
            "Return JSON with key 'evaluations', an array where each item corresponds to a claim in order:\n"
            "- 'claim_index': integer (1, 2, ...)\n"
            "- 'corroborated': boolean\n"
            "- 'corroborating_url': string (the exact corroborating source URL, or null)\n"
            "- 'contradiction_detected': boolean\n"
            "- 'contradiction_details': string (or null, under 15 words if detected)"
        )

        try:
            resp = self.client.chat_completion_json(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.0
            )
            evals = resp.get("evaluations", [])
            eval_map = {e.get("claim_index"): e for e in evals if "claim_index" in e}

            for idx, c in enumerate(claims, 1):
                ev = eval_map.get(idx)
                if ev:
                    results[c.claim_id] = {
                        "corroborated": ev.get("corroborated", False),
                        "corroborating_url": ev.get("corroborating_url"),
                        "contradiction_detected": ev.get("contradiction_detected", False),
                        "details": ev.get("contradiction_details")
                    }
                else:
                    results[c.claim_id] = {
                        "corroborated": False,
                        "corroborating_url": None,
                        "contradiction_detected": False,
                        "details": "Corroboration evaluated."
                    }
        except Exception:
            for c in claims:
                p_src = next((s for s in sources if s.url == c.primary_source_url), None)
                results[c.claim_id] = self.evaluate_check2_corroboration(c, sources, p_src)

        return results

