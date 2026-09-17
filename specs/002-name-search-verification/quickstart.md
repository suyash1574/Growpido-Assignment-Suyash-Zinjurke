# Quickstart Validation Guide: Name-Based Search & Global Authority Verification

**Feature**: `002-name-search-verification`  
**Date**: 2026-09-17  
**Status**: Ready for Validation

---

## 1. Prerequisites
- Python 3.12+ virtual environment activated.
- Valid API keys in `.env`:
  - `TAVILY_API_KEY`: For live public OSINT discovery
  - `GROQ_API_KEY`: Primary high-speed LLM engine
  - `NVIDIA_API_KEY`: Failover LLM engine (`nvidia/nemotron-3.5-lightning-30b-a3b`)

---

## 2. Validation Scenario 1: Name-Based Candidate Discovery & Human Confirmation Gate

1. **Start the FastAPI Application**:
   ```powershell
   python -m uvicorn src.server:app --port 8000 --reload
   ```
2. **Access the Dashboard**:
   Open `http://127.0.0.1:8000` in your web browser.
3. **Execute Name Search**:
   - In Step 1, enter **Name**: `Ronaldo Mouchawar`
   - Optional Context: `Amazon Souq UAE`
   - Click **"Search Candidate Profiles"** (`POST /api/search/candidates`).
4. **Expected Outcome**:
   - The UI reveals a **Candidate Confirmation Gate** with candidate match cards.
   - The top candidate displays:
     - Name: `Ronaldo Mouchawar`
     - Headline / Role: `Vice President at Amazon MENA & Co-founder Souq.com`
     - Location: `Dubai, United Arab Emirates`
     - Link: `https://www.linkedin.com/in/ronaldo-mouchawar-souq`
   - The advisor clicks **"Confirm & Research Target"**, locking this profile into the intelligence pipeline.

---

## 3. Validation Scenario 2: Global Sovereign Tier-1 Authority Grounding (Narendra Modi Test)

1. **Search National / Global Leader**:
   - Enter Name: `Narendra Modi`
   - Context: `Prime Minister India`
   - Click **"Search Candidate Profiles"** → Confirm `https://www.linkedin.com/in/narendramodi`.
2. **Run Pipeline**:
   - The system retrieves public web sources, including official government portals (e.g. `pmindia.gov.in`, `india.gov.in`, official gazettes).
   - `TierClassifier` recognizes `.gov.in`, `.gov`, `.nic.in` as **Tier-1 Primary Authority**.
3. **Inspect Human Gate**:
   - Assertion: *"Narendra Modi has served as the Prime Minister of India since 26 May 2014"*
   - **Check 1 (Primary)**: `PASSED` (Entailed by official government portal `pmindia.gov.in` or `india.gov.in`)
   - **Check 2 (Corroboration)**: `PASSED` (Confirmed by independent news/wire reporting)
   - **Status**: **`VERIFIED`** (or `PARTIALLY_VERIFIED` with citation if corroboration pending), NOT falsely quarantined with `REF-01`.
4. **Inspect Compiled Diagnostic**:
   - Header reads: `Executive Briefing: Narendra Modi`
   - Role / Jurisdiction: `Prime Minister of India | Public Governance | India` (dynamically contextualized, NOT hardcoded to "UAE Commercial Sector").
   - Verified Fact Dossier lists the primary government citation.

---

## 4. Automated Verification Commands

```powershell
# Run backend API tests covering candidate search and global tier classification
python -m pytest tests/test_api.py -v

# Run unit tests verifying TierClassifier and DoubleChecker on global domains
python -m pytest tests/unit/ -v

# Run full Chromium browser automation test
python tests/run_browser_test.py
```
