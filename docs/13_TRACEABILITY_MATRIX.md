# Requirements Traceability Matrix (RTM)
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Traceability Purpose & Architecture
The Requirements Traceability Matrix (RTM) establishes bidirectional traceability across the entire software development lifecycle:
$$\text{Business Need (BRD)} \longleftrightarrow \text{Product Feature (PRD)} \longleftrightarrow \text{Functional Requirement (FRD)} \longleftrightarrow \text{Detailed Spec (FRS)} \longleftrightarrow \text{System Requirement (SRD)} \longleftrightarrow \text{Component Class} \longleftrightarrow \text{Test Case (TC)}$$

This guarantees that every line of code directly serves a business goal and every rubric criterion is validated by automated tests.

---

### 2. Master Traceability Matrix

| BRD ID | PRD ID | FRD ID | FRS ID | SRD ID | System Component / Service | Test Case ID | Rubric Dimension |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BR-FACT-001** | PRD-FEAT-004 | FR-VER-001 | FRS-VER-001 | NFR-DET-001 | `VerificationService.verify_claim()` | **TC-VER-001** | Fact Integrity (25 pts) |
| **BR-FACT-002** | PRD-FEAT-005 | FR-VER-003 | FRS-VER-001 | NFR-DET-001 | `VerificationService.check_twice()` | **TC-VER-001** | Fact Integrity (25 pts) |
| **BR-FACT-003** | PRD-FEAT-006 | FR-VER-005 | FRS-VER-001 | NFR-DET-001 | `ClassifierHub` | **TC-VER-002** | Judgement (20 pts) |
| **BR-FACT-004** | PRD-FEAT-007 | FR-REF-001 | FRS-REF-001 | NFR-SEC-001 | `RefusalService.process_exclusions()` | **TC-REF-001** | Honest Paragraph (10 pts) |
| **BR-GAP-001** | PRD-FEAT-008 | FR-GAP-001 | FRS-GAP-001 | NFR-PERF-001| `DiagnosticService.synthesize_gaps()`| **TC-GAP-001** | Judgement (20 pts) |
| **BR-OUT-001** | PRD-FEAT-010 | FR-OUT-001 | FRS-GAP-001 | NFR-PERF-001| `DiagnosticRenderer.render_one_page()`| **TC-E2E-001** | Output Quality (10 pts) |
| **BR-GOV-001** | PRD-FEAT-009 | FR-HGT-001 | FRS-HGT-001 | NFR-AUD-001 | `HumanGateUI.render_review_table()` | **TC-HGT-001** | Human Gate (15 pts) |
| **BR-AUD-001** | PRD-FEAT-011 | FR-OUT-003 | FRS-HGT-001 | NFR-AUD-001 | `AuditService.log_event()` | **TC-HGT-001** | Operational Run (20 pts) |
| **BR-R01** | PRD-FEAT-007 | FR-REF-002 | FRS-REF-001 | NFR-DET-001 | `VerificationService.enforce_accuracy()`| **TC-REF-001** | Fact Integrity (25 pts) |
| **BR-R02** | PRD-FEAT-002 | FR-DIS-002 | FRS-DIS-001 | NFR-DET-001 | `DiscoveryService.classify_tier()` | **TC-SRC-001** | Judgement (20 pts) |
| **BR-R03** | PRD-FEAT-006 | FR-VER-004 | FRS-VER-001 | NFR-DET-001 | `VerificationService.detect_contradiction()`| **TC-CON-001** | Fact Integrity (25 pts) |
| **BR-R04** | PRD-FEAT-007 | FR-REF-003 | FRS-REF-001 | NFR-AUD-001 | `RefusalService.export_refusal_log()` | **TC-REF-001** | Honest Paragraph (10 pts) |

---

### 3. Traceability Chain Breakdown Examples

#### Chain 1: Primary Source Double-Check Verification
$$\text{BR-FACT-001 / 002} \longrightarrow \text{PRD-FEAT-004 / 005} \longrightarrow \text{FR-VER-001 / 003} \longrightarrow \text{FRS-VER-001} \longrightarrow \text{VerificationService} \longrightarrow \text{TC-VER-001}$$
- **Verification Rule:** Tier-1 source grounding confirmed via regex/semantic match, followed by independent corroboration check. If either fails, claim drops out of `VERIFIED` status.

#### Chain 2: Adversarial Refusal Mechanism
$$\text{BR-FACT-004} \longrightarrow \text{PRD-FEAT-007} \longrightarrow \text{FR-REF-001 / 002} \longrightarrow \text{FRS-REF-001} \longrightarrow \text{RefusalService} \longrightarrow \text{TC-REF-001}$$
- **Verification Rule:** Unverified claims are quarantined, categorized with standardized refusal reason codes (`REF-01` to `REF-04`), and rendered in the explicit Refusal Log.

#### Chain 3: Strategic Presence Three-Gap Engine
$$\text{BR-GAP-001} \longrightarrow \text{PRD-FEAT-008} \longrightarrow \text{FR-GAP-001 / 002} \longrightarrow \text{FRS-GAP-001} \longrightarrow \text{DiagnosticService} \longrightarrow \text{TC-GAP-001}$$
- **Verification Rule:** Verified achievements are benchmarked against public presence to generate exactly 3 prioritized presence gaps across Authority, Channel, and Narrative dimensions.
