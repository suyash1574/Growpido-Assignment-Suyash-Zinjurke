# Growpido Track B Evaluation Rubric Mapping Matrix
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Document Purpose
This document provides an unambiguous, transparent scoring breakdown mapping the official Growpido Track B evaluation criteria directly to our architectural implementations, concrete code artifacts, verification mechanics, and test suites.

---

### 2. Master Rubric Alignment Table (Total: 100 Points)

| Rubric Criterion | Max Points | Core Requirement from Brief | Our Implementation & Architectural Evidence | Cross-Reference Documents |
| :--- | :---: | :--- | :--- | :--- |
| **Fact Integrity** | **25** | Verifies every factual claim against a primary source, and checks it twice. Distinguishes verified, partially verified, and unverified. | • Strict 4-Tier Source Hierarchy (Tier 1 Gov/Registry/Corporate).<br>• Double-Check Protocol: Check 1 (Primary Entailment) + Check 2 (Corroboration/Contradiction).<br>• Deterministic 3-State Classifier Hub (`VERIFIED`, `PARTIALLY_VERIFIED`, `UNVERIFIED`).<br>• Adversarial Refusal Engine quarantines uncorroborated assertions. | [03_FRD.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/03_FRD.md)<br>[11_VERIFICATION_SPEC.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/11_VERIFICATION_SPEC.md)<br>[12_TEST_PLAN.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/12_TEST_PLAN.md) |
| **Does It Run** | **20** | A real, working system starting from a LinkedIn URL and executing end-to-end. | • Modular Python 3.11+ application with reactive Streamlit UI.<br>• Async HTTP engine with SQLite state persistence.<br>• Resilient multi-search fallback (Tavily + DuckDuckGo).<br>• One-click Docker containerization and clean `.env` config. | [05_SRD.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/05_SRD.md)<br>[06_HLD.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/06_HLD.md)<br>[16_DEPLOYMENT.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/16_DEPLOYMENT.md) |
| **Judgement** | **20** | Soundness of candidate choice, depth of research, and quality of presence gaps. | • Candidate Selection: Ronaldo Mouchawar (VP Amazon MENA / Co-founder Souq.com), a titan of UAE tech with complex public footprint.<br>• Triad Gap Framework: Authority Under-Indexing, Channel Deficit, Narrative Fragmentation.<br>• Materiality Scoring (High, Medium, Low) prevents trivial bio noise. | [01_BRD.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/01_BRD.md)<br>[02_PRD.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/02_PRD.md)<br>[04_FRS.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/04_FRS.md) |
| **Human Gate** | **15** | Human sign-off / editorial checkpoint before finalizing intelligence. | • Interactive Human Gate review table built into the Streamlit flow.<br>• Side-by-side evidence snippet and URL inspection.<br>• Manual status override with mandatory audit rationale note.<br>• Explicit "Approve & Compile" gate unlocking final diagnostic. | [03_FRD.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/03_FRD.md)<br>[07_LLD.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/07_LLD.md)<br>[10_AI_AGENT_SPEC.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/10_AI_AGENT_SPEC.md) |
| **Output Quality** | **10** | Clear, executive-ready One-Page Diagnostic consumable by leadership. | • Structured single-page visual hierarchy.<br>• Executive summary, verified facts table, 3 strategic gaps, and refusal log.<br>• Color-coded verification badges and direct source citation chips.<br>• Exportable as GitHub-flavored Markdown and printable PDF. | [04_FRS.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/04_FRS.md)<br>[08_API_SPEC.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/08_API_SPEC.md)<br>[17_LOOM_SCRIPT.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/17_LOOM_SCRIPT.md) |
| **Honest Paragraph** | **10** | Self-awareness of limitations, edge cases, what broke, and future iteration. | • Explicit "Honest Paragraph" disclosing regional API throttling, Arabic PDF/OCR constraints, and temporal ambiguity in secondary press.<br>• Clear engineering roadmap (v1.1 to v1.4) addressing each identified technical debt item. | [15_FAILURE_HANDLING.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/15_FAILURE_HANDLING.md)<br>[18_LIMITATIONS.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/18_LIMITATIONS.md) |
| **Total** | **100** | Full Rubric Compliance | Fully traceable from Business Requirements down to Test Cases and Loom Video Script. | [13_TRACEABILITY_MATRIX.md](file:///d:/Projects/Self%20Improvement%20Hackathon%20project/Growpido/docs/13_TRACEABILITY_MATRIX.md) |

---

### 3. Verification of Core Track B Mandates

#### Mandate A: Ingestion from LinkedIn URL
- **Trace:** `BR-FACT-001` ➔ `PRD-FEAT-001` ➔ `FR-ING-001` ➔ `IngestService.validate_url()`.
- **Implementation:** Clean regex validation, slug parsing, and non-credential OSINT query expansion.

#### Mandate B: Verification Against Primary Source (Double-Checked)
- **Trace:** `BR-FACT-002` ➔ `PRD-FEAT-004/005` ➔ `FR-VER-001/003` ➔ `VerificationService.verify_claim()`.
- **Implementation:** Tier-1 primary source whitelist matching (Check 1) + independent domain corroboration and contradiction check (Check 2).

#### Mandate C: Three-State Labeling
- **Trace:** `BR-FACT-003` ➔ `PRD-FEAT-006` ➔ `FR-VER-005` ➔ `ClassifierHub`.
- **Implementation:** `VERIFIED`, `PARTIALLY_VERIFIED`, and `UNVERIFIED` tags displayed with clear visual badges.

#### Mandate D: Three Biggest Gaps
- **Trace:** `BR-GAP-001` ➔ `PRD-FEAT-008` ➔ `FR-GAP-001` ➔ `DiagnosticService.synthesize_gaps()`.
- **Implementation:** Grounded analysis yielding: (1) Authority Under-Indexing, (2) Channel Diversity Deficit, (3) Narrative Fragmentation.

#### Mandate E: One-Page Diagnostic Output
- **Trace:** `BR-OUT-001` ➔ `PRD-FEAT-010` ➔ `FR-OUT-001` ➔ `DiagnosticRenderer.render_one_page()`.
- **Implementation:** High-density, executive-ready single-page layout.

#### Mandate F: Refused Claim + Causal Rationale
- **Trace:** `BR-FACT-004` ➔ `PRD-FEAT-007` ➔ `FR-REF-001/002` ➔ `RefusalService.process_exclusions()`.
- **Implementation:** Demonstration of excluded $50M angel portfolio claim with Code `REF-01` and formal explanation pursuant to Rule BR-R01.
