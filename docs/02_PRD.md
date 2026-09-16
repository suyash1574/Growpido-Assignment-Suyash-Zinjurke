# Product Requirements Document (PRD)
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Product Vision
To build the most trusted, adversarial, and fact-grounded executive intelligence engine for Growpido advisors. The product transforms an executive's public LinkedIn URL into a high-stakes, audit-backed One-Page Strategic Diagnostic while systematically refusing uncorroborated, hallucinated, or contradictory claims.

---

### 2. Product Goals
- **G-01:** Automate deep OSINT research on UAE-based founders, CEOs, and fund managers in under 2 minutes.
- **G-02:** Eliminate LLM hallucinations through a closed-loop, two-stage primary verification engine.
- **G-03:** Provide an adversarial refusal mechanism that flags and isolates ungrounded assertions with full transparency.
- **G-04:** Compute exactly three high-leverage presence gaps comparing verified achievements with public executive positioning.
- **G-05:** Empower Growpido advisors with an interactive Human Gate to review and approve claims before generating the final diagnostic.

---

### 3. User Personas
#### Persona 1: Tariq Al-Mansoor — Senior Growth Partner at Growpido
- **Goal:** Prepare for an introductory advisory meeting with a prominent DIFC venture fund manager.
- **Needs:** Bulletproof facts (AUM, portfolio exits, board seats) and sharp positioning critique without factual inaccuracies that could ruin rapport.
- **Pain Point:** Cannot spend 3 hours verifying press releases or risk quoting an unverified PR fluff claim.

#### Persona 2: Maya Chen — Executive Intelligence Research Analyst
- **Goal:** Audit engine findings, inspect flagged discrepancies, and validate source provenance.
- **Needs:** A high-speed Human Gate interface with side-by-side evidence inspection, diff views, and one-click override capabilities.

#### Persona 3: Rashid Al-Nuaimi — Target Prospect (Tech CEO, Dubai)
- **Goal:** Understand his market perception and strategic executive branding gaps.
- **Needs:** A clear, elegant, scannable one-page diagnostic highlighting actionable visibility deficiencies.

---

### 4. End-to-End User Journey
```
[Advisor Inputs LinkedIn URL]
            │
            ▼
[OSINT Agent Discovers Footprint & Public Records]
            │
            ▼
[Claim Auditor Extracts Atomic Factual Claims]
            │
            ▼
[Double-Check Primary Source Verification Engine]
            │
    ┌───────┴────────┐
    ▼                ▼
[Verified Claims]  [Refused / Flagged Claims + Rationale]
    └───────┬────────┘
            ▼
[Strategic Presence Gap Engine (Synthesizes 3 Gaps)]
            │
            ▼
[Human Review Gate (Advisor Confirms / Overrides)]
            │
            ▼
[Export One-Page Diagnostic PDF/Markdown + Audit Log]
```

---

### 5. Product Scope & Functional Feature Matrix

| Feature Module | Feature ID | Feature Name | Description | Priority |
| :--- | :--- | :--- | :--- | :--- |
| **Ingestion** | PRD-FEAT-001 | Public Profile Ingest | Accepts standard LinkedIn URL format; parses slug/identifier without requiring login credentials. | P0 (Must Have) |
| **Discovery** | PRD-FEAT-002 | Multi-Tier Search | Crawls Google, Bing, DIFC/ADGM registries, company domains, press releases. | P0 (Must Have) |
| **Extraction** | PRD-FEAT-003 | Atomic Claim Decomp | Breaks bio into discrete atomic claims: Tenure, Education, Funding, Awards, Governance. | P0 (Must Have) |
| **Verification**| PRD-FEAT-004 | Tier-1 Primary Anchor | Matches claim against regulatory, official registry, or company source. | P0 (Must Have) |
| **Verification**| PRD-FEAT-005 | Double-Check Corrob | Second independent verification verifying consistency and absence of dispute. | P0 (Must Have) |
| **Classification**| PRD-FEAT-006| 3-State Tagging | Categorizes claims into `VERIFIED`, `PARTIALLY_VERIFIED`, `UNVERIFIED`. | P0 (Must Have) |
| **Refusal** | PRD-FEAT-007 | Adversarial Refusal | Explicitly excludes uncorroborated claims and outputs refusal rationale. | P0 (Must Have) |
| **Gap Engine** | PRD-FEAT-008 | Three-Gap Diagnosis | Ranks public narrative gaps across: Authority, Channel Presence, Strategic Voice. | P0 (Must Have) |
| **Human Gate** | PRD-FEAT-009 | Reviewer Dashboard | Interactive UI to review, accept, reject, or edit claims prior to export. | P0 (Must Have) |
| **Delivery** | PRD-FEAT-010 | One-Page Diagnostic | Clean executive summary sheet (Web + Exportable PDF/MD). | P0 (Must Have) |
| **Audit** | PRD-FEAT-011 | Full Audit Trail | JSON ledger recording every source URL, query, timestamp, and verification check. | P1 (Should Have) |
| **Reputation** | PRD-FEAT-012 | Sentiment & Signals | Analysis of press sentiment, controversy flags, and quote frequency. | P1 (Should Have) |
| **Monitoring** | PRD-FEAT-013 | Rate-Limit & Fallback | Graceful fallback when search providers throttle or return empty responses. | P1 (Should Have) |

---

### 6. MVP vs. Stretch Scope Definition
#### MVP (Mandatory Deliverable):
- Input: UAE executive LinkedIn URL.
- Live public discovery & claim extraction.
- Double-check primary source verification.
- Explicit Refusal Log (demonstrating why at least one claim was refused).
- 3 strategic presence gaps calculated.
- Human review interactive step.
- Polished One-Page Diagnostic UI output.

#### Stretch (Post-Hackathon):
- Automated continuous monitoring & change alerts for executive profiles.
- Multilingual Arabic-to-English legal registry cross-referencing (UAE MoE).
- Dynamic pitch-deck generator based on diagnostic findings.

---

### 7. User Stories
- **US-01:** As a Growpido advisor, I want to submit a prospect's public LinkedIn URL so that the system automatically gathers public footprint data without me doing manual searches.
- **US-02:** As an advisor, I want every claim verified against a primary source twice so that I never embarrass myself or Growpido with false facts in front of a CEO.
- **US-03:** As an advisor, I want to see which claims the system refused to include and why so that I have complete transparency into unverified rumors or PR puffery.
- **US-04:** As an advisor, I want the system to identify exactly three prominent gaps in how the prospect shows up so that I can lead the sales pitch with high-value advisory insights.
- **US-05:** As a research auditor, I want a Human Gate screen where I can review flagged contradictions and approve the diagnostic before it is published.

---

### 8. UX Principles & Guidelines
1. **Verifiability at a Glance:** Color-coded verification badges (`[VERIFIED: Green]`, `[PARTIAL: Amber]`, `[REFUSED: Red]`) with clickable source chips.
2. **Adversarial Transparency:** Refused claims must be given dedicated visual space, highlighting the exact refusal code and missing evidence.
3. **One-Page Cognitive Discipline:** The final diagnostic must adhere strictly to a single-page density layout (no infinite-scroll fluff).

---

### 9. AI & System Principles
- **No Hallucination Tolerance:** The LLM is forbidden from stating any biographical claim not present in retrieved context.
- **Citation Anchoring:** Every claim output must be programmatically tied to an active URL with fetched snippet tokens.
- **Separation of Concerns:** Separate agent personas for Discovery, Extraction, Verification, and Gap Analysis to prevent bias contamination.
