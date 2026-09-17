# Implementation Plan: Name-Based Prospect Search & Global Authority Verification

**Branch**: `002-name-search-verification` | **Date**: 2026-09-17 | **Spec**: [specs/002-name-search-verification/spec.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/specs/002-name-search-verification/spec.md)

**Input**: Feature specification from `specs/002-name-search-verification/spec.md`

---

## Summary

This feature resolves two critical operational hurdles in the Growpido Executive Prospect Intelligence Engine:
1. **Name-Based Search with Sovereign Candidate Confirmation Gate**: Enables advisors to input a person's name (and optional context keywords) instead of hunting for raw LinkedIn URLs. The engine discovers matching candidate public profiles and presents an interactive confirmation gate where the advisor explicitly validates the target before executing deep OSINT.
2. **Universal Sovereign Tier-1 Registry Recognition & Verification Accuracy**: Expands deterministic domain tier classification to recognize all sovereign national government portals (`.gov`, `.gov.*`, `.nic.in`, `.mil`, `.parliament.*`), accredited academic institutions (`.edu`, `.ac.*`), and official corporate investor portals worldwide. This directly eliminates the false-negative defect where substantiated assertions for national or global leaders (e.g., Narendra Modi's tenure as Prime Minister) were erroneously failed by Check 1/Check 2 and quarantined under `REF-01`.
3. **Adaptive Regional & Sector Diagnostic Context**: Dynamically derives jurisdiction and sector from candidate data, eliminating hardcoded "UAE Commercial Sector" strings and producing tailored Strategic Presence Gaps.

---

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, TailwindCSS, Playwright (Chromium), Pydantic v2, Groq SDK, OpenAI SDK (NVIDIA client)  
**Storage**: PostgreSQL (Aiven Cloud via `psycopg2` / `asyncpg`) with SQLite fallback (`data/growpido.db`)  
**Testing**: `pytest`, `pytest-asyncio`, Playwright end-to-end browser automation  
**Target Platform**: Cross-platform (Windows / Linux / Cloud container)  
**Project Type**: Full-stack web application (FastAPI backend + interactive Tailwind dashboard + OSINT verification worker)  
**Performance Goals**: Candidate search resolution in < 3s; full claim audit in < 60s; 0% false-negative quarantines on substantiated primary assertions  
**Constraints**: Zero-credential OSINT (no LinkedIn login cookies / OAuth); dual-engine failover (Groq -> NVIDIA Nemotron); Human Gate sovereignty  
**Scale/Scope**: Enterprise executive prospect research across global commercial, public, and venture leadership sectors

---

## Constitution Check

*GATE: Evaluated against `.specify/memory/constitution.md`. Must pass before implementation.*

| Constitutional Principle | Status | Plan Compliance Mechanism |
| :--- | :---: | :--- |
| **I. Accuracy Takes Precedence Over Completeness** | **PASS** | Expanding Tier-1 recognition to global sovereign registries strictly enhances accuracy without relaxing entailment or corroboration standards. |
| **II. Two-Stage Double-Check Primary Verification** | **PASS** | Check 1 still requires explicit Tier-1 entailment; Check 2 still requires independent corroboration. Recognizes legitimate state portals (`.gov.in`, `pmindia.gov.in`) as Tier-1. |
| **III. Mandatory Adversarial Refusal** | **PASS** | Uncorroborated assertions remain strictly quarantined under `REF-01` to `REF-05` with causal logs. Substantantiated claims achieve `VERIFIED`. |
| **IV. Sovereign Human-in-the-Loop Gate** | **PASS** | Introduced a new upstream Human Candidate Confirmation Gate, alongside the existing Human Claim Adjudication Gate. No profile is researched or finalized autonomously. |
| **V. Strict Public OSINT Boundaries & Zero-Credential Policy** | **PASS** | Name search operates entirely over public web discovery indexes (Tavily/Google/Bing indexing). No LinkedIn credentials, cookies, or private session tokens used. |

---

## Project Structure

### Documentation (this feature)

```text
specs/002-name-search-verification/
├── spec.md              # Feature specification
├── plan.md              # This implementation plan
├── research.md          # Phase 0 research & technical decisions
├── data-model.md        # Phase 1 data entities & state machine
├── quickstart.md        # Phase 1 validation scenarios
├── contracts/           # Phase 1 API schemas & OpenAPI contracts
│   └── candidate-search-api.json
└── checklists/
    └── requirements.md  # Quality validation checklist
```

### Source Code Architecture

```text
src/
├── config.py                     # Environment variables, Groq & NVIDIA LLM configs
├── llm_client.py                 # Unified Dual-Engine (Groq -> NVIDIA Nemotron failover)
├── server.py                     # FastAPI routes: GET /, POST /api/search/candidates, POST /api/research
├── orchestrator.py               # Research orchestrator coordinating search, audit, and gaps
├── discovery/
│   ├── candidate_search.py       # [NEW] Name-based public candidate discovery engine
│   ├── search_client.py          # Tavily / DuckDuckGo live OSINT query client
│   ├── tier_classifier.py        # [UPDATE] Global sovereign (.gov, .nic.in, .edu) Tier-1 classifier
│   └── web_fetcher.py            # Async parallel web snippet extractor
├── extraction/
│   ├── claim_auditor.py          # Atomic proposition extractor using dual-engine LLM
│   └── materiality.py            # Financial, governance, and tenure materiality scorer
├── verification/
│   ├── double_checker.py         # [UPDATE] Two-stage entailment with global registry support
│   ├── contradiction.py          # Temporal and numerical counter-evidence detection
│   └── refusal_engine.py         # Adversarial quarantine engine (REF-01 to REF-05)
├── diagnosis/
│   ├── gap_synthesizer.py        # [UPDATE] Adaptive sector & jurisdiction gap synthesis
│   └── export.py                 # Executive Markdown & JSON dossier generators
├── storage/
│   ├── db.py                     # PostgreSQL / SQLite persistence manager
│   └── models.py                 # Pydantic models (CandidateMatch, Prospect, Claim, Gap)
└── templates/
    └── index.html                # [UPDATE] Candidate Confirmation Gate & Name Search UI
```

---

## Planned Implementation Phases

### Phase 0: Research & Architecture (Completed)
- Documented root causes of false-negative refusals on global figures.
- Designed name search and candidate confirmation workflow.
- Established regex standards for sovereign government and academic domains worldwide.
- Published [`research.md`](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/specs/002-name-search-verification/research.md).

### Phase 1: Design & Contracts (Completed)
- Defined data model updates: `CandidateMatch`, dynamic `Prospect` fields in [`data-model.md`](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/specs/002-name-search-verification/data-model.md).
- Authored OpenAPI contract in [`contracts/candidate-search-api.json`](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/specs/002-name-search-verification/contracts/candidate-search-api.json).
- Generated step-by-step test verification guide in [`quickstart.md`](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/specs/002-name-search-verification/quickstart.md).

### Phase 2: Implementation (Scheduled for `/speckit-implement`)
1. **Core Service Updates**:
   - Create `src/discovery/candidate_search.py` implementing `CandidateSearchEngine.search_candidates(name, keywords)`.
   - Update `src/discovery/tier_classifier.py` with universal sovereign government and education regex rules.
   - Update `src/verification/double_checker.py` to entail claims against global primary registers.
   - Update `src/diagnosis/gap_synthesizer.py` and `src/storage/models.py` with dynamic jurisdiction and sector fields.
2. **API & Orchestration**:
   - Expose `POST /api/search/candidates` in `src/server.py`.
   - Update `POST /api/research` to accept candidate metadata and prioritize official registry discovery queries.
3. **UI Enhancements (`src/templates/index.html`)**:
   - Add Name Search input with optional Context keywords.
   - Render the Candidate Confirmation Gate with candidate selection cards.
   - Keep direct URL input as an alternative tab.
   - Dynamically bind jurisdiction and sector chips in the Executive Diagnostic.
4. **Verification & Testing**:
   - Unit tests: `tests/unit/test_candidate_search.py` and `tests/unit/test_global_tiers.py`.
   - Integration tests: `tests/test_api.py`.
   - End-to-end browser tests in Chromium (`tests/run_browser_test.py`) verifying both Ronaldo Mouchawar and Narendra Modi workflows.
