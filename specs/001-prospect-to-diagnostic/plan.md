# Implementation Plan: Prospect to Diagnostic Intelligence Engine

**Branch**: `001-prospect-to-diagnostic` | **Date**: 2026-09-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-prospect-to-diagnostic/spec.md`

---

## Summary
Build an adversarial, zero-hallucination OSINT intelligence pipeline that incepts a public UAE executive LinkedIn profile URL, performs real-time public web discovery, extracts atomic factual claims, conducts double-checked primary source verification against official registries/corporate domains, isolates uncorroborated claims into an explicit Refusal Log with causal reasons, identifies exactly three strategic presence gaps, and renders a professional One-Page Diagnostic backed by a Human Gate.

---

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Streamlit (Presentation UI), Groq SDK (Llama 3.3 70B Versatile for sub-second structured inference), Pydantic v2 (Strict Schema Enforcement), HTTPX / BeautifulSoup4 (Async Live Web Fetcher), Tavily / DuckDuckGo (Live OSINT Search)  
**Storage**: Embedded SQLite (local WAL mode) with PostgreSQL support via connection string toggle  
**Testing**: pytest with unit, integration, and golden end-to-end test suites  
**Target Platform**: Cross-platform (Windows, macOS, Linux, Docker container)  
**Project Type**: Agentic Web Service & Interactive Intelligence Application  
**Performance Goals**: End-to-end execution from LinkedIn URL to staged Human Gate in < 90 seconds (P95)  
**Constraints**: Pure live internet OSINT (no offline mock data substitution); zero credential scraping; 100% audit trail provenance  
**Scale/Scope**: Single executive per session; handles up to 20 concurrent discovery searches  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principle I (Accuracy Dominance)**: Adhered. 100% of claims in final diagnostic must pass double-check primary verification; uncorroborated claims are quarantined.
- [x] **Principle II (Two-Stage Verification)**: Check 1 (Primary Source Grounding) + Check 2 (Independent Corroboration & Contradiction Detection) enforced.
- [x] **Principle III (Mandatory Adversarial Refusal)**: Unverified claims excluded from diagnostic and assigned standard refusal codes (`REF-01` to `REF-05`) with causal explanations.
- [x] **Principle IV (Sovereign Human Gate)**: System prohibits autonomous diagnostic compilation; requires advisor inspection, override capability, and sign-off.
- [x] **Principle V (Strict Public OSINT & Zero Credential Policy)**: No LinkedIn login scraping, no CAPTCHA bypass, no automated prospect messaging.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-prospect-to-diagnostic/
├── spec.md              # Feature specification
├── plan.md              # This implementation plan
├── research.md          # Phase 0 technical choices and rationales
├── data-model.md        # Phase 1 domain entities and schemas
├── contracts/           # Phase 1 OpenAPI service contract
│   └── api-contract.json
├── quickstart.md        # Phase 1 validation and run guide
├── checklists/
│   └── requirements.md  # Specification quality checklist
└── tasks.md             # Phase 2 task decomposition (via /speckit-tasks)
```

### Source Code (repository layout)

```text
src/
├── app.py                      # Streamlit interactive application (Human Gate & Diagnostic)
├── orchestrator.py             # Pipeline state controller & workflow coordinator
├── discovery/
│   ├── search_client.py        # Live search provider client (Tavily / DuckDuckGo fallback)
│   ├── web_fetcher.py          # Async HTML fetcher and text tokenizer
│   └── tier_classifier.py      # Deterministic domain source tier classifier (Tiers 1-4)
├── extraction/
│   ├── claim_auditor.py        # Atomic claim extraction and categorization
│   └── materiality.py          # Materiality ranking (High, Medium, Low)
├── verification/
│   ├── double_checker.py       # Two-stage primary verification engine (Checks 1 & 2)
│   ├── contradiction.py        # Contradiction and divergence detection
│   └── refusal_engine.py       # Adversarial refusal and reason code generator
├── diagnosis/
│   ├── gap_synthesizer.py      # 3-Gap strategic presence engine
│   └── diagnostic_renderer.py  # One-Page Diagnostic and PDF/Markdown exporter
└── storage/
    ├── db.py                   # Unified database client (SQLite / PostgreSQL)
    └── models.py               # Pydantic schemas and table definitions

tests/
├── test_ingest.py              # Ingestion & URL validation tests
├── test_discovery.py           # Source tier classification tests
├── test_verification.py        # Double-check verification & contradiction tests
├── test_refusal.py             # Adversarial refusal & reason code tests
├── test_gap_synthesizer.py     # 3-gap triad ranking tests
└── test_e2e.py                 # End-to-end candidate golden test
```

---

## Phase 0 & Phase 1 Execution Artifacts Complete
- `research.md`: Resolved all architectural and technical decisions (Groq Llama 3.3 70B, live internet OSINT, SQLite/PostgreSQL, double-check logic).
- `data-model.md`: Defined domain models (`Prospect`, `EvidenceSource`, `Claim`, `StrategicGap`, `AuditEvent`) and ERD.
- `contracts/api-contract.json`: Specified OpenAPI 3.1 contracts for `/research`, `/claims`, `/override`, and `/diagnostic`.
- `quickstart.md`: Outlined test execution and Streamlit verification scenarios.
