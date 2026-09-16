import pytest
from uuid import uuid4
from src.storage.models import Claim, ClaimCategory, Materiality, ClaimStatus
from src.verification.refusal_engine import RefusalEngine

def test_unverified_claim_receives_ref01():
    claim = Claim(
        claim_id=uuid4(),
        prospect_id=uuid4(),
        claim_text="Personal angel portfolio contains 40+ startups valued over $50M.",
        category=ClaimCategory.FUNDING_FINANCIAL,
        materiality=Materiality.HIGH,
        status=ClaimStatus.UNVERIFIED,
        check1_passed=False
    )
    processed = RefusalEngine.process([claim])[0]
    assert processed.refusal_code == "REF-01"
    assert "No Tier-1 primary source" in processed.refusal_reason

def test_contradiction_claim_receives_ref02():
    claim = Claim(
        claim_id=uuid4(),
        prospect_id=uuid4(),
        claim_text="Founded Souq.com in 2005.",
        category=ClaimCategory.ROLE_TENURE,
        materiality=Materiality.HIGH,
        status=ClaimStatus.PARTIALLY_VERIFIED,
        contradiction_detected=True,
        contradiction_details="Conflicting founding years."
    )
    processed = RefusalEngine.process([claim])[0]
    assert processed.refusal_code == "REF-02"
    assert "Unresolved contradiction" in processed.refusal_reason
