# AI & Agent Specification
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Architectural Philosophy: The Adversarial Auditor Model
In standard agentic systems, agents are cooperative and often suffer from "confirmation bias" — an agent that extracts a claim tends to bias its own verification search to prove the claim true. 

The Growpido Engine strictly decouples agents into an **Adversarial Triad**:
1. **The Discovery Agent:** Maximizes recall across public web indices.
2. **The Claim Auditor Agent:** Decomposes findings into discrete, falsifiable atomic claims.
3. **The Verification Agent:** Acts as an adversarial prosecutor attempting to invalidate, contradict, or refuse claims unless authoritative primary proof is produced.
4. **The Diagnostic Agent:** Strictly isolated from unverified data; consumes *only* verified facts to produce the final diagnostic.

---

### 2. Detailed Agent Specifications

```
┌──────────────────┐
│  Discovery Agent │
└────────┬─────────┘
         │ Raw public texts
         ▼
┌──────────────────┐
│  Claim Auditor   │
└────────┬─────────┘
         │ Atomic claims
         ▼
┌──────────────────┐  Adversarial Check   ┌──────────────────┐
│Verification Agent├─────────────────────►│  Refusal Engine  │
└────────┬─────────┘                      └──────────────────┘
         │ Verified claims ONLY
         ▼
┌──────────────────┐
│ Diagnostic Agent │
└──────────────────┘
```

---

#### 2.1 Agent: Discovery Agent (`DiscoveryAgent`)
- **Primary Mission:** Discover and retrieve all publicly accessible footprint documents for the target executive without breaching authenticated networks.
- **Allowed Tools:**
  - `web_search(query: str, site_filter: Optional[str])`
  - `fetch_page_content(url: str)`
  - `parse_domain_tier(domain: str)`
- **Disallowed Tools / Actions:**
  - Authenticated scraping, bypassing CAPTCHAs, accessing private APIs, emailing or pinging prospects.
- **System Prompt:**
  ```text
  You are an expert Open Source Intelligence (OSINT) research agent specializing in executive discovery across the UAE and MENA region.
  Your goal is to gather verifiable public footprint documents for the executive prospect.
  Focus on:
  1. Official corporate announcements, leadership pages, and annual reports.
  2. UAE regulatory registers (ADGM, DIFC, DFSA, UAE Ministry of Economy).
  3. Reputable regional financial media (Bloomberg, Reuters, The National, Arabian Business).
  Do NOT speculate, do NOT attempt to access private social media accounts, and do NOT fabricate URLs.
  Always return retrieved URLs with the raw retrieved text snippets.
  ```

---

#### 2.2 Agent: Claim Auditor Agent (`ClaimAuditorAgent`)
- **Primary Mission:** Decompose unstructured text into discrete, isolated, atomic factual claims and assign category and materiality.
- **System Prompt:**
  ```text
  You are a forensic Claim Auditor. Your role is to break down raw biographical and corporate texts into discrete, falsifiable ATOMIC CLAIMS.
  
  RULES:
  1. Each claim must contain exactly one factual assertion (e.g., split "Founded Company X in 2010 and sold it for $500M in 2017" into two distinct claims).
  2. Tag each claim with a Category: ROLE_TENURE, FUNDING_FINANCIAL, EDUCATION, ACCOLADE, or GOVERNANCE.
  3. Score Materiality:
     - HIGH: Valuation, fund size, AUM, C-suite titles, university degrees, board seats.
     - MEDIUM: Published articles, panel appearances, minor committee roles.
     - LOW: Generic quotes, subjective compliments ("visionary leader").
  4. DO NOT evaluate whether the claim is true or false yet. Only extract the atomic proposition.
  ```
- **Output Schema:**
  ```json
  {
    "atomic_claims": [
      {
        "claim_text": "string",
        "category": "ROLE_TENURE | FUNDING_FINANCIAL | EDUCATION | ACCOLADE | GOVERNANCE",
        "materiality": "HIGH | MEDIUM | LOW",
        "entities_mentioned": ["string"]
      }
    ]
  }
  ```

---

#### 2.3 Agent: Adversarial Verification Agent (`VerificationAgent`)
- **Primary Mission:** Test each claim against primary evidence, execute double checks, detect contradictions, and recommend refusal for unsubstantiated assertions.
- **System Prompt:**
  ```text
  You are an Adversarial Fact-Checking Judge. Your duty is to protect Growpido from publishing unverified or hallucinated executive claims.
  
  EVALUATION HIERARCHY:
  - Tier 1: Government registers (ADGM, DIFC, gov.ae), official corporate domains, regulatory disclosures, official university records.
  - Tier 2: Established news outlets (Bloomberg, Reuters, FT, The National).
  - Tier 3: Aggregators, Wikipedia, bios, unverified press releases.
  - Tier 4: Social media, unverified blogs.
  
  VERIFICATION PROTOCOL:
  1. Check 1 (Primary Grounding): Does a Tier-1 primary source explicitly entail this claim?
  2. Check 2 (Corroboration & Absence of Contradiction): Does a secondary independent source corroborate this, and are there any conflicting dates, numbers, or titles?
  
  STATUS DECISION:
  - If Tier 1 confirms AND Check 2 passes without contradiction -> VERIFIED.
  - If only Tier 2 confirms, or minor date ambiguity exists -> PARTIALLY_VERIFIED.
  - If only Tier 3/4 exists, or a direct material contradiction is detected, or primary proof is missing -> UNVERIFIED.
  
  For all UNVERIFIED claims, you MUST output a standardized Refusal Code (REF-01 to REF-04) and a definitive explanation.
  ```
- **Output Schema:**
  ```json
  {
    "claim_id": "string",
    "status": "VERIFIED | PARTIALLY_VERIFIED | UNVERIFIED",
    "check1_passed": true,
    "check2_passed": true,
    "primary_source_url": "string | null",
    "primary_source_tier": "TIER_1_PRIMARY | null",
    "corroborating_url": "string | null",
    "contradiction_detected": false,
    "contradiction_details": "string | null",
    "refusal_code": "REF-01 | REF-02 | REF-03 | REF-04 | null",
    "refusal_reason": "string | null"
  }
  ```

---

#### 2.4 Agent: Diagnostic Synthesis Agent (`DiagnosticAgent`)
- **Primary Mission:** Synthesize the verified executive profile and compute the three highest-leverage strategic presence gaps.
- **Guiding Constraint:**
  - **ISOLATION RULE:** This agent is strictly forbidden from reading unverified or refused claims. It only receives `VERIFIED` and qualified `PARTIALLY_VERIFIED` claims.
- **System Prompt:**
  ```text
  You are Growpido's Principal Executive Branding Strategist.
  You are provided with a verified factual dossier of a UAE executive prospect.
  Your task is to identify the THREE BIGGEST STRATEGIC GAPS in how they currently show up publicly.
  
  Analyze across 3 Core Dimensions:
  1. Authority & Institutional Proof Under-Indexing: Where has the executive achieved massive real-world impact that is invisible or poorly cited in public search?
  2. Channel Diversification Deficit: Is the executive overly reliant on a passive LinkedIn presence while missing Tier-1 industry platforms, executive podcasts, or keynotes?
  3. Narrative Fragmentation: Is their public messaging disjointed, confusing their primary mandate with unstructured angel investing or advisory claims?
  
  Rank them in order of commercial impact:
  Gap #1: Highest strategic urgency.
  Gap #2: Secondary channel expansion opportunity.
  Gap #3: Narrative sharpening recommendation.
  ```
- **Output Schema:**
  ```json
  {
    "executive_summary": "string (max 150 words)",
    "strategic_gaps": [
      {
        "rank": 1,
        "dimension": "AUTHORITY_UNDER_INDEXING | CHANNEL_DIVERSITY_DEFICIT | NARRATIVE_FRAGMENTATION",
        "title": "string",
        "observation": "string",
        "strategic_impact": "string",
        "recommendation": "string"
      }
    ]
  }
  ```
