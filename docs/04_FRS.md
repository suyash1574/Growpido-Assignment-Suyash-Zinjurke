# Functional Requirements Specification (FRS)
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Document Overview & Specification Depth
The Functional Requirements Specification (FRS) provides exact technical and algorithmic definitions for each module in the Growpido Prospect to Diagnostic Engine. It specifies input/output schemas, pseudo-code logic, validation constraints, error codes, and strict acceptance criteria.

---

### 2. Detailed Functional Specifications

#### FRS-ING-001: Public LinkedIn Target Ingestion
- **Module:** Ingestion Service (`IngestService`)
- **Functional Scope:** Accepts, cleans, and canonicalizes public LinkedIn profile targets.
- **Input Specification:**
  ```json
  {
    "input_url": "https://www.linkedin.com/in/ronaldo-mouchawar-souq"
  }
  ```
- **Validation Rules:**
  1. URL must match regex: `^https:\/\/(www\.)?linkedin\.com\/in\/[a-zA-Z0-9_-]+\/?$`
  2. Protocol must be HTTPS.
  3. No query parameters permitted (stripped automatically).
- **Processing Logic:**
  1. Extract slug token: `slug = url.strip("/").split("/")[-1]`.
  2. Normalize name tokens by replacing hyphens and underscores with spaces.
  3. Initialize seed `ProspectEntity` with `slug`, `normalized_name`, and `status = INITIALIZED`.
- **Output Specification:**
  ```json
  {
    "prospect_id": "8f3e2a10-c4b9-4d6b-9c88-12a3b4c5d6e7",
    "canonical_url": "https://www.linkedin.com/in/ronaldo-mouchawar-souq",
    "target_name_hint": "Ronaldo Mouchawar",
    "ingested_at": "2026-09-16T04:05:00Z"
  }
  ```

---

#### FRS-DIS-001: Multi-Tiered Public OSINT Discovery
- **Module:** Discovery Service (`DiscoveryService`)
- **Functional Scope:** Orchestrates multi-engine web queries across tiered domain sources.
- **Source Tier Definitions:**
  - **Tier 1 (Authoritative / Primary):**
    - Government & Corporate Registries: `*.gov.ae`, `*.adgm.com`, `*.difc.ae`, `*.sec.gov`, `*.dfsa.ae`.
    - Official Corporate Domains: Verified company domains (`amazon.ae`, `souq.com`, etc.).
    - Academic Registries: Accredited university portals (`*.edu`, official alumni registries).
  - **Tier 2 (Reputable Secondary):**
    - Established Business & Financial Press: Bloomberg, Reuters, Financial Times, Arabian Business, Gulf News, The National.
  - **Tier 3 (Aggregators / Unverified Secondary):**
    - Crunchbase, Wikipedia, PitchBook public summaries, automated bio scrapers. (Permitted for initial discovery query generation only, never for final verification).
  - **Tier 4 (Unverified / Social):**
    - Medium blogs, Reddit, Twitter/X posts, podcast transcripts.
- **Execution Flow:**
  1. Formulate 4 standardized query vectors:
     - Vector A: `"{Target Name}" "{Target Company}" executive biography`
     - Vector B: `"{Target Name}" site:adgm.com OR site:difc.ae OR site:dfsa.ae`
     - Vector C: `"{Target Name}" career education founder CEO interview`
     - Vector D: `"{Target Name}" news press release announcement`
  2. Fetch top 5 URLs per vector via Search API.
  3. Retrieve HTML payloads with 5-second timeout and 100KB truncation safety.
  4. Strip script/style tags, extract clean text, and compute content MD5 hash.

---

#### FRS-CLM-001: Atomic Claim Extraction & Materiality Scoring
- **Module:** Claim Auditor Service (`ClaimAuditor`)
- **Functional Scope:** Deconstructs unstructured discovery texts into discrete atomic factual statements.
- **Decomposition Schema:**
  ```json
  {
    "claim_id": "c1a2b3c4-0001-4000-8000-000000000001",
    "prospect_id": "8f3e2a10-c4b9-4d6b-9c88-12a3b4c5d6e7",
    "raw_claim_text": "Co-founded Souq.com in 2005 alongside Samih Toukan.",
    "category": "ROLE_TENURE",
    "materiality": "HIGH",
    "extracted_entities": {
      "role": "Co-founder",
      "organization": "Souq.com",
      "year_start": 2005,
      "co_founders": ["Samih Toukan"]
    }
  }
  ```
- **Materiality Classification Matrix:**
  - `HIGH`: Financial metrics (fund size, exit valuation, revenue), C-suite/Board appointments, accredited academic degrees, regulatory licenses.
  - `MEDIUM`: Keynote speaker appearances, industry committee memberships, published articles.
  - `LOW`: Personal hobbies, generic quotes, unquantified accolades ("visionary leader").

---

#### FRS-VER-001: Double-Check Primary Source Verification Engine
- **Module:** Verification Engine (`VerificationEngine`)
- **Functional Scope:** Executes the strict two-step verification protocol against primary evidence.
- **Algorithm Flowchart:**
  ```
  [Claim Input]
        │
        ▼
  [Step 1: Primary Evidence Search (Tier 1 Domain)]
        ├─► No Tier-1 Evidence Found ──► Status: UNVERIFIED ──► Route to Refusal Engine
        │
        ▼
  [Step 1 Evaluation: Semantic Entailment >= 0.85]
        ├─► Fails Semantic Entailment ──► Status: UNVERIFIED ──► Route to Refusal Engine
        │
        ▼
  [Step 2: Corroboration & Contradiction Cross-Examination]
        ├─► Conflicting Date/Number Found ──► Status: PARTIALLY_VERIFIED (Flag Contradiction)
        ├─► Corroborated by Independent Tier 1/2 Source ──► Status: VERIFIED
        └─► Single Tier 1 Source with Zero Disputes ──► Status: VERIFIED (Qualified)
  ```
- **Status Assignment Logic:**
  ```python
  if tier1_source_present and check1_passed and check2_passed and not contradiction_detected:
      status = "VERIFIED"
  elif (tier2_source_present or (tier1_source_present and contradiction_detected)) and check1_passed:
      status = "PARTIALLY_VERIFIED"
  else:
      status = "UNVERIFIED"
  ```
- **Output Record:**
  ```json
  {
    "claim_id": "c1a2b3c4-0001-4000-8000-000000000001",
    "status": "VERIFIED",
    "primary_source_url": "https://www.adgm.com/public-registers/...",
    "primary_source_tier": "Tier 1",
    "check_1_result": {
      "verified": true,
      "method": "REGEX_AND_EXACT_TOKEN_MATCH",
      "matched_snippet": "Ronaldo Mouchawar co-founded Souq.com in 2005..."
    },
    "check_2_result": {
      "verified": true,
      "method": "INDEPENDENT_DOMAIN_CORROBORATION",
      "corroborating_url": "https://press.aboutamazon.com/2017/3/...",
      "contradiction_detected": false
    },
    "verification_timestamp": "2026-09-16T04:06:12Z"
  }
  ```

---

#### FRS-REF-001: Adversarial Refusal & Reason Generation
- **Module:** Refusal Engine (`RefusalEngine`)
- **Functional Scope:** Intercepts any claim that does not meet the strict `VERIFIED` criteria and constructs an explicit, mathematically defensible refusal log.
- **Refusal Taxonomy:**
  - `REF-01 (NO_PRIMARY_EVIDENCE):` Claim only exists on blogs or aggregator profiles; no primary corporate or regulatory filing found.
  - `REF-02 (UNRESOLVED_CONTRADICTION):` Primary source A states Year X; primary source B states Year Y.
  - `REF-03 (PR_PUFFERY_UNQUANTIFIED):` Claim contains subjective hype ("Middle East's top innovator") with no certifying institutional metric.
  - `REF-04 (CORROBORATION_FAILURE):` Primary source inconclusive and second check failed to return supporting evidence.
- **Refusal Example Output (Track B Requirement):**
  ```json
  {
    "refused_claim": "Personal angel investment portfolio exceeds $50M across 40 startups.",
    "original_context": "Found in online bio aggregation profile.",
    "attempted_sources": [
      "https://crunchbase-mirror.com/person/...",
      "https://tech-blog-mena.com/..."
    ],
    "refusal_code": "REF-01",
    "refusal_reason": "Aggregator-only citation. No regulatory filing (ADGM/DIFC), verified fund disclosure, or audited portfolio statement exists to corroborate the $50M assertion. Refused from core diagnostic pursuant to Rule BR-R01 (Accuracy Dominance)."
  }
  ```

---

#### FRS-GAP-001: Three Strategic Presence Gaps
- **Module:** Diagnostic Synthesis Engine (`DiagnosticEngine`)
- **Functional Scope:** Maps verified accomplishments against the executive's digital footprint to extract exactly three actionable strategic positioning gaps.
- **Gap Dimensions:**
  1. **Dimensional Gap 1: Authority & Institutional Proof Under-Indexing**
     - Metric: Verified achievements (e.g., $580M exit or massive regional logistics network) exist in regulatory/financial news, but executive's own channels lack clear, authoritative documentation of these milestones.
  2. **Dimensional Gap 2: Channel Diversification & Search Real-Estate Deficiency**
     - Metric: Executive is heavily reliant on a single dormant LinkedIn profile with zero verified thought leadership on major industry platforms (Forbes Middle East, Bloomberg UAE, podcast appearances, whitepapers).
  3. **Dimensional Gap 3: Narrative Fragmentation & Role Ambiguity**
     - Metric: Lack of clear thematic positioning; bio attempts to claim multiple disparate areas (Angel, Advisor, Operator, Fund Manager) without a cohesive core narrative.
- **Ranking Criteria:**
  - Ranked by `Commercial Impact Score` (1–10) based on how directly the gap hinders Growpido's proposed advisory engagement. Top 3 highest scores are selected.

---

#### FRS-HGT-001: Human Gate & Editorial Sign-Off Interface
- **Module:** Human Review Dashboard (`HumanGateUI`)
- **Functional Scope:** Intercepts engine outputs in an intermediate state, requiring explicit human advisor approval.
- **State Machine:**
  - `PROSPECT_INGESTED` ➔ `DISCOVERY_COMPLETE` ➔ `CLAIMS_EXTRACTED` ➔ `VERIFICATION_COMPLETE` ➔ `AWAITING_HUMAN_GATE` ➔ `APPROVED` ➔ `DIAGNOSTIC_RENDERED`.
- **Allowed Human Actions:**
  - `APPROVE_AS_IS`: Accepts all machine classifications.
  - `OVERRIDE_STATUS`: Change status of specific claim (requires 20-character rationale string logged to audit ledger).
  - `EXCLUDE_CLAIM`: Manually send a verified claim to Refusal Log.
  - `COMMIT_AND_GENERATE`: Seals the audit trail and renders final One-Page Diagnostic.
