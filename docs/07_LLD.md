# Low-Level Design (LLD)
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Document Overview
The Low-Level Design (LLD) translates system architecture into concrete object models, interface contracts, service classes, and method signatures. It guides engineers directly in implementing Python classes and Pydantic schemas.

---

### 2. Class Diagram & Domain Models
```
┌───────────────────────────┐         ┌───────────────────────────┐
│       ProspectEntity      │ 1     * │        EvidenceSource     │
├───────────────────────────┤─────────├───────────────────────────┤
│ + prospect_id: UUID       │         │ + source_id: UUID         │
│ + linkedin_url: str       │         │ + prospect_id: UUID       │
│ + full_name: str          │         │ + url: str                │
│ + target_company: str     │         │ + domain: str             │
│ + status: ProspectStatus  │         │ + tier: SourceTier        │
└─────────────┬─────────────┘         │ + raw_content_hash: str   │
              │ 1                     └─────────────┬─────────────┘
              │                                     │ 1
              ▼ *                                   ▼ *
┌───────────────────────────┐         ┌───────────────────────────┐
│        ClaimEntity        │ 1     * │     VerificationRecord    │
├───────────────────────────┤─────────├───────────────────────────┤
│ + claim_id: UUID          │         │ + verification_id: UUID   │
│ + prospect_id: UUID       │         │ + claim_id: UUID          │
│ + claim_text: str         │         │ + primary_source_id: UUID │
│ + category: ClaimCategory │         │ + check1_passed: bool     │
│ + materiality: Materiality│         │ + check2_passed: bool     │
│ + status: ClaimStatus     │         │ + contradiction: bool     │
│ + refusal_reason: str     │         │ + confidence_score: float │
└─────────────┬─────────────┘         └───────────────────────────┘
              │ 1
              │
              ▼ *
┌───────────────────────────┐         ┌───────────────────────────┐
│      StrategicGapEntity   │         │       AuditEventEntity    │
├───────────────────────────┤         ├───────────────────────────┤
│ + gap_id: UUID            │         │ + event_id: UUID          │
│ + prospect_id: UUID       │         │ + prospect_id: UUID       │
│ + rank: int (1, 2, 3)     │         │ + event_type: str         │
│ + dimension: GapDimension │         │ + payload: dict           │
│ + title: str              │         │ + timestamp: datetime     │
│ + observation: str        │         └───────────────────────────┘
│ + strategic_impact: str   │
│ + recommendation: str     │
└───────────────────────────┘
```

---

### 3. Enumerations & Value Objects
```python
from enum import Enum

class ProspectStatus(str, Enum):
    INITIALIZED = "INITIALIZED"
    DISCOVERING = "DISCOVERING"
    EXTRACTING = "EXTRACTING"
    VERIFYING = "VERIFYING"
    AWAITING_REVIEW = "AWAITING_REVIEW"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class SourceTier(str, Enum):
    TIER_1_PRIMARY = "TIER_1_PRIMARY"      # Official registry, Gov, Corporate primary
    TIER_2_SECONDARY = "TIER_2_SECONDARY"  # Reputable financial press (Bloomberg, Reuters)
    TIER_3_AGGREGATOR = "TIER_3_AGGREGATOR"# Wikipedia, Crunchbase mirror, bios
    TIER_4_SOCIAL = "TIER_4_SOCIAL"        # Twitter/X, Medium, unverified blogs

class ClaimCategory(str, Enum):
    ROLE_TENURE = "ROLE_TENURE"
    FUNDING_FINANCIAL = "FUNDING_FINANCIAL"
    EDUCATION_CREDENTIAL = "EDUCATION_CREDENTIAL"
    ACCOLADE_AWARD = "ACCOLADE_AWARD"
    GOVERNANCE_BOARD = "GOVERNANCE_BOARD"
    THOUGHT_LEADERSHIP = "THOUGHT_LEADERSHIP"

class Materiality(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ClaimStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    UNVERIFIED = "UNVERIFIED"

class GapDimension(str, Enum):
    AUTHORITY_UNDER_INDEXING = "AUTHORITY_UNDER_INDEXING"
    CHANNEL_DIVERSITY_DEFICIT = "CHANNEL_DIVERSITY_DEFICIT"
    NARRATIVE_FRAGMENTATION = "NARRATIVE_FRAGMENTATION"
```

---

### 4. Service Interfaces & Method Signatures

#### 4.1 Ingestion Service (`IngestService`)
```python
class IngestService:
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validates that URL is a clean, public LinkedIn profile URL."""
        ...
        
    @staticmethod
    def parse_slug(url: str) -> str:
        """Extracts and cleans profile slug token."""
        ...
        
    def initialize_prospect(self, url: str) -> ProspectEntity:
        """Creates initial prospect record in SQLite."""
        ...
```

#### 4.2 Discovery Service (`DiscoveryService`)
```python
class DiscoveryService:
    def __init__(self, search_client, http_client):
        self.search_client = search_client
        self.http_client = http_client

    async def execute_search(self, prospect: ProspectEntity) -> List[EvidenceSource]:
        """Runs multi-query searches and persists raw source metadata."""
        ...

    def classify_source_tier(self, url: str) -> SourceTier:
        """Applies deterministic regex rules to map domains to SourceTier 1-4."""
        ...

    async def fetch_snapshot(self, url: str) -> str:
        """Fetches raw HTML, strips noise, returns clean plaintext."""
        ...
```

#### 4.3 Claim Auditor Service (`ClaimAuditorService`)
```python
class ClaimAuditorService:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    async def extract_atomic_claims(
        self, prospect: ProspectEntity, sources: List[EvidenceSource]
    ) -> List[ClaimEntity]:
        """Deconstructs unstructured text into discrete atomic claims with categories."""
        ...

    def score_materiality(self, claim: ClaimEntity) -> Materiality:
        """Classifies claim materiality into High, Medium, or Low."""
        ...
```

#### 4.4 Verification Service (`VerificationService`)
```python
class VerificationService:
    def __init__(self, llm_client, search_client):
        self.llm_client = llm_client
        self.search_client = search_client

    async def verify_claim(
        self, claim: ClaimEntity, available_sources: List[EvidenceSource]
    ) -> VerificationRecord:
        """
        Executes double-check verification:
        Check 1: Authority and semantic entailment against Tier-1 source.
        Check 2: Corroboration search and contradiction detection.
        """
        ...

    def detect_contradiction(
        self, claim: ClaimEntity, candidate_snippets: List[str]
    ) -> bool:
        """Evaluates whether conflicting statements exist regarding date, title, or value."""
        ...
```

#### 4.5 Refusal & Reason Service (`RefusalService`)
```python
class RefusalService:
    @staticmethod
    def process_exclusions(claims: List[ClaimEntity]) -> List[ClaimEntity]:
        """
        Filters out claims that fail verification and attaches standardized
        refusal codes (REF-01 to REF-04) and contextual explanations.
        """
        ...
```

#### 4.6 Strategic Gap & Diagnostic Service (`DiagnosticService`)
```python
class DiagnosticService:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def synthesize_presence_gaps(
        self, prospect: ProspectEntity, verified_claims: List[ClaimEntity]
    ) -> List[StrategicGapEntity]:
        """Synthesizes exactly three prioritized strategic presence gaps."""
        ...

    def render_one_page_diagnostic(
        self,
        prospect: ProspectEntity,
        verified_claims: List[ClaimEntity],
        refused_claims: List[ClaimEntity],
        gaps: List[StrategicGapEntity],
    ) -> str:
        """Generates executive one-page Markdown and HTML presentation."""
        ...
```

#### 4.7 Audit Ledger Service (`AuditService`)
```python
class AuditService:
    def log_event(self, prospect_id: str, event_type: str, payload: dict) -> None:
        """Writes an immutable, timestamped event to the SQLite audit log."""
        ...
        
    def export_audit_trail(self, prospect_id: str) -> dict:
        """Returns the complete, chronologically ordered audit log for export."""
        ...
```
