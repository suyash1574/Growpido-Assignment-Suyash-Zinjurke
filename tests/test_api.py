import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from src.server import app, db
from src.storage.models import Claim, ClaimCategory, ClaimStatus, Materiality, Prospect, ProspectStatus, StrategicGap, GapDimension
from src.diagnosis.diagnostic_renderer import DiagnosticRenderer

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_external_network(monkeypatch):
    """
    Mock external search, web fetch, and LLM calls for lightning-fast (< 5s) deterministic testing.
    """
    from src.discovery.search_client import SearchClient
    from src.discovery.web_fetcher import WebFetcher
    from src.llm_client import UnifiedLLMClient

    async def mock_search(self, query: str, max_results: int = 5):
        q_lower = query.lower()
        if "narendra modi" in q_lower:
            return [{
                "title": "Narendra Modi - Prime Minister of India | LinkedIn",
                "url": "https://in.linkedin.com/in/narendramodi",
                "snippet": "Narendra Modi is the Prime Minister of India, located in New Delhi, India."
            }]
        elif "ronaldo" in q_lower or "mouchawar" in q_lower:
            return [{
                "title": "Ronaldo Mouchawar - Vice President, Amazon Middle East | LinkedIn",
                "url": "https://www.linkedin.com/in/ronaldomouchawar",
                "snippet": "Ronaldo Mouchawar is Vice President at Amazon MENA, co-founder of Souq.com, located in Dubai, United Arab Emirates."
            }, {
                "title": "Ronaldo Mouchawar Biography and Career | The National News",
                "url": "https://www.thenationalnews.com/business/ronaldo-mouchawar-souq",
                "snippet": "Ronaldo Mouchawar founded Souq.com in Dubai in 2005. Amazon acquired Souq in 2017."
            }]
        return [{
            "title": "Executive Leadership Profile",
            "url": "https://ae.linkedin.com/in/executive-leader",
            "snippet": "CEO and Founder based in Dubai, United Arab Emirates."
        }]

    async def mock_fetch(self, url: str):
        return {
            "status_code": 200,
            "url": url,
            "text": (
                "Ronaldo Mouchawar co-founded Souq.com in 2005 in Dubai, United Arab Emirates. "
                "In 2017, Amazon acquired Souq.com for approximately $580 million. "
                "Ronaldo Mouchawar currently serves as Vice President of Amazon Middle East and North Africa. "
                "Third-party celebrity net worth aggregators estimate his personal fortune at $150 million without regulatory proof."
            ),
            "content_hash": "sha256_mock_hash_123"
        }

    def mock_chat_json(self, messages, max_tokens=800, temperature=0.1):
        content = "\n".join(m.get("content", "") for m in messages).lower()
        if "extract atomic claims" in content:
            return {
                "claims": [
                    {"claim_text": "Ronaldo Mouchawar co-founded Souq.com in Dubai in 2005.", "category": "ROLE_TENURE"},
                    {"claim_text": "Amazon acquired Souq.com in 2017 for approximately $580 million.", "category": "FUNDING_FINANCIAL"},
                    {"claim_text": "Ronaldo Mouchawar serves as Vice President of Amazon MENA.", "category": "ROLE_TENURE"},
                    {"claim_text": "Celebrity net worth aggregators report personal wealth at $150 million.", "category": "FUNDING_FINANCIAL"}
                ]
            }
        elif "strategic presence gaps" in content or "synthesize exactly 3" in content:
            return {
                "gaps": [
                    {
                        "rank": 1,
                        "dimension": "AUTHORITY_UNDER_INDEXING",
                        "title": "Disproportionate Market Influence vs. Digital Visibility",
                        "observation": "Extensive commercial footprint is under-represented in primary knowledge graphs.",
                        "strategic_impact": "Institutional partners default to secondary aggregator summaries.",
                        "recommendation": "Publish authoritative founder retrospectives across sovereign channels."
                    },
                    {
                        "rank": 2,
                        "dimension": "CHANNEL_DIVERSITY_DEFICIT",
                        "title": "Single-Channel Dependency in Executive Communications",
                        "observation": "Public commentary is largely concentrated on third-party conference reports.",
                        "strategic_impact": "Reduced direct influence over executive brand narrative.",
                        "recommendation": "Establish owned long-form executive publishing platform."
                    },
                    {
                        "rank": 3,
                        "dimension": "NARRATIVE_FRAGMENTATION",
                        "title": "Historical Legacy Narrative Fragmentation",
                        "observation": "Souq.com founding achievements and Amazon MENA scale are split across disparate media accounts.",
                        "strategic_impact": "Diminished sovereign executive profile continuity.",
                        "recommendation": "Consolidate official archival timeline on primary sovereign domain."
                    }
                ]
            }
        return {}

    def mock_chat(self, messages, max_tokens=600, temperature=0.0, json_mode=False):
        content = "\n".join(m.get("content", "") for m in messages).lower()
        if "entailment" in content:
            if "$150 million" in content or "celebrity" in content or "aggregators" in content:
                return "FAIL: No primary sovereign registry corroborates this aggregator net worth estimate."
            return "PASS: The primary record directly entails this executive tenure fact."
        elif "contradiction" in content:
            return "CONTRADICTION: None. Sources are consistent."
        return "PASS"

    monkeypatch.setattr(SearchClient, "search", mock_search)
    monkeypatch.setattr(WebFetcher, "fetch_and_clean", mock_fetch)
    monkeypatch.setattr(UnifiedLLMClient, "chat_completion_json", mock_chat_json)
    monkeypatch.setattr(UnifiedLLMClient, "chat_completion", mock_chat)


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

def test_track_b_scope_enforcement_default_true():
    # When enforce_track_b is omitted, it must default to True and reject non-UAE target with 422
    payload = {
        "linkedin_url": "https://www.linkedin.com/in/narendramodi",
        "candidate_name": "Narendra Modi",
        "candidate_headline": "Prime Minister of India",
        "candidate_location": "New Delhi, India"
    }
    response = client.post("/api/research", json=payload)
    assert response.status_code == 422
    assert "Track B Scope Violation" in response.json()["detail"]

def test_contradicted_and_refused_claims_excluded_from_dossier():
    """
    Directly tests Issue 1: Contradicted/refused claims must NEVER appear in the main dossier table.
    """
    prospect = Prospect(
        full_name="Ronaldo Mouchawar",
        primary_role="CEO",
        current_company="Souq.com",
        location_country="United Arab Emirates",
        sector="E-Commerce",
        linkedin_url="https://www.linkedin.com/in/ronaldomouchawar",
        slug="ronaldo"
    )
    
    clean_claim = Claim(
        prospect_id=prospect.prospect_id,
        claim_text="Ronaldo Mouchawar co-founded Souq.com in 2005.",
        category=ClaimCategory.ROLE_TENURE,
        materiality=Materiality.HIGH,
        status=ClaimStatus.VERIFIED,
        check1_passed=True,
        check2_passed=True
    )
    
    contradicted_claim = Claim(
        prospect_id=prospect.prospect_id,
        claim_text="Ronaldo Mouchawar stepped down in 2015 before acquisition.",
        category=ClaimCategory.ROLE_TENURE,
        materiality=Materiality.HIGH,
        status=ClaimStatus.PARTIALLY_VERIFIED,
        check1_passed=False,
        check2_passed=False,
        contradiction_detected=True,
        contradiction_details="Conflict with official corporate press record.",
        refusal_code="REF-02",
        refusal_reason="Unresolved contradiction across public sources regarding tenure date."
    )
    
    gaps = [
        StrategicGap(
            prospect_id=prospect.prospect_id,
            rank=1,
            dimension=GapDimension.AUTHORITY_UNDER_INDEXING,
            title="Gap 1",
            observation="Obs 1",
            strategic_impact="Impact 1",
            recommendation="Rec 1"
        )
    ]
    
    md_output = DiagnosticRenderer.render_markdown(prospect, [clean_claim, contradicted_claim], gaps)
    
    # Assert clean claim is in the Fact Dossier table
    assert "| `VERIFIED` | ROLE_TENURE | Ronaldo Mouchawar co-founded Souq.com in 2005." in md_output
    
    # Assert contradicted claim is NOT in the Fact Dossier table
    assert "| `PARTIAL` | ROLE_TENURE | Ronaldo Mouchawar stepped down in 2015" not in md_output
    
    # Assert contradicted claim IS present in the Quarantined section with REF-02
    assert "REF-02" in md_output
    assert "Ronaldo Mouchawar stepped down in 2015 before acquisition." in md_output

def test_one_page_length_budget_enforced():
    """
    Directly tests Issue 2: Markdown output enforces strict top-5 claims table and one-page budget.
    """
    prospect = Prospect(
        full_name="Ronaldo Mouchawar",
        primary_role="CEO",
        current_company="Souq.com",
        location_country="United Arab Emirates",
        sector="E-Commerce",
        linkedin_url="https://www.linkedin.com/in/ronaldomouchawar",
        slug="ronaldo"
    )
    
    # Create 12 verified claims
    claims = [
        Claim(
            prospect_id=prospect.prospect_id,
            claim_text=f"Verified Assertion #{i}",
            category=ClaimCategory.ROLE_TENURE,
            materiality=Materiality.HIGH if i <= 5 else Materiality.LOW,
            status=ClaimStatus.VERIFIED,
            check1_passed=True,
            check2_passed=True
        )
        for i in range(1, 13)
    ]
    
    refused = Claim(
        prospect_id=prospect.prospect_id,
        claim_text="Unverified aggregator estimate.",
        category=ClaimCategory.FUNDING_FINANCIAL,
        materiality=Materiality.MEDIUM,
        status=ClaimStatus.UNVERIFIED,
        refusal_code="REF-01",
        refusal_reason="No Tier-1 primary source substantiated this claim."
    )
    claims.append(refused)
    
    gaps = [
        StrategicGap(
            prospect_id=prospect.prospect_id,
            rank=i,
            dimension=GapDimension.AUTHORITY_UNDER_INDEXING,
            title=f"Strategic Gap #{i}",
            observation=f"Observation #{i}",
            strategic_impact=f"Impact #{i}",
            recommendation=f"Recommendation #{i}"
        )
        for i in range(1, 4)
    ]
    
    md_output = DiagnosticRenderer.render_markdown(prospect, claims, gaps)
    
    # Count rows in the fact dossier table (lines starting with | `VERIFIED` |)
    table_rows = [line for line in md_output.splitlines() if line.startswith("| `VERIFIED` |")]
    assert len(table_rows) == 5, f"Expected exactly 5 rows in Fact Dossier, got {len(table_rows)}"
    
    # Check notice explaining one-page brevity
    assert "Top 5 material assertions displayed for one-page executive brevity" in md_output
    
    # Check total length fits comfortably within one-page briefing budget (under 75 lines)
    assert len(md_output.splitlines()) < 75

def test_guaranteed_refusal_example_in_pipeline():
    """
    Directly tests Issue 3: Final run must guarantee at least one real refused claim in the output.
    """
    url = "https://www.linkedin.com/in/ronaldo-mouchawar-souq"
    response = client.post("/api/research", json={"linkedin_url": url, "enforce_track_b": True})
    assert response.status_code == 200
    data = response.json()
    
    # Find quarantined claims
    refused_claims = [c for c in data["claims"] if c.get("refusal_code")]
    assert len(refused_claims) >= 1, "Track B mandate violated: zero quarantined assertions returned!"
    assert refused_claims[0]["refusal_code"] in ["REF-01", "REF-02", "REF-03", "REF-04", "REF-05"]
    assert len(refused_claims[0]["refusal_reason"]) > 10

def test_person_and_entity_summary_rendering():
    """
    Tests that Person and Entity summaries are correctly synthesized, persisted, and rendered.
    """
    prospect = Prospect(
        full_name="Ronaldo Mouchawar",
        primary_role="Vice President, Amazon MENA",
        current_company="Amazon MENA",
        location_country="United Arab Emirates",
        sector="E-Commerce & Digital Marketplaces",
        linkedin_url="https://www.linkedin.com/in/ronaldo-mouchawar-souq",
        slug="ronaldo-mouchawar-souq",
        person_summary="Ronaldo Mouchawar is a technology pioneer serving as Vice President of Amazon MENA and co-founder of Souq.com.",
        entity_summary="Amazon MENA is the leading e-commerce and cloud logistics fulfillment infrastructure network in the Middle East."
    )
    db.save_prospect(prospect)
    retrieved = db.get_prospect(str(prospect.prospect_id))
    assert retrieved["person_summary"] == prospect.person_summary
    assert retrieved["entity_summary"] == prospect.entity_summary

    md_output = DiagnosticRenderer.render_markdown(prospect, [], [])
    assert "## Executive & Operating Entity Briefing" in md_output
    assert "**The Executive (Person)**: Ronaldo Mouchawar is a technology pioneer" in md_output
    assert "**The Operating Entity (Company)**: Amazon MENA is the leading e-commerce" in md_output

def test_profile_facts_retrieved_verified_and_counted():
    """
    Tests that profile facts retrieved from LinkedIn (role, company, location)
    are seeded as candidate claims, marked is_profile_fact=True, verified, and counted in Verified (Double-Checked).
    """
    from src.extraction.claim_auditor import ClaimAuditor
    from uuid import uuid4
    auditor = ClaimAuditor()
    pid = uuid4()
    claims = auditor.extract_profile_claims(
        prospect_id=pid,
        full_name="Ronaldo Mouchawar",
        primary_role="Vice President, Amazon MENA & Co-founder Souq.com",
        current_company="Amazon MENA",
        location_country="United Arab Emirates"
    )
    assert len(claims) >= 2
    assert all(c.is_profile_fact for c in claims)
    claim_texts = " ".join(c.claim_text for c in claims)
    assert "Ronaldo Mouchawar" in claim_texts
    assert "Souq" in claim_texts or "Amazon" in claim_texts

    # Check persistence and rendering
    prospect = Prospect(
        full_name="Ronaldo Mouchawar",
        primary_role="Vice President, Amazon MENA",
        current_company="Amazon MENA",
        location_country="United Arab Emirates",
        sector="E-Commerce & Digital Marketplaces",
        linkedin_url="https://www.linkedin.com/in/ronaldo-mouchawar-souq",
        slug="ronaldo-mouchawar-souq"
    )
    db.save_claims(claims)
    retrieved = db.get_claims(str(pid))
    assert len(retrieved) == len(claims)
    assert any(r.get("is_profile_fact") == 1 for r in retrieved)

    # Verify that verified profile claims are rendered in Markdown with Profile tag
    verified_profile_claim = Claim(
        prospect_id=prospect.prospect_id,
        claim_text="Ronaldo Mouchawar serves as Vice President of Amazon MENA.",
        category=ClaimCategory.ROLE_TENURE,
        materiality=Materiality.HIGH,
        status=ClaimStatus.VERIFIED,
        check1_passed=True,
        check2_passed=True,
        is_profile_fact=True,
        primary_source_url="https://press.aboutamazon.com/2017/3/amazon-to-acquire-souq-com",
        secondary_source_url="https://www.reuters.com/article/souq-amazon"
    )
    md = DiagnosticRenderer.render_markdown(prospect, [verified_profile_claim], [])
    assert "| `VERIFIED` | ROLE_TENURE (Profile) | Ronaldo Mouchawar serves as Vice President" in md


