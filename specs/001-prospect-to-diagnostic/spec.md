# Feature Specification: Prospect to Diagnostic Intelligence Engine

**Feature Branch**: `001-prospect-to-diagnostic`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "Track B - Prospect to Diagnostic: Build something that, starting from a LinkedIn URL: researches the person from public sources, verifies every factual claim against a primary source and checks it twice, labels each finding (verified, partially verified, or unverified), identifies the three biggest gaps in how they currently show up publicly, outputs a one-page diagnostic, and demonstrates one claim refused and why."

## Clarifications

### Session 2026-09-16
- Q: How should the system handle search provider failures or missing external API keys during automated execution? → A: Live public internet discovery only; do not add offline mock failovers. The system must fetch real-time public web intelligence directly from live search engines/registries. If live search APIs fail or credentials are missing, fail transparently with an explicit error rather than substituting cached or synthetic data.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Public Target Ingestion & Primary Source Double-Check Verification (Priority: P1)

An executive intelligence advisor inputs a public LinkedIn URL for a UAE-based founder, CEO, or fund manager into the system. The system automatically extracts discrete factual assertions from publicly available web records, subjects each claim to an adversarial two-stage verification against authoritative primary evidence (official registries or direct corporate records), detects any contradictions, and tags every claim with a transparent verification badge (`VERIFIED`, `PARTIALLY_VERIFIED`, or `UNVERIFIED`).

**Why this priority**: Core fact integrity is the non-negotiable bedrock of Growpido Track B (worth 25 points on the rubric). If the system hallucinates, cites unverified aggregator blogs, or fails to double-check assertions, all downstream advisory credibility is lost.

**Independent Test**: Can be fully tested by submitting a known UAE executive profile URL (e.g., `https://www.linkedin.com/in/ronaldo-mouchawar-souq`), asserting that all extracted biographical and career claims are verified against primary records (such as corporate filings and government registries), and confirming that every finding carries one of the three required verification labels with citation links.

**Acceptance Scenarios**:

1. **Given** a valid public LinkedIn profile URL of a UAE executive, **When** the advisor initiates discovery and verification, **Then** the system extracts atomic claims and validates them against primary Tier-1 sources through two distinct check stages.
2. **Given** a factual claim supported by both an official registry and corroborating corporate record, **When** both verification checks pass with no contradictions, **Then** the claim is labeled `VERIFIED`.
3. **Given** a factual claim supported only by secondary press or displaying minor temporal ambiguity across sources, **When** evaluated by the verification engine, **Then** the claim is labeled `PARTIALLY_VERIFIED` and flagged for review.
4. **Given** a claim appearing solely on bio scrapers or blog directories without primary evidence, **When** evaluated, **Then** the claim is labeled `UNVERIFIED` and sent to the refusal quarantine.

---

### User Story 2 - Adversarial Claim Refusal with Causal Justification (Priority: P2)

An executive intelligence advisor reviews the findings and inspects the dedicated Refusal Log. The system demonstrates at least one extracted public claim that it actively refused to incorporate into the final executive profile because it failed primary source verification, explaining precisely which evidence was missing and why the claim was rejected.

**Why this priority**: Directly required by the Track B brief ("plus one claim your system refused to include and why it refused") and demonstrates adherence to Constitution Principle I (Accuracy over Completeness) and Principle III (Mandatory Adversarial Refusal).

**Independent Test**: Can be independently tested by providing an input profile containing secondary PR puffery or uncorroborated financial metrics (e.g., a rumored "$50M personal angel portfolio" from speaker bios); the system must exclude the assertion from the main profile and output a refusal record with code `REF-01` and an explicit explanatory rationale.

**Acceptance Scenarios**:

1. **Given** an extracted assertion lacking primary regulatory or audited corporate filing, **When** the verification engine completes its checks, **Then** the claim is refused and excluded from the core profile.
2. **Given** a refused claim, **When** an advisor views the refusal summary, **Then** the system presents the original text, attempted search sources, refusal code, and a clear causal explanation.

---

### User Story 3 - Three Strategic Public Presence Gaps Identification (Priority: P3)

An executive advisor analyzes the prospect's verified achievements against their public digital footprint. The system synthesizes and ranks exactly three high-leverage presence gaps explaining how the executive underrepresents their institutional authority, suffers from channel concentration, or displays narrative fragmentation.

**Why this priority**: Required by the Track B brief ("identifies the three biggest gaps in how they currently show up publicly") and equips Growpido advisors with immediate, high-value commercial pitch angles.

**Independent Test**: Can be independently tested by verifying that exactly three distinct gaps are returned, each corresponding to Authority Under-Indexing, Channel Diversity Deficit, and Narrative Fragmentation, complete with evidence rationale and advisory recommendations.

**Acceptance Scenarios**:

1. **Given** a completed set of verified executive facts, **When** the gap engine assesses the public footprint, **Then** it produces exactly three prioritized gaps ranked by commercial impact.
2. **Given** an executive with massive commercial milestones but absent personal web channels, **When** evaluated, **Then** the system highlights Authority Under-Indexing as a primary strategic gap with concrete recommendations.

---

### User Story 4 - Sovereign Human-in-the-Loop Review Gate (Priority: P4)

Before any diagnostic is finalized, an advisor inspects an interactive review dashboard where all claims, evidence snippets, contradiction flags, and refusal reasons are displayed. The advisor can accept machine classifications or manually override statuses with an audit comment before authorizing report compilation.

**Why this priority**: Satisfies the 15-point Human Gate rubric requirement and ensures human accountability over algorithmic decisions.

**Independent Test**: Can be independently tested by toggling a claim status from `PARTIALLY_VERIFIED` to `VERIFIED` in the interface with a comment; the system must log the override in the audit trail and update the diagnostic.

**Acceptance Scenarios**:

1. **Given** unapproved pipeline findings, **When** presented at the review stage, **Then** the system blocks final diagnostic compilation until an advisor explicitly signs off.
2. **Given** an advisor overriding a claim status, **When** submitted with a rationale, **Then** the override event is recorded in the permanent audit ledger.

---

### User Story 5 - One-Page Executive Diagnostic Delivery & Audit Export (Priority: P5)

The advisor clicks compile, and the system renders a clean, scannable One-Page Diagnostic containing verified executive facts, the 3 strategic presence gaps, the demonstrated refused claim, and a downloadable cryptographic audit trail.

**Why this priority**: Satisfies the brief requirement ("outputs a one-page diagnostic") and delivers the final commercial asset.

**Independent Test**: Can be tested by verifying that the output adheres to a single-page density format, includes direct source citations, and provides complete JSON audit export.

**Acceptance Scenarios**:

1. **Given** an approved review state, **When** compiled, **Then** the system renders a formatted One-Page Diagnostic.
2. **Given** a generated diagnostic, **When** exported, **Then** the complete audit trail linking every claim to its source hash and verification check is downloadable.

---

### Edge Cases

- **What happens when the prospect's public web footprint is virtually non-existent?**
  The system gracefully degrades, halts verification of phantom claims, and identifies severe digital invisibility as Strategic Gap #1 without hallucinating facts.
- **What happens when two authoritative primary sources directly contradict each other (e.g., conflicting founding dates)?**
  The claim is immediately flagged as `PARTIALLY_VERIFIED` with a `CONTRADICTION_DETECTED` warning, locked out of automatic `VERIFIED` status, and routed to the Human Gate.
- **What happens when a search provider experiences rate limits or timeouts?**
  The system triggers exponential backoff with jitter across live search providers; if live search fails entirely, it raises an explicit `ERR_LIVE_SEARCH_FAILED` without falling back to pre-recorded or synthetic offline mock datasets.
- **What happens if a user submits a private or invalid LinkedIn URL?**
  The system rejects the input at the ingestion gate with a user-friendly error message without attempting credential bypass.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a public LinkedIn profile URL and validate its structure without requiring user login credentials or session cookies.
- **FR-002**: System MUST search public web indices, corporate disclosures, and regulatory registries in real time to discover live public footprint records, strictly rejecting offline mock data substitution.
- **FR-003**: System MUST classify discovered sources into a 4-tier hierarchy: Tier 1 (Official registries / Corporate primary), Tier 2 (Reputable financial press), Tier 3 (Aggregators / Directories), and Tier 4 (Unverified social).
- **FR-004**: System MUST decompose discovered texts into discrete atomic factual claims with category and materiality ratings.
- **FR-005**: System MUST execute a two-stage verification protocol for every material claim: Check 1 (Primary source authority and semantic entailment) and Check 2 (Independent corroboration and contradiction check).
- **FR-006**: System MUST label every claim as `VERIFIED`, `PARTIALLY_VERIFIED`, or `UNVERIFIED`.
- **FR-007**: System MUST refuse to include unverified or contradictory material claims in the core executive profile.
- **FR-008**: System MUST display at least one refused claim with an assigned refusal code (`REF-01` to `REF-05`) and a detailed causal explanation of why it was excluded.
- **FR-009**: System MUST evaluate verified achievements against public presence to identify and rank exactly three strategic presence gaps.
- **FR-010**: System MUST provide an interactive Human Gate requiring advisor review, status override capability, and explicit sign-off before report generation.
- **FR-011**: System MUST output a scannable, executive-ready One-Page Diagnostic view with color-coded verification badges and citation links.
- **FR-012**: System MUST record every query, URL snapshot, verification check, refusal reason, and human override in an immutable audit ledger.

---

### Key Entities

- **Prospect**: Represents the target executive; contains public profile URL, canonical name, current title, and corporate organization.
- **EvidenceSource**: Represents a retrieved public document; contains source URL, domain, assigned source tier, snapshot content hash, and retrieval timestamp.
- **Claim**: Represents an isolated atomic factual assertion; contains statement text, category, materiality rating, verification status, primary source anchor, and refusal reason if rejected.
- **StrategicGap**: Represents one of three prioritized presence deficiencies; contains priority rank (1–3), gap dimension, observation, commercial impact, and recommendation.
- **AuditEvent**: Represents an immutable ledger entry recording system actions, verification decisions, and human overrides with timestamps.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of claims classified as `VERIFIED` in the final diagnostic must be grounded in an authoritative primary source with two completed verification checks.
- **SC-002**: Zero factual hallucinations or ungrounded speculative metrics in the final executive diagnostic.
- **SC-003**: 100% of refused claims are accompanied by a valid refusal code and specific causal explanation.
- **SC-004**: The system generates exactly three prioritized presence gaps for any analyzed executive footprint.
- **SC-005**: End-to-end execution from LinkedIn URL entry to staged Human Gate completes in under 120 seconds.
- **SC-006**: 100% of execution sessions maintain an immutable audit trail linking claims to source URLs and check outcomes.
- **SC-007**: The final executive diagnostic fits entirely within a single standard presentation page view.

---

## Assumptions

- Target executives are founders, CEOs, or fund managers operating in the UAE with an active, publicly crawlable LinkedIn presence.
- Public search engines and regulatory web indices contain sufficient public domain data to establish baseline corporate and career facts.
- Advisor users have basic domain knowledge to review evidence snippets and adjudicate flagged contradictions at the Human Gate.
- The system operates purely in passive OSINT mode; no credentialed scraping, private network infiltration, or automated prospect outreach is conducted.
