# Business Requirements Document (BRD)
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Document Control
- **Project Name:** Growpido Prospect Intelligence Engine (Track B)
- **Document Version:** 1.0.0
- **Status:** Approved / Baseline
- **Document Owner:** Lead Systems Architect & Requirements Engineering Team
- **Target Audience:** Growpido Leadership, Product Engineers, AI Architects, Evaluation Committee

---

### 2. Executive Summary
Growpido helps high-profile executives, founders, CEOs, and fund managers establish authority, presence, and personal brand impact. To deliver hyper-targeted strategic advisory, Growpido must evaluate how a prospect appears across public domains, identify visibility and narrative gaps, and generate actionable executive diagnostics.

However, generating prospect intelligence using generic Large Language Models (LLMs) poses existential brand and advisory risks: **AI hallucinations, ungrounded factual assertions, and fabricated citations**. 

The **Growpido Prospect to Diagnostic Engine** is an enterprise-grade, agentic intelligence system designed to ingest a public LinkedIn profile URL of a UAE-based executive, orchestrate multi-tiered public source discovery, subject every extracted factual claim to double-checked primary source verification, detect contradictions, enforce strict refusal logic, pinpoint the top three strategic public presence gaps, and render a verified, executive-ready One-Page Diagnostic alongside an immutable audit trail.

**Core Business Principle:**
> **Accuracy takes absolute precedence over completeness.** If a claim cannot be verified against authoritative primary evidence through two independent checks, it must be flagged, qualified, or systematically refused.

---

### 3. Business Context & Strategic Alignment
Growpido engages with Tier-1 decision makers (Founders, C-suite leaders, and Fund Managers in high-growth hubs such as the UAE/MENA region). Presenting an executive with inaccurate biographical data, false corporate milestones, or fictitious accolades instantly destroys credibility and sales conversion. 

The Growpido platform must automate initial discovery while acting as an adversarial fact-checker that guarantees zero-hallucination outputs before any human advisor or prospect reviews the intelligence briefing.

---

### 4. Problem Statement
1. **Unreliable Automated OSINT:** Standard scraping tools and LLM wrappers fabricate executive roles, fund sizes, educational credentials, and awards due to hallucination loops and stale training data.
2. **Citation Laundering:** Aggregator websites (e.g., automated bios, content scrapers, unverified press releases) frequently echo unverified PR claims, giving the illusion of corroboration without primary authority.
3. **Lack of Refusal Mechanics:** Typical AI engines strive to answer every prompt at all costs, guessing missing metrics or synthesizing speculative narratives rather than refusing unsupported claims.
4. **Vague, Unactionable Feedback:** Existing lead-enrichment tools deliver disconnected raw data points rather than structured strategic gaps explaining *how* the executive underrepresents their market authority.

---

### 5. Business Objectives
- **BO-01: Zero Hallucination Rate in Final Diagnostics:** 100% of factual assertions in the final executive diagnostic must be grounded in verified or explicitly qualified primary evidence.
- **BO-02: Double-Check Verification Standard:** Mandate a two-stage independent verification protocol (primary authority validation + secondary cross-examination) before granting "Verified" status.
- **BO-03: Deterministic Claim Refusal:** Explicitly refuse and isolate any material claim that fails primary verification, logging the exact rationale in an audit trail.
- **BO-04: High-Value Strategic Gap Identification:** Systematically identify exactly three prioritized, defensible narrative/presence gaps based strictly on verified reality vs. public footprint.
- **BO-05: Executive-Ready One-Page Asset:** Deliver a cohesive, scannable one-page diagnostic format suited for C-level presentation.
- **BO-06: 100% Auditability:** Maintain an immutable event-log from raw public URLs down to claim status, source tier, verification timestamps, and refusal reasons.

---

### 6. Current Pain Points
| ID | Current Pain Point | Business Impact | Desired Engine State |
| :--- | :--- | :--- | :--- |
| **PP-01** | Manual prospect fact-checking takes 2–3 hours per executive. | Bottleneck in onboarding and sales pipeline velocity. | Automated OSINT & verification executed in < 120 seconds. |
| **PP-02** | Scraping secondary bio aggregators yields outdated/false titles. | High risk of embarrassing errors in front of clients. | Multi-tier source hierarchy prioritizing Tier-1 primary records. |
| **PP-03** | Black-box AI generation without traceable citations. | Inability to defend findings during client pitch calls. | Granular claim-level citations with cryptographic/URL auditability. |
| **PP-04** | Ambiguous unverified gossip treated as factual truth. | Reputational and legal exposure for Growpido. | Strict refusal mechanism segregates unverified material. |

---

### 7. Target Users & Personas
1. **Growpido Strategy Advisors & Account Executives:** Need authoritative, bulletproof diagnostics before entering discovery and advisory meetings.
2. **Research Analysts & Fact Auditors:** Review automated claims, inspect contradiction alerts, and grant human-in-the-loop sign-off.
3. **Prospect Executives (CEOs, Founders, Fund Managers):** End recipients of the One-Page Diagnostic who demand razor-sharp strategic insights without factual errors.

---

### 8. Stakeholders
- **Growpido Executive Leadership:** Demands brand protection, high advisory conversion, and algorithmic excellence.
- **Growpido Engineering & AI Team:** Responsible for system uptime, deterministic verification, and LLM orchestration.
- **Evaluation & Hackathon Rubric Assessors:** Require proof of adherence to Track B criteria (verification rigor, refusal example, runnable architecture).

---

### 9. Business Requirements (High-Level)
- **BR-FACT-001 (Primary Source Verification):** The engine shall require all material factual claims to be validated against an authoritative primary source (e.g., government registries, official regulatory filings, verified company websites, primary publications).
- **BR-FACT-002 (Double-Check Protocol):** Every factual claim must undergo two distinct verification steps (authority check + corroboration/consistency check) before obtaining "Verified" status.
- **BR-FACT-003 (Three-State Classification):** The system shall classify all findings into three mutually exclusive categories: `VERIFIED`, `PARTIALLY_VERIFIED`, or `UNVERIFIED`.
- **BR-FACT-004 (Explicit Refusal & Justification):** The system shall refuse to include unverified or contradictory material claims in the core diagnostic and shall output an explicit refusal justification explaining why the claim was withheld.
- **BR-GAP-001 (Three Presence Gaps):** The system shall analyze the verified footprint against industry benchmarks to identify the three largest strategic gaps in the executive’s public presence.
- **BR-OUT-001 (One-Page Diagnostic Delivery):** The system shall produce a structured, clean one-page diagnostic consumable by both human advisors and prospect executives.
- **BR-GOV-001 (Human Gate):** Provide a human review stage prior to final diagnostic commitment, ensuring an advisor can override or confirm machine classifications.
- **BR-AUD-001 (Audit Trail & Provenance):** Every claim, classification, source tier, and refusal event must be recorded in an immutable ledger.

---

### 10. Business Rules
- **Rule BR-R01 (Accuracy Dominance):** Under no circumstance shall the system sacrifice verification accuracy to produce a longer or more comprehensive report.
- **Rule BR-R02 (Source Hierarchy Adherence):** Aggregator databases, social forums, and unverified blogs shall never be accepted as primary verification sources (Discovery only).
- **Rule BR-R03 (Contradiction Lockout):** If two authoritative sources present conflicting material facts (e.g., differing tenure dates or fund sizes), the claim must be locked as `PARTIALLY_VERIFIED` or `UNVERIFIED` and routed to the Human Gate.
- **Rule BR-R04 (Refusal Retention):** Refused claims are not silently deleted; they must be displayed in the Audit and Refusal breakdown with clear causal rationale.

---

### 11. Success Metrics & Key Performance Indicators (KPIs)
| Metric ID | KPI Description | Target Benchmark |
| :--- | :--- | :--- |
| **KPI-01** | Factual Hallucination Rate | 0.0% (Zero hallucinated claims in final diagnostic) |
| **KPI-02** | Primary Source Grounding Ratio | 100% of `VERIFIED` claims backed by Tier-1 primary URLs |
| **KPI-03** | Refusal Transparency Index | 100% of rejected claims accompanied by standardized refusal reason codes |
| **KPI-04** | Processing Latency | < 120 seconds end-to-end per prospect execution |
| **KPI-05** | Human Gate Review Efficiency | Advisor review completed in < 60 seconds with pre-ranked claims |

---

### 12. Scope
#### In-Scope:
- Ingestion of public LinkedIn profile URLs of UAE-based founders, CEOs, and fund managers.
- Public web discovery across search engines, corporate registries, official press releases, news archives, and regulatory portals.
- Claim extraction, categorization (biographical, operational, financial, reputational), and materiality ranking.
- Two-step verification engine evaluating authority, semantic alignment, and contradiction detection.
- Three-gap presence diagnostic synthesis.
- Production of a printable/viewable One-Page Diagnostic and explicit Refusal Log.
- Complete audit logging and human review workflow.

#### Out-of-Scope:
- Scraping private, authenticated, or gated LinkedIn networks behind login credentials.
- Contacting prospects via automated messaging, InMail, email, or cold outreach.
- Multi-tenant enterprise role-based billing and CRM integration.
- Speculative financial profiling or sensitive personal attribute inference.

---

### 13. Assumptions & Constraints
- **Assumptions:** The prospect has an existing, publicly crawlable LinkedIn presence and their business footprint exists in public web indices.
- **Constraints:** Must operate entirely within public OSINT boundaries; must comply with UAE data privacy laws and ethical web indexing standards.

---

### 14. Risks & Mitigations
| Risk ID | Risk Description | Severity | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **RSK-01** | Anti-scraping rate limits on public engines. | High | Multi-provider search fallback (Tavily, SerpAPI, DuckDuckGo) with exponential backoff. |
| **RSK-02** | LLM hallucination of citations. | Critical | Strict deterministic verification layer: URLs must be scraped and regex-matched before LLM citation is accepted. |
| **RSK-03** | Low public digital footprint for niche fund managers. | Medium | Graceful degradation: output diagnostic highlighting severe under-indexing as Gap #1, without inventing claims. |

---

### 15. Growpido Hackathon Track B Rubric Mapping
| Rubric Category | Weight | How Our System Satisfies This Requirement |
| :--- | :--- | :--- |
| **Fact Integrity** | 25 pts | Double-check verification pipeline, primary source hierarchy, refusal mechanism for unverified claims. |
| **Does It Run** | 20 pts | Fully functional Python/Streamlit architecture, deterministic execution, dockerized deployment. |
| **Judgement** | 20 pts | Source authority tiers, materiality classification, and gap weighting based on executive reality. |
| **Human Gate** | 15 pts | Dedicated human review interface enabling manual override of flagged/partial claims before diagnostic output. |
| **Output Quality** | 10 pts | High-impact, professional One-Page Executive Diagnostic with clean visual hierarchy. |
| **Honest Paragraph** | 10 pts | Explicit disclosure of edge cases, failed lookups, limitations, and future enhancements. |

---

### 16. Glossary
- **Primary Source (Tier 1):** The direct, original publisher of record (e.g., regulatory disclosures, court filings, official university registries, official corporate domain).
- **Secondary Source (Tier 2):** Established journalistic outlets and major media reporting on an event.
- **Aggregator Source (Tier 3):** Automated databases, Wikipedia, crunchbase mirrors, bio directories (permitted for discovery, prohibited for verification).
- **Double-Check Verification:** Two independent checks: Check 1 confirms primary source existence and semantic support; Check 2 checks against negative/conflicting assertions.
- **Strategic Presence Gap:** A discrepancy between an executive’s actual business achievements and their public narrative visibility.
