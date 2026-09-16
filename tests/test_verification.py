import pytest
from uuid import uuid4
from src.storage.models import Claim, ClaimCategory, Materiality, ClaimStatus
from src.verification.classifier_hub import ClassifierHub

def test_classifier_hub_verified():
    claim = Claim(
        claim_id=uuid4(),
        prospect_id=uuid4(),
        claim_text="Co-founded Souq.com in 2005.",
        category=ClaimCategory.ROLE_TENURE,
        materiality=Materiality.HIGH,
        check1_passed=True,
        check2_passed=True,
        contradiction_detected=False
    )
    assert ClassifierHub.classify(claim) == ClaimStatus.VERIFIED

def test_classifier_hub_partial_due_to_contradiction():
    claim = Claim(
        claim_id=uuid4(),
        prospect_id=uuid4(),
        claim_text="Founded Souq.com in 2005.",
        category=ClaimCategory.ROLE_TENURE,
        materiality=Materiality.HIGH,
        check1_passed=True,
        check2_passed=True,
        contradiction_detected=True,
        contradiction_details="Source A says 2005, Source B says 2006."
    )
    assert ClassifierHub.classify(claim) == ClaimStatus.PARTIALLY_VERIFIED

def test_classifier_hub_unverified_when_check1_fails():
    claim = Claim(
        claim_id=uuid4(),
        prospect_id=uuid4(),
        claim_text="Private angel investment fund exceeds $100M.",
        category=ClaimCategory.FUNDING_FINANCIAL,
        materiality=Materiality.HIGH,
        check1_passed=False,
        check2_passed=False,
        contradiction_detected=False
    )
    assert ClassifierHub.classify(claim) == ClaimStatus.UNVERIFIED
