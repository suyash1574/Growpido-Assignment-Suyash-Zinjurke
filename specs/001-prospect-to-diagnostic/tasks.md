# Tasks: Prospect to Diagnostic Intelligence Engine

**Feature**: `001-prospect-to-diagnostic`  
**Date**: 2026-09-16  
**Status**: Ready for Execution  
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Data Model**: [data-model.md](data-model.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, directory structure, and dependencies.

- [ ] T001 Create source directories `src/discovery`, `src/extraction`, `src/verification`, `src/diagnosis`, `src/storage`, and `tests/` per implementation plan
- [ ] T002 Configure Python runtime dependencies in `requirements.txt` (`streamlit`, `groq`, `pydantic`, `httpx`, `beautifulsoup4`, `psycopg2-binary`, `pytest`)
- [ ] T003 [P] Configure environment settings and secret loading in `src/config.py` loading `GROQ_API_KEY`, `GROQ_MODEL`, and search keys from `.env`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models, database repository, and basic HTTP client infrastructure.

- [ ] T004 Create Pydantic domain models in `src/storage/models.py` (`Prospect`, `EvidenceSource`, `Claim`, `StrategicGap`, `AuditEvent`) per `data-model.md`
- [ ] T005 Implement dual SQLite/PostgreSQL persistence engine in `src/storage/db.py` with table creation, connection pooling, and schema initialization
- [ ] T006 [P] Implement audit event logger in `src/storage/audit.py` writing immutable timestamped events to database
- [ ] T007 [P] Implement async HTTP web fetcher and text tokenizer in `src/discovery/web_fetcher.py` with sanitization, content-hashing (SHA-256), and timeout handling
- [ ] T008 Implement live OSINT search provider in `src/discovery/search_client.py` querying live search (Tavily/DuckDuckGo) with explicit `ERR_LIVE_SEARCH_FAILED` on failure (no offline mocks)
- [ ] T009 [P] Implement deterministic domain tier classifier in `src/discovery/tier_classifier.py` mapping domains to Tiers 1 through 4

**Checkpoint**: Core foundation and data models ready — user story implementation can begin.

---

## Phase 3: User Story 1 - Public Target Ingestion & Primary Source Double-Check Verification (Priority: P1) 🎯 MVP

**Goal**: Ingest public LinkedIn URL, discover live public records, extract atomic claims, execute two-stage double-check primary verification, and label each claim (`VERIFIED`, `PARTIALLY_VERIFIED`, `UNVERIFIED`).

**Independent Test**: Run `pytest tests/test_verification.py` verifying a known UAE executive profile (`ronaldo-mouchawar-souq`), asserting that all extracted claims are verified against primary records (such as corporate filings and government registries), and confirming that every finding carries one of the three required verification labels with citation links.

### Tests for User Story 1
- [ ] T010 [P] [US1] Unit test for URL validation and slug parsing in `tests/test_ingest.py`
- [ ] T011 [P] [US1] Unit test for source tier classification in `tests/test_discovery.py`
- [ ] T012 [P] [US1] Integration test for double-check primary verification and contradiction detection in `tests/test_verification.py`

### Implementation for User Story 1
- [ ] T013 [P] [US1] Implement LinkedIn URL validator and canonical slug parser in `src/discovery/ingest.py`
- [ ] T014 [US1] Implement atomic claim extractor and category classifier in `src/extraction/claim_auditor.py` using Groq Llama 3.3 70B structured outputs
- [ ] T015 [P] [US1] Implement claim materiality scorer in `src/extraction/materiality.py` (High/Medium/Low)
- [ ] T016 [US1] Implement Check 1 (Primary Source Grounding & Entailment >= 0.85) in `src/verification/double_checker.py`
- [ ] T017 [US1] Implement Check 2 (Independent Corroboration & Consistency) and contradiction detector in `src/verification/contradiction.py`
- [ ] T018 [US1] Implement 3-state classifier hub in `src/verification/classifier_hub.py` assigning `VERIFIED`, `PARTIALLY_VERIFIED`, or `UNVERIFIED`

**Checkpoint**: User Story 1 is fully functional. Claims can be ingested, extracted, and verified double-checked against live web sources.

---

## Phase 4: User Story 2 - Adversarial Claim Refusal with Causal Justification (Priority: P2)

**Goal**: Exclude unverified or contradictory material claims from the core diagnostic and produce an explicit Refusal Log demonstrating why each was refused.

**Independent Test**: Run `pytest tests/test_refusal.py` asserting that an uncorroborated third-party claim (e.g., "$50M personal angel portfolio") is quarantined from the diagnostic and assigned code `REF-01` with a detailed causal explanation.

### Tests for User Story 2
- [ ] T019 [P] [US2] Unit test for refusal codes and explanation generation in `tests/test_refusal.py`

### Implementation for User Story 2
- [ ] T020 [US2] Implement refusal taxonomy and exclusion processor in `src/verification/refusal_engine.py` supporting codes `REF-01` to `REF-05`
- [ ] T021 [US2] Implement refusal ledger formatter and audit serialization in `src/verification/refusal_engine.py`

**Checkpoint**: User Story 2 complete. The system actively refuses unverified claims with complete causal transparency.

---

## Phase 5: User Story 3 - Three Strategic Public Presence Gaps Identification (Priority: P3)

**Goal**: Synthesize verified facts against public visibility to identify and rank exactly three strategic presence gaps (Authority Under-Indexing, Channel Diversity Deficit, Narrative Fragmentation).

**Independent Test**: Run `pytest tests/test_gap_synthesizer.py` verifying that exactly 3 prioritized gaps are generated with commercial impact and actionable Growpido advisory recommendations.

### Tests for User Story 3
- [ ] T022 [P] [US3] Unit test for three-gap synthesis and dimension ranking in `tests/test_gap_synthesizer.py`

### Implementation for User Story 3
- [ ] T023 [US3] Implement 3-gap presence analyzer in `src/diagnosis/gap_synthesizer.py` using Groq Llama 3.3 70B
- [ ] T024 [US3] Implement executive strategic recommendation generator in `src/diagnosis/gap_synthesizer.py`

**Checkpoint**: User Story 3 complete. Exactly three high-leverage presence gaps are generated for the prospect.

---

## Phase 6: User Story 4 - Sovereign Human-in-the-Loop Review Gate (Priority: P4)

**Goal**: Provide an interactive staging interface where advisors inspect evidence snippets, check contradiction warnings, override statuses with audit comments, and approve report compilation.

**Independent Test**: Launch Streamlit UI, perform a manual override on a flagged claim with comment, and verify that the override is recorded in `audit_log` and reflected in the diagnostic.

### Implementation for User Story 4
- [ ] T025 [US4] Implement interactive Human Gate staging table in `src/ui/human_gate.py` displaying claims, citation chips, and contradiction alerts
- [ ] T026 [US4] Implement manual override action handler with mandatory rationale comment input in `src/ui/human_gate.py`
- [ ] T027 [US4] Implement advisor sign-off authorization lock (`Approve & Compile Diagnostic`) in `src/ui/human_gate.py`

**Checkpoint**: User Story 4 complete. Advisors have sovereign sign-off authority before final output generation.

---

## Phase 7: User Story 5 - One-Page Executive Diagnostic Delivery & Audit Export (Priority: P5)

**Goal**: Render a clean, executive-ready One-Page Diagnostic and exportable audit trail.

**Independent Test**: Compile approved diagnostic for Ronaldo Mouchawar and verify that the layout fits single-page density, shows verified facts, 3 gaps, the refused claim, and exports valid Markdown/JSON.

### Implementation for User Story 5
- [ ] T028 [US5] Implement One-Page Diagnostic renderer in `src/diagnosis/diagnostic_renderer.py`
- [ ] T029 [US5] Implement Streamlit executive diagnostic presentation card view in `src/ui/diagnostic_view.py`
- [ ] T030 [US5] Implement export routines (Markdown and JSON audit trail) in `src/diagnosis/export.py`

**Checkpoint**: User Story 5 complete. Full C-suite diagnostic deliverable is rendered and exportable.

---

## Phase 8: Orchestration, Polish & Golden Run

**Purpose**: End-to-end integration, main application runner, and golden rubric validation.

- [ ] T031 Implement end-to-end pipeline coordinator in `src/orchestrator.py` chaining Ingest ➔ Discovery ➔ Extraction ➔ Verification ➔ Refusal ➔ Gaps ➔ Human Gate ➔ Diagnostic
- [ ] T032 Build primary Streamlit application in `src/app.py` tying together input URL form, live progress indicators, Human Gate, and One-Page Diagnostic
- [ ] T033 Implement end-to-end candidate golden test in `tests/test_e2e.py` testing Ronaldo Mouchawar's public profile
- [ ] T034 [P] Update documentation and verify all tests pass with `pytest tests/ -v`

---

## Dependencies & Execution Order

```
[Phase 1: Setup] ──► [Phase 2: Foundational]
                             │
                             ▼
         [Phase 3: User Story 1 (P1 - Verification MVP)]
                             │
                             ▼
         [Phase 4: User Story 2 (P2 - Refusal Engine)]
                             │
                             ▼
         [Phase 5: User Story 3 (P3 - Strategic 3-Gaps)]
                             │
                             ▼
         [Phase 6: User Story 4 (P4 - Human Gate)]
                             │
                             ▼
         [Phase 7: User Story 5 (P5 - One-Page Diagnostic)]
                             │
                             ▼
         [Phase 8: Orchestration & Golden Run]
```

---

## Implementation Strategy & MVP

1. **Step 1 (MVP Delivery)**: Implement Phase 1, Phase 2, and Phase 3 (US1). Validate that LinkedIn URL ingestion extracts claims and validates them double-checked against live web primary sources.
2. **Step 2 (Refusal & Gaps)**: Implement Phase 4 (US2) and Phase 5 (US3) to add the adversarial refusal engine and 3 presence gaps.
3. **Step 3 (Human Gate & Delivery)**: Implement Phase 6 (US4) and Phase 7 (US5) to provide the Streamlit review dashboard and One-Page Diagnostic.
4. **Step 4 (Final Polish)**: Implement Phase 8 and execute the complete golden test suite for Ronaldo Mouchawar.
