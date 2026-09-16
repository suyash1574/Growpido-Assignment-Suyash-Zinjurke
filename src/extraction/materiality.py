from src.storage.models import Materiality, ClaimCategory

class MaterialityScorer:
    HIGH_KEYWORDS = [
        "fund", "aum", "valuation", "million", "billion", "exit", "$", "acquisition",
        "vice president", "ceo", "founder", "co-founder", "partner", "board", "director",
        "degree", "master", "phd", "bachelor", "university"
    ]
    
    MEDIUM_KEYWORDS = [
        "keynote", "speaker", "panel", "advisory", "committee", "award", "fellow", "conference"
    ]

    @classmethod
    def score(cls, claim_text: str, category: ClaimCategory) -> Materiality:
        text_lower = claim_text.lower()
        if category in [ClaimCategory.FUNDING_FINANCIAL, ClaimCategory.GOVERNANCE_BOARD]:
            return Materiality.HIGH

        if any(kw in text_lower for kw in cls.HIGH_KEYWORDS):
            return Materiality.HIGH

        if any(kw in text_lower for kw in cls.MEDIUM_KEYWORDS):
            return Materiality.MEDIUM

        return Materiality.LOW
