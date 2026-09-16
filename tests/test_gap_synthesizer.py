import pytest
from uuid import uuid4
from src.storage.models import Claim, ClaimCategory, Materiality, ClaimStatus, GapDimension
from src.diagnosis.gap_synthesizer import GapSynthesizer

def test_gap_synthesizer_returns_exact_three_gaps():
    synthesizer = GapSynthesizer()
    prospect_id = uuid4()
    claims = [
        Claim(
            claim_id=uuid4(),
            prospect_id=prospect_id,
            claim_text="Vice President of Amazon MENA.",
            category=ClaimCategory.ROLE_TENURE,
            materiality=Materiality.HIGH,
            status=ClaimStatus.VERIFIED
        )
    ]
    gaps = synthesizer.synthesize_gaps(prospect_id, "Ronaldo Mouchawar", claims)
    assert len(gaps) == 3
    assert gaps[0].rank == 1
    assert gaps[1].rank == 2
    assert gaps[2].rank == 3
    assert gaps[0].dimension == GapDimension.AUTHORITY_UNDER_INDEXING
    assert gaps[1].dimension == GapDimension.CHANNEL_DIVERSITY_DEFICIT
    assert gaps[2].dimension == GapDimension.NARRATIVE_FRAGMENTATION
