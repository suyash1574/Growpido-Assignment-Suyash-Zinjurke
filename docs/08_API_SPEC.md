# API Specification & Service Contracts
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Overview
The Growpido Engine exposes clean internal service contracts and REST endpoints, facilitating seamless interaction between the Streamlit presentation tier, backend orchestrator, and external audit consumers.

---

### 2. Base Endpoint Definitions
- **Base URL:** `http://localhost:8501/api/v1` (or internal Python service dispatcher)
- **Content-Type:** `application/json`
- **Authentication:** Bearer token / Internal session token

---

### 3. API Endpoints

#### 3.1 `POST /research/start`
Initiates target profile ingestion and begins asynchronous OSINT discovery.

**Request Payload:**
```json
{
  "linkedin_url": "https://www.linkedin.com/in/ronaldo-mouchawar-souq",
  "region_hint": "UAE",
  "priority": "HIGH"
}
```

**Response Payload (202 Accepted):**
```json
{
  "status": "ACCEPTED",
  "session_id": "8f3e2a10-c4b9-4d6b-9c88-12a3b4c5d6e7",
  "target_slug": "ronaldo-mouchawar-souq",
  "current_stage": "DISCOVERY",
  "created_at": "2026-09-16T04:10:00Z"
}
```

---

#### 3.2 `GET /research/{session_id}/claims`
Retrieves all extracted claims with current verification status and evidence links.

**Response Payload (200 OK):**
```json
{
  "session_id": "8f3e2a10-c4b9-4d6b-9c88-12a3b4c5d6e7",
  "total_claims": 8,
  "claims": [
    {
      "claim_id": "c1a2b3c4-0001-4000-8000-000000000001",
      "text": "Vice President of Amazon Middle East & North Africa (MENA).",
      "category": "ROLE_TENURE",
      "materiality": "HIGH",
      "status": "VERIFIED",
      "primary_source": {
        "url": "https://press.aboutamazon.com/executives/ronaldo-mouchawar",
        "tier": "TIER_1_PRIMARY",
        "snippet": "Ronaldo Mouchawar serves as Vice President of Amazon MENA..."
      },
      "verification_count": 2,
      "contradiction_detected": false
    },
    {
      "claim_id": "c1a2b3c4-0002-4000-8000-000000000002",
      "text": "Holds a private venture fund with over $100M committed capital.",
      "category": "FUNDING_FINANCIAL",
      "materiality": "HIGH",
      "status": "UNVERIFIED",
      "primary_source": null,
      "verification_count": 0,
      "contradiction_detected": false,
      "refusal_reason": "Aggregator mention only; no regulatory filing or audited fund disclosure located."
    }
  ]
}
```

---

#### 3.3 `POST /verification/verify-claim`
On-demand verification execution for a single claim against primary sources.

**Request Payload:**
```json
{
  "claim_id": "c1a2b3c4-0001-4000-8000-000000000001",
  "candidate_source_urls": [
    "https://press.aboutamazon.com/...",
    "https://www.adgm.com/..."
  ],
  "force_double_check": true
}
```

**Response Payload (200 OK):**
```json
{
  "claim_id": "c1a2b3c4-0001-4000-8000-000000000001",
  "status": "VERIFIED",
  "check_1_passed": true,
  "check_2_passed": true,
  "contradiction": false,
  "confidence_score": 0.98,
  "verified_at": "2026-09-16T04:11:15Z"
}
```

---

#### 3.4 `POST /review/override`
Enables human advisors at the Human Gate to override or edit machine classifications.

**Request Payload:**
```json
{
  "session_id": "8f3e2a10-c4b9-4d6b-9c88-12a3b4c5d6e7",
  "claim_id": "c1a2b3c4-0002-4000-8000-000000000002",
  "new_status": "PARTIALLY_VERIFIED",
  "override_rationale": "Secondary interview on Bloomberg UAE quotes the $100M figure, though formal fund registrar filing remains pending.",
  "auditor_id": "advisor_tariq_almansoor"
}
```

**Response Payload (200 OK):**
```json
{
  "status": "OVERRIDE_RECORDED",
  "claim_id": "c1a2b3c4-0002-4000-8000-000000000002",
  "updated_status": "PARTIALLY_VERIFIED",
  "audit_event_id": "aud-9988-7766"
}
```

---

#### 3.5 `GET /diagnostic/{session_id}`
Renders and delivers the complete, verified One-Page Diagnostic and Refusal Breakdown.

**Response Payload (200 OK):**
```json
{
  "session_id": "8f3e2a10-c4b9-4d6b-9c88-12a3b4c5d6e7",
  "prospect": {
    "name": "Ronaldo Mouchawar",
    "primary_role": "VP, Amazon MENA & Co-founder, Souq.com",
    "location": "Dubai, UAE"
  },
  "verified_facts_count": 6,
  "refused_claims_count": 2,
  "strategic_gaps": [
    {
      "rank": 1,
      "dimension": "AUTHORITY_UNDER_INDEXING",
      "title": "Unleveraged Pioneer Authority",
      "observation": "Built the Arab world's first $580M tech exit, yet personal website/direct thought-leadership domain is inactive.",
      "strategic_impact": "Diminishes executive standing when courting Tier-1 global institutional co-investors.",
      "recommendation": "Establish an authoritative digital domain housing verified keynotes, case studies, and investment criteria."
    },
    {
      "rank": 2,
      "dimension": "CHANNEL_DIVERSITY_DEFICIT",
      "title": "Monolithic LinkedIn Reliance",
      "observation": "Public commentary is strictly siloed on LinkedIn; absent from leading international tech podcast indices and video archives.",
      "strategic_impact": "Restricts reach to passive LinkedIn followers rather than active institutional allocators.",
      "recommendation": "Repurpose quarterly strategic insights into guest columns on Tier-1 financial media and targeted fireside sessions."
    },
    {
      "rank": 3,
      "dimension": "NARRATIVE_FRAGMENTATION",
      "title": "Corporate vs. Independent Angel Dichotomy",
      "observation": "Public narrative conflates Amazon VP duties with private venture advisory without distinct positioning guardrails.",
      "strategic_impact": "Creates ambiguity regarding commercial focus and investment vehicle mandate.",
      "recommendation": "Codify a distinct 'Executive Fellowship & Angel Philosophy' narrative pillar separate from corporate operations."
    }
  ],
  "refusal_sample": {
    "refused_claim": "Personal angel portfolio contains 40+ active startups valued over $50M.",
    "refusal_reason": "No regulatory filing (ADGM/DIFC) or certified audit statement available. Refused under Rule BR-R01 (Accuracy Dominance)."
  },
  "audit_log_url": "/api/v1/audit/8f3e2a10-c4b9-4d6b-9c88-12a3b4c5d6e7"
}
```
