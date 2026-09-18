import pytest
from fastapi.testclient import TestClient
from src.server import app, db
from src.storage.models import ClaimStatus, ProspectStatus

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Track B" in data["track"]

def test_dashboard_ui_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Growpido" in response.text
    assert "Sovereign Human-in-the-Loop Review Gate" in response.text

def test_invalid_linkedin_url():
    response = client.post("/api/research", json={"linkedin_url": "https://example.com/not-linkedin"})
    assert response.status_code == 400
    assert "Invalid LinkedIn profile URL" in response.json()["detail"]

def test_full_pipeline_and_human_gate_flow():
    # 1. Trigger research on canonical assessment target (UAE Founder/CEO)
    url = "https://www.linkedin.com/in/ronaldo-mouchawar-souq"
    response = client.post("/api/research", json={"linkedin_url": url, "enforce_track_b": True})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    prospect_id = data["prospect_id"]
    assert len(data["claims"]) > 0
    assert len(data["gaps"]) == 3
    assert data["prospect"]["track_b_compliant"] is True

    # 2. Query prospect details
    p_resp = client.get(f"/api/prospects/{prospect_id}")
    assert p_resp.status_code == 200
    p_data = p_resp.json()
    assert p_data["prospect"]["full_name"] == "Ronaldo Mouchawar"

    # 3. VERIFY SOVEREIGN APPROVAL GATING: Export must be locked (HTTP 403) before approval
    pre_md_resp = client.get(f"/api/prospects/{prospect_id}/diagnostic/markdown")
    assert pre_md_resp.status_code == 403
    assert "locked" in pre_md_resp.json()["detail"].lower()

    pre_json_resp = client.get(f"/api/prospects/{prospect_id}/diagnostic/json")
    assert pre_json_resp.status_code == 403
    assert "locked" in pre_json_resp.json()["detail"].lower()

    # 4. Adjudicate claim via Human Gate override
    claim_id = data["claims"][0]["claim_id"]
    override_resp = client.post(
        f"/api/claims/{claim_id}/override",
        json={
            "status": "VERIFIED",
            "override_notes": "Advisor verified directly against Amazon 2017 regulatory press disclosure."
        }
    )
    assert override_resp.status_code == 200
    assert override_resp.json()["new_status"] == "VERIFIED"

    # 5. Approve prospect at Human Gate
    approve_resp = client.post(
        f"/api/prospects/{prospect_id}/approve",
        json={"reviewer_notes": "All claims audited and verified."}
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == ProspectStatus.APPROVED.value

    # 6. Download Markdown Diagnostic (Now unlocked)
    md_resp = client.get(f"/api/prospects/{prospect_id}/diagnostic/markdown")
    assert md_resp.status_code == 200
    assert "Executive Diagnostic Briefing: Ronaldo Mouchawar" in md_resp.text
    assert "Three Biggest Strategic Presence Gaps" in md_resp.text
    # Ensure no fabricated $50M claim exists
    assert "$50M" not in md_resp.text

    # 7. Export JSON Dossier
    json_resp = client.get(f"/api/prospects/{prospect_id}/diagnostic/json")
    assert json_resp.status_code == 200
    json_data = json_resp.json()
    assert json_data["prospect"]["slug"] == "ronaldo-mouchawar-souq"
    assert len(json_data["claims"]) > 0

    # 8. Cryptographic Hash-Chained Audit Trail Verification
    verify_resp = client.get(f"/api/prospects/{prospect_id}/audit/verify")
    assert verify_resp.status_code == 200
    v_data = verify_resp.json()
    assert v_data["verification"]["valid"] is True
    assert v_data["verification"]["total_events"] > 0
    assert v_data["verification"]["head_hash"] != "GENESIS"

def test_candidate_search_track_b_classification():
    # UAE Founder Candidate
    resp_uae = client.post(
        "/api/search/candidates",
        json={"name": "Ronaldo Mouchawar", "context_keywords": "Amazon MENA Souq UAE"}
    )
    assert resp_uae.status_code == 200
    candidates_uae = resp_uae.json()["candidates"]
    assert len(candidates_uae) > 0
    assert candidates_uae[0]["track_b_compliant"] is True

    # Non-UAE Political Candidate (Negative Test)
    resp_non_uae = client.post(
        "/api/search/candidates",
        json={"name": "Narendra Modi", "context_keywords": "Prime Minister of India"}
    )
    assert resp_non_uae.status_code == 200
    candidates_non_uae = resp_non_uae.json()["candidates"]
    assert len(candidates_non_uae) > 0
    # Modi should be flagged as non-Track B compliant
    assert candidates_non_uae[0]["track_b_compliant"] is False
    assert "Track B Scope Warning" in candidates_non_uae[0]["compliance_notes"]

def test_candidate_search_empty_name():
    response = client.post("/api/search/candidates", json={"name": "  "})
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]

def test_track_b_scope_enforcement():
    # Attempting to ingest non-UAE candidate with enforce_track_b=True must be rejected with 422
    payload = {
        "linkedin_url": "https://www.linkedin.com/in/narendramodi",
        "candidate_name": "Narendra Modi",
        "candidate_headline": "Prime Minister of India",
        "candidate_location": "New Delhi, India",
        "enforce_track_b": True
    }
    response = client.post("/api/research", json=payload)
    assert response.status_code == 422
    assert "Track B Scope Violation" in response.json()["detail"]
