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

        # Filter Tier-1 sources with token/entity overlap
        matching_sources = []
        words = [w.lower() for w in claim.claim_text.replace(",", "").replace(".", "").split() if len(w) > 3]
        for src in tier1_sources:
            snippet = src.raw_text_snippet or ""
            if not snippet:
                continue
            match_count = sum(1 for w in words if w in snippet.lower())
            if len(words) == 0 or match_count > 0:
                matching_sources.append(src)

        if not matching_sources:
            return {
                "passed": False,
                "primary_source": None,
                "reason": "Tier-1 sources found but none contained relevant keyword entities."
            }

        # Batch candidate Tier-1 passages into a single entailment verification call with centered window
        passages = "\n\n".join([
            f"Source URL: {s.url}\nPassage: {extract_relevant_context(s.raw_text_snippet or '', claim.claim_text, max_chars=2000)}"
            for s in matching_sources[:3]
        ])

        prompt = (
            "You are an adversarial fact verification auditor. "
            "Determine if ANY of the following Tier-1 Source Passages strictly entails the Claim.\n"
            "Note: Treat standard date formats (e.g. '26 May 2014' vs 'May 26, 2014'), honorifics (e.g. 'Shri Narendra Modi' vs 'Narendra Modi'), "
            "and role synonyms ('sworn in as', 'took oath as', 'assumed office as', 'served as') as semantically entailed if they state the same core fact.\n\n"
            f"Claim: \"{claim.claim_text}\"\n\n"
            f"Tier-1 Source Passages:\n{passages}\n\n"
            "Return JSON with keys:\n"
            "- 'entailed': boolean (true if any passage entails the claim, false otherwise)\n"
            "- 'primary_url': string (the exact Source URL that entails the claim, or null)\n"
            "- 'explanation': string"
        )

        try:
            res = self.client.chat_completion_json(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.1
            )
            if res.get("entailed") is True:
                primary_url = res.get("primary_url")
                matched_src = next((s for s in matching_sources if s.url == primary_url), matching_sources[0])
                return {
                    "passed": True,
                    "primary_source": matched_src,
                    "reason": res.get("explanation", "Tier-1 source entails claim.")
                }
        except Exception:
            pass

        return {
            "passed": False,
            "primary_source": None,
            "reason": "Tier-1 sources found but none semantically entailed the claim."
        }

    def evaluate_check1_batch(self, claims: List[Claim], sources: List[EvidenceSource]) -> Dict[UUID, Dict[str, Any]]:
        """
        Check 1 (High-Performance Batch Mode): Evaluates primary source entailment in optimized chunks of up to 10 claims.
        Returns dict mapping claim_id -> {'passed': bool, 'primary_source': EvidenceSource or None, 'reason': str}
        """
        results = {}
        if not claims:
            return results

        tier1_sources = [s for s in sources if s.source_tier == SourceTier.TIER_1_PRIMARY and (s.raw_text_snippet or "").strip()]
        if not tier1_sources:
            for c in claims:
                results[c.claim_id] = {
                    "passed": False,
                    "primary_source": None,
                    "reason": "No Tier-1 primary source exists in evidence set."
                }
            return results

        # Infer subject name from first claim text
        subject_query = claims[0].claim_text if claims else ""
        passages_text = "\n\n".join([
            f"[Source {idx+1} URL: {s.url}]\n{extract_relevant_context(s.raw_text_snippet or '', subject_query, max_chars=1000)}"
            for idx, s in enumerate(tier1_sources[:2])
        ])

        chunk_size = 10
        for start_i in range(0, len(claims), chunk_size):
            chunk = claims[start_i:start_i + chunk_size]
            claims_text = "\n".join([
                f"[{i+1}] {c.claim_text}"
                for i, c in enumerate(chunk)
            ])

            prompt = (
                "You are an adversarial fact verification auditor.\n"
                "Determine if each of the following Factual Claims is strictly entailed by ANY of the provided Tier-1 Primary Source passages.\n"
                "Note: Treat standard date formats, honorifics, and role synonyms as semantically entailed if they state the same core fact.\n\n"
                f"Tier-1 Source Passages:\n{passages_text}\n\n"
                f"Factual Claims to Verify:\n{claims_text}\n\n"
                "Return JSON with key 'evaluations', an array where each item corresponds to a claim in order:\n"
                "- 'claim_index': integer (1, 2, ...)\n"
                "- 'entailed': boolean (true if entailed by any Tier-1 source passage, false otherwise)\n"
                "- 'primary_url': string (the exact Tier-1 Source URL that entailed it, or null)"
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
                    if ev and ev.get("entailed") is True:
                        p_url = ev.get("primary_url")
                        src = next((s for s in tier1_sources if s.url == p_url), tier1_sources[0])
                        results[c.claim_id] = {
                            "passed": True,
                            "primary_source": src,
                            "reason": ev.get("explanation", "Tier-1 source entails claim.")
                        }
                    else:
                        results[c.claim_id] = {
                            "passed": False,
                            "primary_source": None,
                            "reason": ev.get("explanation", "Tier-1 sources found but none semantically entailed the claim.") if ev else "Not entailed."
                        }
            except Exception:
                for c in chunk:
                    results[c.claim_id] = self.evaluate_check1_primary(c, sources)

        return results

