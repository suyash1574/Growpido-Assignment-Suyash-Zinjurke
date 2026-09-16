# Test Plan & Test Cases
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Test Strategy Overview
The Growpido Engine test suite proves that our system deterministically satisfies every functional requirement, rubric criterion, and edge case. The suite combines unit testing, adversarial synthetic test fixtures, integration tests against live/mocked OSINT responses, and end-to-end diagnostic evaluation.

---

### 2. Test Execution Matrix by Rubric Category

| Test Suite | Rubric Target | Scope & Objective |
| :--- | :--- | :--- |
| **TS-01: Ingest & Parser** | Operational Robustness | Validates URL normalization, malicious string injection prevention, and slug parsing. |
| **TS-02: Source Hierarchy** | 20 pts (Judgement) | Proves deterministic classification of Tier 1 through Tier 4 sources. |
| **TS-03: Double Verification** | 25 pts (Fact Integrity) | Tests two-stage verification, semantic entailment gates, and independent source validation. |
| **TS-04: Contradiction Engine**| 25 pts (Fact Integrity) | Proves conflicting data points are caught and prevented from achieving `VERIFIED` status. |
| **TS-05: Adversarial Refusal** | 10 pts (Honest Paragraph/Refusal)| Validates rejection taxonomy, standardized reason codes, and refusal isolation. |
| **TS-06: 3-Gap Synthesizer** | 10 pts (Output Quality) | Verifies exact generation of three prioritized strategic gaps across the 3 core dimensions. |
| **TS-07: Human Gate** | 15 pts (Human Gate) | Validates advisor review workflows, manual status overrides, and audit log generation. |
| **TS-08: End-to-End Golden** | 20 pts (Does It Run) | Full pipeline execution from candidate LinkedIn URL to printable One-Page Diagnostic. |

---

### 3. Detailed Test Cases

#### TS-01: Ingestion & Target Resolution
- **TC-ING-001 (Valid Public URL):**
  - *Input:* `https://www.linkedin.com/in/ronaldo-mouchawar-souq`
  - *Expected:* Clean slug `ronaldo-mouchawar-souq`, status `INITIALIZED`, no error.
- **TC-ING-002 (Malformed & Gated URLs):**
  - *Input:* `https://linkedin.com/feed/`, `ftp://evil.com`, `javascript:alert(1)`
  - *Expected:* Validation error `ERR_INVALID_PROFILE_URL`, execution blocked.

#### TS-02: Source Tier Classification
- **TC-SRC-001 (Tier 1 Primary Detection):**
  - *Input URL:* `https://www.adgm.com/public-registers/companies/record-1234`
  - *Expected:* `SourceTier.TIER_1_PRIMARY`.
- **TC-SRC-002 (Tier 2 Financial Press Detection):**
  - *Input URL:* `https://www.bloomberg.com/news/articles/2021-05-12/amazon-souq-mena`
  - *Expected:* `SourceTier.TIER_2_SECONDARY`.
- **TC-SRC-003 (Tier 3 Aggregator Quarantine):**
  - *Input URL:* `https://en.wikipedia.org/wiki/Ronaldo_Mouchawar`
  - *Expected:* `SourceTier.TIER_3_AGGREGATOR` (Disallowed from primary verification).

#### TS-03: Double-Check Verification Integrity (Fact Integrity)
- **TC-VER-001 (Official Primary Source Corroborated):**
  - *Claim:* "Co-founded Souq.com in 2005."
  - *Source 1:* `amazon.ae` corporate history (Tier 1).
  - *Source 2:* `adgm.com` / `reuters.com` (Tier 1/2 corroboration).
  - *Expected:* Check 1 = True, Check 2 = True, Contradiction = False ➔ `VERIFIED`.
- **TC-VER-002 (Secondary Source Only — Partial):**
  - *Claim:* "Attended regional retail forum as opening keynote speaker in 2022."
  - *Source 1:* `arabianbusiness.com` event report (Tier 2).
  - *Expected:* Check 1 = True (Tier 2), Check 2 = True ➔ `PARTIALLY_VERIFIED`.
- **TC-VER-003 (Aggregator-Only Source — Unverified):**
  - *Claim:* "Favorite hobby is vintage car restoration."
  - *Source 1:* Unverified bio aggregator blog (Tier 3).
  - *Expected:* Check 1 = False ➔ `UNVERIFIED` ➔ Sent to Refusal Engine.

#### TS-04: Contradiction Detection
- **TC-CON-001 (Conflicting Founding Dates):**
  - *Claim:* "Founded Souq.com in 2005."
  - *Snippet A:* "Mouchawar established Souq.com in late 2005."
  - *Snippet B:* "Souq.com, launched in 2007 by Mouchawar..."
  - *Expected:* Contradiction Flag = `True` ➔ Status downgraded to `PARTIALLY_VERIFIED`, alert sent to Human Gate.

#### TS-05: Adversarial Refusal & Reason Logging
- **TC-REF-001 (Unsubstantiated Financial Metric):**
  - *Claim:* "Personally manages a $50M personal tech venture portfolio."
  - *Evidence:* Blog quote only; zero regulatory disclosures.
  - *Expected Result:*
    - Claim excluded from final diagnostic.
    - Added to Refusal Log with Code `REF-01 (NO_PRIMARY_EVIDENCE)`.
    - Rationale explicitly cites lack of ADGM/DIFC/corporate filings.

#### TS-06: Three-Gap Synthesis Validation
- **TC-GAP-001 (Exact Triad Output):**
  - *Input:* 6 verified claims + digital presence footprint.
  - *Expected Result:* Exactly 3 gaps returned, mapped respectively to:
    1. `AUTHORITY_UNDER_INDEXING`
    2. `CHANNEL_DIVERSITY_DEFICIT`
    3. `NARRATIVE_FRAGMENTATION`
    - Gaps contain concrete evidence, commercial impact statement, and Growpido advisory recommendation.

#### TS-07: Human Gate Workflow & Audit Ledger
- **TC-HGT-001 (Advisor Status Override):**
  - *Action:* Advisor manually changes claim status from `PARTIALLY_VERIFIED` to `VERIFIED` with comment "Confirmed via direct primary company disclosure".
  - *Expected Result:* Claim updated, audit event logged with timestamp and advisor ID, final diagnostic renders updated status.

#### TS-08: Complete System Run (Track B Candidate Golden Test)
- **TC-E2E-001 (Full Candidate Run):**
  - *Candidate:* Ronaldo Mouchawar (UAE-based tech leader).
  - *Execution:* Ingest ➔ OSINT Search ➔ Claim Audit ➔ Double-Check ➔ Refusal ➔ Gap Synthesis ➔ Human Gate ➔ Render.
  - *Expected Result:*
    - Engine runs smoothly in < 90 seconds.
    - Produces One-Page Diagnostic with verified claims.
    - Demonstrates 1 refused claim with transparent rationale.
    - Output matches Track B assessment brief requirements 100%.
