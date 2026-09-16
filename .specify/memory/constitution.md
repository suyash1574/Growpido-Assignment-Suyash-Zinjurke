<!--
Sync Impact Report:
- Version change: none (uninitialized template) → v1.0.0
- List of modified principles:
  * [PRINCIPLE_1_NAME] → I. Accuracy Takes Precedence Over Completeness (NON-NEGOTIABLE)
  * [PRINCIPLE_2_NAME] → II. Two-Stage Double-Check Primary Verification
  * [PRINCIPLE_3_NAME] → III. Mandatory Adversarial Refusal & Causal Justification
  * [PRINCIPLE_4_NAME] → IV. Sovereign Human-in-the-Loop Gate
  * [PRINCIPLE_5_NAME] → V. Strict Public OSINT Boundaries & Zero-Credential Policy
- Added sections:
  * Additional Constraints & Engineering Standards
  * Development Workflow & Verification Gates
  * Governance
- Removed sections: None
- Follow-up TODOs: None (all template placeholders fully defined).
-->

# Growpido Track B Intelligence Engine Constitution

## Core Principles

### I. Accuracy Takes Precedence Over Completeness (NON-NEGOTIABLE)
Under no circumstance shall the system sacrifice factual accuracy or verification rigor to generate a longer, more complete, or seemingly authoritative profile. If a material factual claim cannot be verified against authoritative primary evidence through two independent checks, it MUST be quarantined, qualified, or systematically refused. Hallucinated citations, speculative metrics, and ungrounded PR puffery are strictly forbidden from entering any executive diagnostic.

### II. Two-Stage Double-Check Primary Verification
Every extracted material claim MUST undergo two distinct verification gates before achieving `VERIFIED` status:
1. **Primary Authority Gate (Check 1):** The claim must be anchored to a Tier-1 primary source (official government/free-zone registry, regulatory filing, accredited university record, or official corporate domain) with direct semantic entailment ($\ge 0.85$). Secondary aggregators (Tier 3/4) are permitted solely for query discovery, never for verification.
2. **Corroboration & Consistency Gate (Check 2):** An independent source must confirm the assertion, and the claim must be actively tested against counter-evidence. Any temporal, role, or numerical contradiction locks the claim out of `VERIFIED` status and automatically routes it to `PARTIALLY_VERIFIED` with a contradiction warning.

### III. Mandatory Adversarial Refusal & Causal Justification
The engine MUST operate adversarially against its own extracted findings. Any material claim that fails primary source grounding or contains unresolved contradictions MUST be excluded from the core diagnostic and written to an explicit, transparent Refusal Log. Every refused claim MUST carry a standardized refusal reason code (`REF-01` through `REF-05`) alongside a human-readable causal explanation detailing the missing primary evidence.

### IV. Sovereign Human-in-the-Loop Gate
The system MUST NEVER compile or deliver a final One-Page Executive Diagnostic autonomously. An interactive Human Gate interface MUST intercept findings after verification, presenting advisors with full citation provenance, raw snippet quotes, and contradiction badges. Human advisors retain absolute authority to override, reclassify, or exclude claims, provided every manual override is committed with a mandatory audit rationale string.

### V. Strict Public OSINT Boundaries & Zero-Credential Policy
The engine MUST operate exclusively within publicly indexed web data. It MUST NEVER require, store, or inject LinkedIn user login credentials, session cookies (`li_at`), or OAuth tokens. The system MUST NOT bypass CAPTCHAs, access gated private networks, infer non-commercial PII or sensitive personal attributes, or trigger automated prospect outreach (no emails, connection requests, or InMails). Public source availability does not confer implicit trustworthiness.

## Additional Constraints & Engineering Standards

- **Deterministic Verification Rules:** Source tier classification, domain whitelisting, URL normalization, and contradiction checks MUST rely on deterministic code and regex anchors, using LLMs only for semantic entailment and executive text synthesis.
- **Three Strategic Presence Gaps:** The engine MUST evaluate the verified executive footprint against industry benchmarks to synthesize exactly three prioritized, defensible commercial gaps (Authority Under-Indexing, Channel Diversity Deficit, Narrative Fragmentation).
- **Executive One-Page Layout:** The final diagnostic MUST adhere strictly to a dense, scannable, single-page layout consumable by C-suite executives in under 90 seconds.
- **Immutable Cryptographic Auditability:** Every execution session, source URL, content hash (SHA-256), verification decision, refusal code, and human override MUST be permanently logged into an ACID-compliant local SQLite ledger.

## Development Workflow & Verification Gates

- **Specification Traceability:** Every software component, service interface, and automated test MUST trace directly to a permanent requirement identifier (`BR-XXX`, `PRD-FEAT-XXX`, `FR-XXX`, `FRS-XXX`, `SR-XXX`).
- **Test-First Verification:** Any changes or additions to verification logic, refusal reason assignment, or source tiering MUST be validated against automated test suites (`TS-01` through `TS-08`) before deployment.
- **Graceful Failure & Resilience:** Network timeouts, search provider throttling (HTTP 429), or target site bot-blocks MUST trigger automated failovers and exponential backoff routines without crashing pipeline execution or leaving orphaned states.

## Governance

This Constitution represents the supreme architectural and ethical law of the Growpido Prospect Intelligence Engine. It supersedes any temporary implementation convenience, model prompt shortcuts, or speculative feature requests.

- **Amendment Procedure:** Amendments require explicit documentation of rationale, a formal version increment, and a comprehensive Sync Impact Report.
- **Versioning Policy:** 
  - **MAJOR (x.0.0):** Incompatible governance shifts, removal of core principles, or alterations to fundamental fact-integrity rules.
  - **MINOR (1.x.0):** Addition of new architectural principles, expanded source tiers, or regulatory compliance standards.
  - **PATCH (1.0.x):** Non-semantic refinements, wording clarifications, and structural formatting adjustments.
- **Compliance Auditing:** Every pull request and architecture review must verify complete adherence to Principles I through V prior to merge.

**Version**: 1.0.0 | **Ratified**: 2026-09-16 | **Last Amended**: 2026-09-16
