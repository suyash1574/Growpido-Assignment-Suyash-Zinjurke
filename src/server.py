import os
import json
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path

from src.storage.db import Database
from src.storage.models import Prospect, Claim, StrategicGap, ClaimStatus, ProspectStatus
from src.orchestrator import Orchestrator
from src.diagnosis.diagnostic_renderer import DiagnosticRenderer

app = FastAPI(
    title="Growpido Track B — Executive Prospect Intelligence API",
    description="Adversarial OSINT Research, Double-Checked Verification, Sovereign Human Gate, and One-Page Diagnostic Engine.",
    version="1.0.0"
)

# Template and static paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Shared database & orchestrator
db = Database()
from src.discovery.candidate_search import CandidateSearchEngine
from src.storage.models import CandidateMatch

orchestrator = Orchestrator(db)

# Request / Response Schemas
class CandidateSearchRequest(BaseModel):
    name: str
    context_keywords: Optional[str] = None
    max_candidates: Optional[int] = 5

class ResearchRequest(BaseModel):
    linkedin_url: str
    candidate_name: Optional[str] = None
    candidate_headline: Optional[str] = None
    candidate_location: Optional[str] = None
    candidate_company: Optional[str] = None
    candidate_role: Optional[str] = None
    enforce_track_b: Optional[bool] = True

class ClaimOverrideRequest(BaseModel):
    status: str
    override_notes: Optional[str] = "Manual override by Advisor"

class ApproveRequest(BaseModel):
    reviewer_notes: Optional[str] = "Approved at Sovereign Human Gate"

# --- Web UI Endpoint ---
@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Serves the Growpido Executive Intelligence Dashboard UI."""
    return templates.TemplateResponse(request, "index.html")

# --- Health Check ---
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Growpido Intelligence Engine (Track B)",
        "track": "Track B: Public OSINT & Double-Checked Verification"
    }

# --- Candidate Search (US1: Upstream Confirmation Gate) ---
@app.post("/api/search/candidates")
async def search_candidates(req: CandidateSearchRequest):
    """
    User Story 1: Upstream Human Candidate Confirmation Gate.
    Searches public web records for candidate profiles matching the provided name
    and optional context keywords, returning candidate match cards for advisor selection.
    """
    name = req.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    engine = CandidateSearchEngine()
    candidates = await engine.search_candidates(
        name=name,
        context_keywords=req.context_keywords,
        max_candidates=req.max_candidates or 5
    )
    return {
        "success": True,
        "query_name": name,
        "total_matches": len(candidates),
        "candidates": [c.model_dump(mode="json") for c in candidates]
    }

# --- Pipeline Execution ---
@app.post("/api/research")
async def execute_research_pipeline(req: ResearchRequest):
    """
    Executes the end-to-end intelligence pipeline:
    1. Canonical Ingestion
    2. Live OSINT Discovery
    3. Claim Extraction
    4. Two-Stage Double-Check Verification
    5. Adversarial Refusal Processing
    6. 3-Gap Strategic Presence Synthesis
    """
    url = req.linkedin_url.strip()
    if not url or "linkedin.com/in/" not in url:
        raise HTTPException(
            status_code=400,
            detail="Invalid LinkedIn profile URL. Must be in format: https://www.linkedin.com/in/{slug}"
        )

    try:
        result = await orchestrator.execute_research(
            linkedin_url=url,
            candidate_name=req.candidate_name,
            candidate_headline=req.candidate_headline,
            candidate_location=req.candidate_location,
            candidate_company=req.candidate_company,
            candidate_role=req.candidate_role,
            enforce_track_b=bool(req.enforce_track_b)
        )

        return {
            "success": True,
            "prospect_id": str(result["prospect"].prospect_id),
            "prospect": result["prospect"].model_dump(mode="json"),
            "sources_count": len(result["sources"]),
            "claims": [c.model_dump(mode="json") for c in result["claims"]],
            "gaps": [g.model_dump(mode="json") for g in result["gaps"]]
        }
    except ValueError as ve:
        if "Track B Scope Violation" in str(ve):
            raise HTTPException(status_code=422, detail=str(ve))
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

# --- Retrieve Prospect Intelligence ---
@app.get("/api/prospects/{prospect_id}")
async def get_prospect_details(prospect_id: str):
    """Retrieves current prospect info, verified & quarantined claims, and strategic gaps."""
    prospect = db.get_prospect(prospect_id)
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")

    claims = db.get_claims(prospect_id)
    gaps = db.get_gaps(prospect_id)
    audit = db.get_audit_log(prospect_id)

    return {
        "prospect": prospect,
        "claims": claims,
        "gaps": gaps,
        "audit_events": audit
    }

# --- Human Gate: Claim Adjudication ---
@app.post("/api/claims/{claim_id}/override")
async def override_claim_status(claim_id: str, req: ClaimOverrideRequest):
    """
    Sovereign Human-in-the-Loop Gate:
    Allows advisors to review contradictory evidence or false flags and manually adjudicate claim status.
    Requires an override rationale for strict audit tracking.
    """
    allowed_statuses = [ClaimStatus.VERIFIED.value, ClaimStatus.PARTIALLY_VERIFIED.value, ClaimStatus.UNVERIFIED.value]
    if req.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed values: {allowed_statuses}"
        )

    claim = db.get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    success = db.update_claim_status(claim_id, req.status, req.override_notes or "Manual override")
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update claim status")

    # Record Audit Event
    orchestrator.audit.log(
        claim["prospect_id"],
        "HUMAN_CLAIM_OVERRIDE",
        {
            "claim_id": claim_id,
            "old_status": claim["status"],
            "new_status": req.status,
            "reason": req.override_notes
        }
    )

    return {
        "success": True,
        "claim_id": claim_id,
        "new_status": req.status,
        "notes": req.override_notes
    }

# --- Human Gate: Final Approval & Compilation ---
@app.post("/api/prospects/{prospect_id}/approve")
async def approve_prospect_diagnostic(prospect_id: str, req: ApproveRequest):
    """
    Approves the prospect at the Sovereign Human Gate, transitioning status to APPROVED
    and compiling the One-Page Executive Diagnostic.
    """
    prospect = db.get_prospect(prospect_id)
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")

    db.update_prospect_status(prospect_id, ProspectStatus.APPROVED.value)
    orchestrator.audit.log(
        prospect_id,
        "DIAGNOSTIC_APPROVED",
        {"reviewer_notes": req.reviewer_notes}
    )

    return {
        "success": True,
        "prospect_id": prospect_id,
        "status": ProspectStatus.APPROVED.value
    }

# --- Export One-Page Diagnostic ---
@app.get("/api/prospects/{prospect_id}/diagnostic/markdown")
async def download_diagnostic_markdown(prospect_id: str):
    """Generates and downloads the verified One-Page Executive Diagnostic in Markdown."""
    prospect_row = db.get_prospect(prospect_id)
    if not prospect_row:
        raise HTTPException(status_code=404, detail="Prospect not found")

    prospect = Prospect(**prospect_row)
    # Sovereign Human Gate Enforcement: diagnostic cannot be exported until formally approved
    if prospect.status != ProspectStatus.APPROVED:
        raise HTTPException(
            status_code=403,
            detail="Diagnostic export locked: Prospect has not been approved at the Sovereign Human Gate. Adjudicate claims and sign off before compilation."
        )

    claim_rows = db.get_claims(prospect_id)
    gap_rows = db.get_gaps(prospect_id)

    claims = [Claim(**c) for c in claim_rows]
    gaps = [StrategicGap(**g) for g in gap_rows]

    md_content = DiagnosticRenderer.render_markdown(prospect, claims, gaps)

    return PlainTextResponse(
        content=md_content,
        headers={
            "Content-Disposition": f'attachment; filename="Growpido_Diagnostic_{prospect.slug}.md"'
        },
        media_type="text/markdown"
    )

@app.get("/api/prospects/{prospect_id}/diagnostic/json")
async def download_diagnostic_json(prospect_id: str):
    """Exports the entire verified dossier, evidence citations, and append-only audit trail."""
    prospect = db.get_prospect(prospect_id)
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")

    # Sovereign Human Gate Enforcement: diagnostic cannot be exported until formally approved
    if prospect["status"] != ProspectStatus.APPROVED.value:
        raise HTTPException(
            status_code=403,
            detail="Diagnostic export locked: Prospect has not been approved at the Sovereign Human Gate. Adjudicate claims and sign off before compilation."
        )

    claims = db.get_claims(prospect_id)
    gaps = db.get_gaps(prospect_id)
    audit = db.get_audit_log(prospect_id)

    payload = {
        "prospect": prospect,
        "total_claims": len(claims),
        "claims": claims,
        "strategic_gaps": gaps,
        "audit_trail": audit
    }

    return JSONResponse(
        content=payload,
        headers={
            "Content-Disposition": f'attachment; filename="Growpido_Dossier_{prospect["slug"]}.json"'
        }
    )

@app.get("/api/prospects/{prospect_id}/audit/verify")
async def verify_prospect_audit_trail(prospect_id: str):
    """
    Cryptographically verifies the immutable SHA-256 hash chain for a prospect's audit log.
    """
    prospect_row = db.get_prospect(prospect_id)
    if not prospect_row:
        raise HTTPException(status_code=404, detail="Prospect not found")

    result = db.verify_audit_trail(prospect_id)
    return {
        "success": True,
        "prospect_id": prospect_id,
        "verification": result
    }
