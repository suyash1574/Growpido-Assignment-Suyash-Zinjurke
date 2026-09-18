# Tasks: Name-Based Prospect Search & Global Authority Verification

**Feature**: `002-name-search-verification`  
**Input**: Feature specification from `specs/002-name-search-verification/spec.md`, Implementation plan from `specs/002-name-search-verification/plan.md`  
**Status**: Ready for Implementation

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verification of core environment and model configuration

- [x] T001 Verify search configuration, Groq/NVIDIA Dual-Engine availability, and candidate search routing parameters in `src/config.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models and schema foundations required before implementing search and verification workflows

- [x] T002 Implement `CandidateMatch` Pydantic schema and add dynamic `sector` field to `Prospect` model in `src/storage/models.py`
- [x] T003 [P] Update database schema helpers to store and retrieve dynamic `sector` and `location_country` in `src/storage/db.py`

---

## Phase 3: User Story 1 - Name-Based Prospect Search & Human Confirmation Gate (Priority: P1) ⭐ MVP

**Goal**: Allow advisors to search prospects by name, review candidate profile matches, and confirm the right person before launching deep research.

**Independent Test**: Enter "Ronaldo Mouchawar" or "Narendra Modi" into name search; verify candidate cards are returned; select target and verify pipeline launches for that confirmed individual.

### Tests for User Story 1
- [x] T004 [P] [US1] Create unit tests for candidate search query construction and profile parsing in `tests/unit/test_candidate_search.py`

### Implementation for User Story 1
- [x] T005 [US1] Implement `CandidateSearchEngine` querying public search for business profiles and extracting candidate cards in `src/discovery/candidate_search.py`
- [x] T006 [US1] Implement `POST /api/search/candidates` endpoint in `src/server.py`
- [x] T007 [US1] Update `Orchestrator` to accept confirmed candidate metadata and populate initial prospect entity in `src/orchestrator.py`
- [x] T008 [US1] Add Name Search interface, search submission, and interactive Candidate Confirmation Gate cards in `src/templates/index.html`

**Checkpoint**: At this point, User Story 1 is fully functional: advisors can search by name, view matching candidates, and confirm target profile.

---

## Phase 4: User Story 2 - Global Sovereign Tier-1 Authority Grounding (Priority: P1)

**Goal**: Expand Tier-1 primary authority recognition to sovereign government registries, official gazettes, parliament portals, and accredited universities worldwide, eliminating false-negative `REF-01` quarantines for substantiated assertions.

**Independent Test**: Execute research on "Narendra Modi"; verify official government sources (`.gov.in`, `pmindia.gov.in`) are categorized as `TIER_1_PRIMARY`, Check 1 passes entailment, and the tenure assertion achieves `VERIFIED` status in the Fact Dossier.

### Tests for User Story 2
- [x] T009 [P] [US2] Create unit tests for universal sovereign government (`.gov`, `.gov.*`, `.nic.in`, `.mil`, `.parliament.*`) and education (`.edu`, `.ac.*`) tier classification in `tests/unit/test_global_tiers.py`

### Implementation for User Story 2
- [x] T010 [US2] Expand `TierClassifier.classify_tier` with universal sovereign government and accredited university regex patterns in `src/discovery/tier_classifier.py`
- [x] T011 [US2] Update `DoubleChecker.evaluate_check1_primary` in `src/verification/double_checker.py` to evaluate semantic entailment against discovered global Tier-1 primary records
- [x] T012 [US2] Update `Orchestrator.execute_research` in `src/orchestrator.py` to dynamically query official government and corporate registries based on prospect entity attributes

**Checkpoint**: At this point, User Stories 1 AND 2 are complete: search by name works, and substantiated public assertions for global leaders achieve verified status.

---

## Phase 5: User Story 3 - Adaptive Geography & Context-Aware Diagnostic Synthesis (Priority: P2)

**Goal**: Tailor the One-Page Executive Diagnostic and 3 Strategic Presence Gaps dynamically to the prospect's verified jurisdiction and sector, eliminating hardcoded UAE commercial sector assumptions.

**Independent Test**: Generate diagnostic for a non-UAE public or corporate leader; verify executive briefing subtitle and Strategic Presence Gaps reflect the prospect's actual operating domain and region.

### Tests for User Story 3
- [x] T013 [P] [US3] Create unit tests for adaptive jurisdiction and sector gap synthesis in `tests/unit/test_adaptive_gaps.py`

### Implementation for User Story 3
- [x] T014 [US3] Update `GapSynthesizer.synthesize_gaps` to dynamically incorporate prospect `location_country` and `sector` in `src/diagnosis/gap_synthesizer.py`
- [x] T015 [US3] Update diagnostic header, jurisdiction chips, and markdown export rendering in `src/templates/index.html` and `src/diagnosis/export.py`

**Checkpoint**: All three user stories are now fully implemented and integrated.

---

## Phase 6: Polish & Verification

**Purpose**: Cross-cutting testing, automated browser verification, and validation scenarios

- [x] T016 [P] Update API integration test suite covering `POST /api/search/candidates` and global tier checks in `tests/test_api.py`
- [x] T017 Update Playwright browser test script `tests/run_browser_test.py` to automate name search, candidate confirmation, and diagnostic compilation
- [x] T018 Execute validation scenarios from `quickstart.md` across both benchmark UAE target and global leader target

---

## Dependencies & Execution Order

### Phase Dependencies
1. **Phase 1 (Setup)**: Immediate start.
2. **Phase 2 (Foundational)**: Depends on Phase 1 — Blocks all User Stories.
3. **Phase 3 (User Story 1 - P1)**: Depends on Phase 2 — Deliverable MVP!
4. **Phase 4 (User Story 2 - P1)**: Depends on Phase 2 — Can proceed in parallel or after US1.
5. **Phase 5 (User Story 3 - P2)**: Depends on Phase 3 and Phase 4.
6. **Phase 6 (Polish & Verification)**: Depends on all user stories complete.

### Parallel Opportunities
- `T002` and `T003` can run in parallel.
- `T004` (US1 tests) and `T009` (US2 tests) can run in parallel.
- `T010` (Tier classifier) and `T005` (Candidate search) can be developed in parallel as they touch separate files.

---

## Implementation Strategy

### MVP Scope (User Story 1 + User Story 2)
1. Foundational data models (`CandidateMatch`, `Prospect.sector`).
2. Candidate search API + UI candidate confirmation gate.
3. Universal sovereign Tier-1 classification to fix false-negative refusals.
4. Validate with automated tests (`tests/test_api.py`).
