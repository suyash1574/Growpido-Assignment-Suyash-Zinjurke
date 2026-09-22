import json
import re
from uuid import UUID
from typing import List, Dict, Any, Optional
from src.llm_client import llm_client, UnifiedLLMClient
from src.storage.models import Claim, EvidenceSource, SourceTier

def extract_relevant_context(text: str, query: str, max_chars: int = 2500) -> str:
    """
    Extracts the most relevant context window from a source text centered on matching tokens.
    If the text is <= max_chars, returns it in full.
    Otherwise, finds the first occurrence of significant query tokens (>= 4 chars) and extracts a centered window.
    """
    if not text or len(text) <= max_chars:
        return text or ""

    lower_text = text.lower()
    tokens = [t.lower() for t in re.sub(r'[^a-zA-Z0-9\s]', ' ', query).split() if len(t) >= 4]
    
    match_idx = -1
    for t in tokens:
        idx = lower_text.find(t)
        if idx != -1:
            match_idx = idx
            break

    if match_idx == -1:
        return text[:max_chars]

    half = max_chars // 2
    start = max(0, match_idx - half)
    end = min(len(text), start + max_chars)
    if end - start < max_chars:
        start = max(0, end - max_chars)
    return text[start:end]

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
            [f"Domain: {s.domain}\nURL: {s.url}\nText: {extract_relevant_context(s.raw_text_snippet or '', claim.claim_text, max_chars=1800)}" for s in matching_sources[:3]]
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
                max_tokens=600,
                temperature=0.1
            )
            corroborated = result.get("corroborated", False)
            corroborating_url = result.get("corroborating_url")
            details = result.get("contradiction_details")
            
            import urllib.parse
            if corroborated and corroborating_url and primary_source and primary_source.url:
                primary_domain = urllib.parse.urlparse(primary_source.url).netloc.lower().replace("www.", "")
                corr_domain = urllib.parse.urlparse(corroborating_url).netloc.lower().replace("www.", "")
                if primary_domain == corr_domain:
                    corroborated = False
                    corroborating_url = None
                    details = "Corroboration rejected: must be an independent domain."

            return {
                "corroborated": corroborated,
                "corroborating_url": corroborating_url,
                "contradiction_detected": result.get("contradiction_detected", False),
                "details": details
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

        # Build single corroboration context window
        subject_query = claims[0].claim_text if claims else ""
        non_tier1_sources = [s for s in candidate_sources if s.source_tier == SourceTier.TIER_2_SECONDARY] or candidate_sources
        passages_text = "\n\n".join([
            f"[Source URL: {s.url}]\n{extract_relevant_context(s.raw_text_snippet or '', subject_query, max_chars=1000)}"
            for s in non_tier1_sources[:2]
        ])

        import urllib.parse
        chunk_size = 10
        for start_i in range(0, len(claims), chunk_size):
            chunk = claims[start_i:start_i + chunk_size]
            claims_text = "\n".join([
                f"[{i+1}] (Primary URL: {c.primary_source_url or 'None'}) {c.claim_text}"
                for i, c in enumerate(chunk)
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

                for idx, c in enumerate(chunk, 1):
                    ev = eval_map.get(idx)
                    if ev:
                        corroborated = ev.get("corroborated", False)
                        corroborating_url = ev.get("corroborating_url")
                        details = ev.get("contradiction_details")
                        
                        # Programmatically enforce cross-domain corroboration
                        if corroborated and corroborating_url and c.primary_source_url:
                            primary_domain = urllib.parse.urlparse(c.primary_source_url).netloc.lower().replace("www.", "")
                            corr_domain = urllib.parse.urlparse(corroborating_url).netloc.lower().replace("www.", "")
                            if primary_domain == corr_domain:
                                corroborated = False
                                corroborating_url = None
                                details = "Corroboration rejected: must be an independent domain."

                        results[c.claim_id] = {
                            "corroborated": corroborated,
                            "corroborating_url": corroborating_url,
                            "contradiction_detected": ev.get("contradiction_detected", False),
                            "details": details
                        }
                    else:
                        results[c.claim_id] = {
                            "corroborated": False,
                            "corroborating_url": None,
                            "contradiction_detected": False,
                            "details": "Corroboration evaluated."
                        }
            except Exception:
                for c in chunk:
                    p_src = next((s for s in sources if s.url == c.primary_source_url), None)
                    results[c.claim_id] = self.evaluate_check2_corroboration(c, sources, p_src)

        return results

