# System Requirements Document & System Requirements Specification (SRD / SRS)
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. System Overview & Technology Stack
The Growpido Prospect to Diagnostic Engine is an agentic, fact-deterministic intelligence pipeline implemented in **Python 3.11+**, utilizing a modular micro-service architecture with a reactive **Streamlit** presentation tier, structured schema validation via **Pydantic v2**, persistent audit storage via **SQLite**, and an asynchronous LLM orchestration layer powered by **Groq (Llama 3.3 70B Versatile / Llama 3.1 70B)** for sub-second, low-latency structured reasoning and adversarial claim auditing.

---

### 2. Architectural Blueprint & Component Topology
```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION TIER                        │
│     Streamlit Interactive Web UI (Human Gate & Diagnostic)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / WebSocket
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                       │
│     LangGraph / Async Pipeline Orchestrator (Stateful)      │
└──────────────┬───────────────┬───────────────┬──────────────┘
               │               │               │
               ▼               ▼               ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │ Discovery   │ │ Claim       │ │ Double-Check│
        │ Agent       │ │ Auditor     │ │ Verification│
        └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
               │               │               │
               └───────────────┼───────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    DETERMINISTIC ENGINES                    │
│   • Source Tier Classifier       • Contradiction Detector   │
│   • Adversarial Refusal Engine   • Gap Ranking Synthesizer  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     PERSISTENCE LAYER                       │
│   • SQLite (Metadata, Claims, Verifications, Audit Trail)   │
│   • Local JSON Evidence Store (Raw HTML/Text Snapshots)     │
└─────────────────────────────────────────────────────────────┘
```

---

### 3. Technical Requirements Specification

#### 3.1 Compute & Runtime Environment
- **Runtime:** Python 3.11.x (x86-64 / ARM64).
- **Core Dependencies:**
  - `streamlit >= 1.38.0`: Reactive user interface & human gate dashboard.
  - `pydantic >= 2.8.0`: Strict type validation and JSON schema enforcement.
  - `httpx >= 0.27.0`: High-concurrency async HTTP client with connection pooling.
  - `beautifulsoup4 >= 4.12.0`: HTML sanitization, text token extraction, metadata parsing.
  - `sqlite3`: Embedded ACID-compliant database for audit logs.
  - `tavily-python / duckduckgo-search`: Multi-engine OSINT search providers.
  - `google-genai / openai`: LLM reasoning, decomposition, and gap synthesis.

#### 3.2 Non-Functional Requirements (NFRs)
| NFR ID | Category | Requirement Specification | Target Benchmark |
| :--- | :--- | :--- | :--- |
| **NFR-PERF-001** | Latency | End-to-end execution from LinkedIn URL to staged Human Gate. | < 90 seconds (P95) |
| **NFR-PERF-002** | Concurrency | Async web crawling with bounded rate limits. | Max 10 concurrent requests; polite crawling (1 req/sec/domain). |
| **NFR-DET-001** | Determinism | Verification logic must evaluate against regex/string search anchors before LLM synthesis. | 100% deterministic source tiering. |
| **NFR-REL-001** | Resilience | Search API failover mechanism. | If Primary Search (Tavily) errors, auto-failover to DuckDuckGo/SerpAPI. |
| **NFR-SEC-001** | Data Privacy | No storage of sensitive PII (passwords, private emails, phone numbers). | Zero non-public PII retained. |
| **NFR-AUD-001** | Immutability | All verification decisions written with SHA-256 hash of evidence snippet. | 100% cryptographic provenance. |

---

### 4. Detailed Component Technical Specifications

#### 4.1 Orchestrator State Machine (`PipelineContext`)
The pipeline state is modeled as an immutable Pydantic state container passed across pipeline nodes:
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PipelineState(BaseModel):
    session_id: str
    prospect_url: str
    prospect_slug: str
    canonical_name: Optional[str] = None
    target_company: Optional[str] = None
    discovery_urls: List[str] = Field(default_factory=list)
    raw_evidence_snapshots: dict = Field(default_factory=dict)
    extracted_claims: List[dict] = Field(default_factory=list)
    verification_results: List[dict] = Field(default_factory=list)
    refused_claims: List[dict] = Field(default_factory=list)
    identified_gaps: List[dict] = Field(default_factory=list)
    human_approved: bool = False
    audit_events: List[dict] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

#### 4.2 Deterministic Verification Pipeline
The verification layer does not solely rely on an LLM. It implements a two-stage hybrid pipeline:
1. **Algorithmic Text Extraction:** Regex extraction of dates, currency figures, and company strings from raw fetched text.
2. **LLM Entailment Classifier:** Prompted with zero-temperature JSON mode:
   - System instruction: *"You are an adversarial fact auditor. Answer ONLY whether the provided source snippet logically entails the claim. If any ambiguity or contradiction exists, return false."*
3. **Double-Check Confirmation:** Check #1 evaluates primary domain authority; Check #2 confirms absence of counter-evidence in secondary press or independent registries.

#### 4.3 Persistence Architecture (SQLite Schema)
```sql
CREATE TABLE IF NOT EXISTS prospects (
    prospect_id TEXT PRIMARY KEY,
    linkedin_url TEXT NOT NULL,
    full_name TEXT NOT NULL,
    current_company TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evidence_sources (
    source_id TEXT PRIMARY KEY,
    prospect_id TEXT NOT NULL,
    url TEXT NOT NULL,
    domain TEXT NOT NULL,
    source_tier TEXT NOT NULL,
    http_status INTEGER,
    content_hash TEXT NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prospect_id) REFERENCES prospects(prospect_id)
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY,
    prospect_id TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    category TEXT NOT NULL,
    materiality TEXT NOT NULL,
    status TEXT NOT NULL, -- VERIFIED, PARTIALLY_VERIFIED, UNVERIFIED
    primary_source_id TEXT,
    check1_passed BOOLEAN,
    check2_passed BOOLEAN,
    contradiction_detected BOOLEAN,
    refusal_reason TEXT,
    human_override_status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prospect_id) REFERENCES prospects(prospect_id),
    FOREIGN KEY(primary_source_id) REFERENCES evidence_sources(source_id)
);

CREATE TABLE IF NOT EXISTS audit_log (
    event_id TEXT PRIMARY KEY,
    prospect_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_payload JSON NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 5. Failure Handling & Error Recovery
- **E01: Rate Limit on Search Engine:** Exponential backoff with jitter (`wait = 2^attempt + uniform(0, 1)`); fallback to secondary search engine.
- **E02: Blocked/Gated Target Page (HTTP 403/429):** Log warning in audit trail, downgrade domain reachability score, and exclude from Tier-1 consideration without crashing pipeline.
- **E03: LLM JSON Parse Error:** Pydantic validation retry loop (max 3 attempts); if parsing fails repeatedly, quarantine claim into `UNVERIFIED` state with error code `ERR_LLM_PARSER_FAILURE`.
- **E04: Low Evidence Breadth:** If total accessible public sources < 3, flag profile as `LOW_DIGITAL_FOOTPRINT` and generate Diagnostic highlighting absence of public authority records as primary strategic gap.
