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
    # 1. Trigger research on canonical assessment target
    url = "https://www.linkedin.com/in/ronaldo-mouchawar-souq"
    response = client.post("/api/research", json={"linkedin_url": url})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    prospect_id = data["prospect_id"]
    assert len(data["claims"]) > 0
    assert len(data["gaps"]) == 3

    # 2. Query prospect details
    p_resp = client.get(f"/api/prospects/{prospect_id}")
    assert p_resp.status_code == 200
    p_data = p_resp.json()
    assert p_data["prospect"]["full_name"] == "Ronaldo Mouchawar"

    # 3. Adjudicate claim via Human Gate override
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

    # 4. Approve prospect at Human Gate
    approve_resp = client.post(
        f"/api/prospects/{prospect_id}/approve",
        json={"reviewer_notes": "All claims audited and verified."}
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == ProspectStatus.APPROVED.value

    # 5. Download Markdown Diagnostic
    md_resp = client.get(f"/api/prospects/{prospect_id}/diagnostic/markdown")
    assert md_resp.status_code == 200
    assert "Executive Diagnostic Briefing: Ronaldo Mouchawar" in md_resp.text
    assert "Three Biggest Strategic Presence Gaps" in md_resp.text

    # 6. Export JSON Dossier
    json_resp = client.get(f"/api/prospects/{prospect_id}/diagnostic/json")
    assert json_resp.status_code == 200
    json_data = json_resp.json()
    assert json_data["prospect"]["slug"] == "ronaldo-mouchawar-souq"
    assert len(json_data["claims"]) > 0
