import pytest
from uuid import uuid4
from src.diagnosis.gap_synthesizer import GapSynthesizer
from src.storage.models import Claim, ClaimCategory, ClaimStatus, GapDimension

def test_adaptive_gaps_non_uae_leader():
    synthesizer = GapSynthesizer()
    prospect_id = uuid4()
    
    verified_claim = Claim(
        prospect_id=prospect_id,
        claim_text="Narendra Modi has served as Prime Minister of India since 2014.",
        category=ClaimCategory.ROLE_TENURE,
        status=ClaimStatus.VERIFIED
    )
    
    gaps = synthesizer.synthesize_gaps(
        prospect_id=prospect_id,
        candidate_name="Narendra Modi",
        verified_claims=[verified_claim],
        location_country="India",
        sector="Public Governance & State Leadership"
    )
    
    assert len(gaps) == 3
    assert all(g.dimension in [GapDimension.AUTHORITY_UNDER_INDEXING, GapDimension.CHANNEL_DIVERSITY_DEFICIT, GapDimension.NARRATIVE_FRAGMENTATION] for g in gaps)
    # Ensure default fallback or generated text doesn't inappropriately claim Modi is a UAE commercial executive
    for g in gaps:
        assert "UAE executive" not in g.observation.lower()
