# High-Level Design (HLD)
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Executive Architecture Overview
The Growpido Prospect to Diagnostic Engine is designed around an **Adversarial Multi-Agent Verification Architecture**. Unlike naive retrieval-augmented generation (RAG) pipelines that trust whatever text is retrieved, our architecture bifurcates the discovery process from verification, enforcing an independent audit stage and a human sign-off gate before generating the final executive diagnostic.

---

### 2. High-Level Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             USER / ADVISOR                                  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Submits LinkedIn URL
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          STREAMLIT INTERACTION TIER                         │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌─────────────────┐  │
│  │ Target Ingest Form    │  │ Human Gate Review     │  │ Diagnostic View │  │
│  └───────────────────────┘  └───────────────────────┘  └─────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Session State
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     RESEARCH & AUDIT ORCHESTRATOR                           │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    PIPELINE STATE CONTROLLER                          │  │
│  └───────────────────┬───────────────────────────────┬───────────────────┘  │
│                      │                               │                      │
│                      ▼                               ▼                      │
│         ┌─────────────────────────┐     ┌─────────────────────────┐         │
│         │   DISCOVERY AGENT       │     │   REPUTATION AGENT      │         │
│         │ • Public Search         │     │ • Media Mentions        │         │
│         │ • Registry Lookup       │     │ • Sentiment Analysis    │         │
│         │ • Content Sanitizer     │     │ • Social Resonance      │         │
│         └────────────┬────────────┘     └────────────┬────────────┘         │
│                      │                               │                      │
│                      └───────────────┬───────────────┘                      │
│                                      ▼                                      │
│                         ┌─────────────────────────┐                         │
│                         │   CLAIM AUDITOR AGENT   │                         │
│                         │ • Atomic Claim Extractor│                         │
│                         │ • Materiality Scorer    │                         │
│                         └────────────┬────────────┘                         │
│                                      ▼                                      │
│                         ┌─────────────────────────┐                         │
│                         │   DOUBLE-CHECK ENGINE   │                         │
│                         │ • Check 1: Primary Auth │                         │
│                         │ • Check 2: Corroboration│                         │
│                         │ • Contradiction Detector│                         │
│                         └────────────┬────────────┘                         │
│                                      ▼                                      │
│                         ┌─────────────────────────┐                         │
│                         │     CLASSIFIER HUB      │                         │
│                         │   Verified / Partial    │                         │
│                         └──────┬───────────┬──────┘                         │
│                                │           │                                │
│                   Passed Checks│           │Failed / Refused                │
│                                ▼           ▼                                │
│               ┌──────────────────┐       ┌──────────────────┐               │
│               │ 3-GAP SYNTHESIZER│       │  REFUSAL ENGINE  │               │
│               │ • Authority Gap  │       │ • Code Assignment│               │
│               │ • Channel Gap    │       │ • Missing Proof  │               │
│               │ • Narrative Gap  │       │ • Audit Reason   │               │
│               └────────┬─────────┘       └────────┬─────────┘               │
│                        │                          │                         │
│                        └─────────────┬────────────┘                         │
│                                      ▼                                      │
│                         ┌─────────────────────────┐                         │
│                         │    HUMAN GATE STAGE     │                         │
│                         │ • Reviewer Confirmation │                         │
│                         │ • Manual Override Logic │                         │
│                         └────────────┬────────────┘                         │
│                                      ▼                                      │
│                         ┌─────────────────────────┐                         │
│                         │ ONE-PAGE DIAGNOSTIC GEN │                         │
│                         │ • Clean Executive Layout│                         │
│                         │ • Audit Trail Export    │                         │
│                         └─────────────────────────┘                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3. Subsystem Breakdown

#### 3.1 Ingestion & Target Resolution Subsystem
- **Function:** Accepts public LinkedIn profile URL (e.g., `linkedin.com/in/ronaldo-mouchawar-souq`), validates syntax, canonicalizes identity tokens, and prevents automated credential abuse.
- **Components:** `URLValidator`, `SlugParser`, `TargetEntityResolver`.

#### 3.2 Discovery & OSINT Ingestion Subsystem
- **Function:** Executes broad, multi-vector public search queries across web indices, official free-zone registries (ADGM, DIFC), and corporate portals. Sanitizes HTML and stores text snapshots.
- **Components:** `SearchProviderRouter` (Tavily/DuckDuckGo), `WebFetcher`, `HTMLSanitizer`, `SourceTierClassifier`.

#### 3.3 Claim Auditor Subsystem
- **Function:** Ingests raw unstructured text and extracts clean, isolated atomic claims. Assigns category tags (`Role`, `Education`, `Funding`, `Accolade`) and materiality ratings (`High`, `Medium`, `Low`).
- **Components:** `ClaimExtractor`, `EntityResolver`, `MaterialityRanker`.

#### 3.4 Double-Check Verification & Contradiction Subsystem
- **Function:** Executes the core fact-integrity algorithm:
  - **Check 1 (Primary Source Grounding):** Maps claim against official regulatory registry or company primary URL.
  - **Check 2 (Independent Corroboration):** Performs secondary search to corroborate details and actively tests for contradictory dates or claims.
- **Components:** `PrimarySourceMatcher`, `SemanticEntailmentEvaluator`, `ContradictionDetector`.

#### 3.5 Refusal & Exclusion Subsystem
- **Function:** Isolates claims that fail primary verification or contain conflicting records. Generates an explicit, transparent refusal log with standard error codes (`REF-01` to `REF-04`).
- **Components:** `RefusalFilter`, `ReasonCodeGenerator`, `AuditSerializer`.

#### 3.6 Diagnostic & Strategic Gap Subsystem
- **Function:** Analyzes the delta between the prospect's verified achievements and their public presence footprint, synthesizing exactly three commercial presence gaps.
- **Components:** `BenchmarkComparator`, `GapRanker`, `ExecutiveNarrativeFormatter`.

#### 3.7 Human Gate & Editorial Subsystem
- **Function:** Provides an interactive approval screen where human advisors review, edit, or override machine findings before diagnostic compilation.
- **Components:** `HumanGateDashboard`, `OverrideAuditor`, `DiagnosticRenderer`.

---

### 4. Data Flow Matrix
| Step | Sender | Receiver | Payload Description |
| :--- | :--- | :--- | :--- |
| **01** | User / Web UI | Ingestion Service | Raw LinkedIn URL string. |
| **02** | Ingestion Service | Discovery Agent | Canonical Target Entity (Name, Slug). |
| **03** | Discovery Agent | Raw Storage | Raw HTML and sanitized text snapshots with content hashes. |
| **04** | Discovery Agent | Claim Auditor | List of sanitized document chunks with source tier metadata. |
| **05** | Claim Auditor | Verification Engine | Atomic claims with entity tags and materiality ratings. |
| **06** | Verification Engine | Classifier Hub | Claim verification records (Check 1 & Check 2 results, contradiction flags). |
| **07** | Classifier Hub | Refusal Engine | Claims categorized as `UNVERIFIED` or contradictory. |
| **08** | Classifier Hub | Gap Synthesizer | Verified and partially verified factual profile dataset. |
| **09** | Gap Synthesizer | Human Gate UI | Draft diagnostic containing verified claims, 3 gaps, and refused claims. |
| **10** | Human Gate UI | Diagnostic Generator | Approved diagnostic payload with human auditor sign-off signature. |

---

### 5. Architectural Quality Attributes
- **Adversarial by Default:** Verification components operate independently of discovery agents to eliminate confirmation bias.
- **Deterministic Guardrails:** LLMs are used for semantic classification and formatting, while source tiering, URL validation, and contradiction filtering rely on deterministic code.
- **Fault-Tolerant Execution:** Any failure in third-party search APIs triggers automatic failovers without crashing active sessions.
