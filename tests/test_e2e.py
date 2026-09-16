import pytest
import asyncio
from src.storage.db import Database
from src.orchestrator import Orchestrator
from src.storage.models import ClaimStatus

def test_full_candidate_pipeline_ronaldo():
    db = Database(":memory:")
    orchestrator = Orchestrator(db)
    
    url = "https://www.linkedin.com/in/ronaldo-mouchawar-souq"
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(orchestrator.execute_research(url))
    
    # Assertions
    assert result["prospect"].full_name == "Ronaldo Mouchawar"
    assert len(result["claims"]) > 0
    assert len(result["gaps"]) == 3
    
    # Verify at least one claim has verified or partial status
    verified = [c for c in result["claims"] if c.status in [ClaimStatus.VERIFIED, ClaimStatus.PARTIALLY_VERIFIED]]
    assert len(verified) > 0
    
    # Verify audit trail was recorded
    audit_events = db.get_audit_log(str(result["prospect"].prospect_id))
    assert len(audit_events) >= 4
