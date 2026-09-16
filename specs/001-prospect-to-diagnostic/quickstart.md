# Quickstart Validation & Run Guide

**Feature**: `001-prospect-to-diagnostic`  
**Date**: 2026-09-16  
**Status**: Ready for Implementation  

---

## 1. Prerequisites
- Python `3.11+`
- Valid `GROQ_API_KEY` configured in `.env`
- Active Internet Connection (for live public OSINT discovery)

---

## 2. Environment Setup
```bash
# 1. Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

---

## 3. Quick Run Verification Scenarios

### Scenario A: Run Automated Test Suites
Prove fact integrity, double-check logic, and adversarial refusal:
```bash
pytest tests/ -v
```
**Expected Outcome:**
- `test_ingest.py`: URL normalization passes.
- `test_verification.py`: Tier-1 grounding passes; Check 1 and Check 2 validate assertions.
- `test_refusal.py`: Unverified claims are quarantined with `REF-01` and explicit refusal explanation.
- `test_gap_synthesizer.py`: Exactly 3 strategic presence gaps returned.

---

### Scenario B: Launch Interactive Web Application
```bash
streamlit run src/app.py
```
**Steps to Validate:**
1. Open `http://localhost:8501`.
2. Enter Candidate LinkedIn URL: `https://www.linkedin.com/in/ronaldo-mouchawar-souq`.
3. Click **"Run Intelligence Pipeline"**.
4. Observe live execution stages:
   - Target Ingestion ➔ Live OSINT Discovery ➔ Claim Extraction ➔ Double-Check Verification.
5. Review the **Human Gate**:
   - Inspect verified claims, citation chips, and contradiction warnings.
   - Click **"Approve & Compile Diagnostic"**.
6. View the final **One-Page Diagnostic**:
   - Verified facts table.
   - 3 Strategic Presence Gaps (Authority, Channel, Narrative).
   - Demonstrates the refused claim ($50M angel portfolio rumor) with causal rationale.
