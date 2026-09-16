# Phase 1: Data Model Specification

**Feature**: `001-prospect-to-diagnostic`  
**Date**: 2026-09-16  
**Status**: Completed  

---

## 1. Domain Entities & Schemas

### 1.1 `Prospect`
Represents the target executive profile.

```python
class Prospect(BaseModel):
    prospect_id: UUID = Field(default_factory=uuid4)
    linkedin_url: HttpUrl
    slug: str
    full_name: str
    current_company: Optional[str] = None
    primary_role: Optional[str] = None
    location_country: str = "UAE"
    status: ProspectStatus = ProspectStatus.INITIALIZED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Validation & Integrity Rules:**
- `linkedin_url` must match regex: `^https:\/\/(www\.)?linkedin\.com\/in\/[a-zA-Z0-9_-]+\/?$`
- `slug` must be alphanumeric with hyphens/underscores.
- `status` transitions: `INITIALIZED` ➔ `DISCOVERING` ➔ `EXTRACTING` ➔ `VERIFYING` ➔ `AWAITING_REVIEW` ➔ `APPROVED` ➔ `COMPLETED`.

---

### 1.2 `EvidenceSource`
Represents a retrieved public web page or official regulatory registry record.

```python
class SourceTier(str, Enum):
    TIER_1_PRIMARY = "TIER_1_PRIMARY"      # Official registries, gov portals, primary corporate domains
    TIER_2_SECONDARY = "TIER_2_SECONDARY"  # Reputable financial press (Bloomberg, Reuters, FT, The National)
    TIER_3_AGGREGATOR = "TIER_3_AGGREGATOR"# Aggregators, Wikipedia, bios, directories (Discovery only)
    TIER_4_SOCIAL = "TIER_4_SOCIAL"        # Social media, unverified blogs, forums (Quarantined)

class EvidenceSource(BaseModel):
    source_id: UUID = Field(default_factory=uuid4)
    prospect_id: UUID
    url: HttpUrl
    domain: str
    source_tier: SourceTier
    http_status: Optional[int] = None
    content_hash: str  # SHA-256 hash of cleaned text
    raw_text_snippet: Optional[str] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 1.3 `Claim`
Represents an isolated, atomic factual statement extracted from public evidence.

```python
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

class Claim(BaseModel):
    claim_id: UUID = Field(default_factory=uuid4)
    prospect_id: UUID
    claim_text: str
    category: ClaimCategory
    materiality: Materiality
    status: ClaimStatus = ClaimStatus.UNVERIFIED
    primary_source_id: Optional[UUID] = None
    secondary_source_id: Optional[UUID] = None
    check1_passed: bool = False
    check2_passed: bool = False
    contradiction_detected: bool = False
    refusal_code: Optional[str] = None  # REF-01 to REF-05
    refusal_reason: Optional[str] = None
    human_override: bool = False
    override_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 1.4 `StrategicGap`
Represents one of the three prioritized public presence discrepancies.

```python
class GapDimension(str, Enum):
    AUTHORITY_UNDER_INDEXING = "AUTHORITY_UNDER_INDEXING"
    CHANNEL_DIVERSITY_DEFICIT = "CHANNEL_DIVERSITY_DEFICIT"
    NARRATIVE_FRAGMENTATION = "NARRATIVE_FRAGMENTATION"

class StrategicGap(BaseModel):
    gap_id: UUID = Field(default_factory=uuid4)
    prospect_id: UUID
    rank: int = Field(ge=1, le=3)
    dimension: GapDimension
    title: str
    observation: str
    strategic_impact: str
    recommendation: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 1.5 `AuditEvent`
Represents an immutable, timestamped record of pipeline execution and human overrides.

```python
class AuditEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    prospect_id: UUID
    event_type: str
    actor: str = "SYSTEM_AGENT"
    event_payload: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

---

## 2. Entity Relationship Diagram (ERD)

```
┌───────────────────────────┐         ┌───────────────────────────┐
│         Prospect          │ 1     * │       EvidenceSource      │
├───────────────────────────┤─────────├───────────────────────────┤
│ + prospect_id (PK)        │         │ + source_id (PK)          │
│ + linkedin_url            │         │ + prospect_id (FK)        │
│ + full_name               │         │ + url                     │
│ + status                  │         │ + domain                  │
└─────────────┬─────────────┘         │ + source_tier             │
              │ 1                     │ + content_hash            │
              │                       └─────────────┬─────────────┘
              ▼ *                                   │ 1
┌───────────────────────────┐                       │
│           Claim           │                       │
├───────────────────────────┤                       │
│ + claim_id (PK)           │                       │
│ + prospect_id (FK)        │                       │
│ + claim_text              │                       │
│ + status (VERIFIED/...)   │                       │
│ + primary_source_id (FK)  │───────────────────────┘ *
│ + secondary_source_id (FK)│
│ + check1_passed           │
│ + check2_passed           │
│ + contradiction_detected  │
│ + refusal_code            │
│ + refusal_reason          │
└─────────────┬─────────────┘
              │ 1
              │
              ▼ *
┌───────────────────────────┐         ┌───────────────────────────┐
│       StrategicGap        │         │         AuditEvent        │
├───────────────────────────┤         ├───────────────────────────┤
│ + gap_id (PK)             │         │ + event_id (PK)           │
│ + prospect_id (FK)        │         │ + prospect_id (FK)        │
│ + rank (1, 2, 3)          │         │ + event_type              │
│ + dimension               │         │ + actor                   │
│ + title                   │         │ + event_payload           │
│ + recommendation          │         │ + timestamp               │
└───────────────────────────┘         └───────────────────────────┘
```
