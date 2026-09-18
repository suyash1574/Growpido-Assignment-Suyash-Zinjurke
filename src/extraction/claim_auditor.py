import json
from uuid import UUID
from typing import List, Dict, Any, Optional
from src.llm_client import llm_client, UnifiedLLMClient
from src.storage.models import Claim, ClaimCategory
from src.extraction.materiality import MaterialityScorer

class ClaimAuditor:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        if api_key or model:
            self.client = UnifiedLLMClient(groq_api_key=api_key, groq_model=model)
        else:
            self.client = llm_client

    def extract_claims(self, prospect_id: UUID, candidate_name: str, discovered_texts: List[str]) -> List[Claim]:
        """
        Decomposes unstructured OSINT text into isolated atomic factual claims using Groq with NVIDIA failover.
        """
        name_parts = [p.lower() for p in candidate_name.split() if len(p) > 2]
        # Prioritize texts that explicitly mention the candidate
        relevant_texts = []
        other_texts = []
        for t in discovered_texts:
            t_lower = t.lower()
            if any(part in t_lower for part in name_parts):
                relevant_texts.append(t)
            else:
                other_texts.append(t)

        ordered_texts = relevant_texts if relevant_texts else other_texts
        combined_text = "\n---\n".join(ordered_texts[:8])[:12000]

        system_prompt = (
            "You are an adversarial forensic Claim Auditor for an executive fact-checking engine. "
            f"Your job is to extract discrete, atomic factual claims about the executive prospect: {candidate_name}.\n\n"
            "RULES:\n"
            "1. Each claim must be a single, self-contained atomic proposition with exactly one predicate.\n"
            "2. Split multi-fact sentences into separate claims.\n"
            "3. Categorize each claim into: ROLE_TENURE, FUNDING_FINANCIAL, EDUCATION_CREDENTIAL, ACCOLADE_AWARD, GOVERNANCE_BOARD, or THOUGHT_LEADERSHIP.\n"
            "4. Return a JSON object with key 'claims', where each item has 'claim_text' and 'category'.\n"
            "5. Do NOT include opinions or vague PR slogans."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Extract atomic claims for {candidate_name} from this public text:\n\n{combined_text}"}
        ]

        data = self.client.chat_completion_json(messages=messages, max_tokens=3000, temperature=0.1)
        extracted = data.get("claims", [])

        claims = []
        for item in extracted:
            cat_str = item.get("category", "ROLE_TENURE")
            try:
                category = ClaimCategory(cat_str)
            except ValueError:
                category = ClaimCategory.ROLE_TENURE

            text = item.get("claim_text", "").strip()
            if not text:
                continue

            materiality = MaterialityScorer.score(text, category)
            claim = Claim(
                prospect_id=prospect_id,
                claim_text=text,
                category=category,
                materiality=materiality
            )
            claims.append(claim)

        # Return all valid extracted claims, sorted by materiality (HIGH -> MEDIUM -> LOW)
        claims.sort(key=lambda c: 0 if c.materiality.value == "HIGH" else (1 if c.materiality.value == "MEDIUM" else 2))
        return claims
