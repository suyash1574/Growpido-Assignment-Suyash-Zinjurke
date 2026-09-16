from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl

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
    TIER_1_PRIMARY = "TIER_1_PRIMARY"      # Official registries, gov portals, primary corporate domains
    TIER_2_SECONDARY = "TIER_2_SECONDARY"  # Reputable financial press (Bloomberg, Reuters, FT, The National)
    TIER_3_AGGREGATOR = "TIER_3_AGGREGATOR"# Aggregators, Wikipedia, bios, directories (Discovery only)
    TIER_4_SOCIAL = "TIER_4_SOCIAL"        # Social media, unverified blogs, forums (Quarantined)

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

class Prospect(BaseModel):
    prospect_id: UUID = Field(default_factory=uuid4)
    linkedin_url: str
    slug: str
    full_name: str
    current_company: Optional[str] = None
    primary_role: Optional[str] = None
    location_country: str = "UAE"
    status: ProspectStatus = ProspectStatus.INITIALIZED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class EvidenceSource(BaseModel):
    source_id: UUID = Field(default_factory=uuid4)
    prospect_id: UUID
    url: str
    domain: str
    source_tier: SourceTier
    http_status: Optional[int] = 200
    content_hash: str
    raw_text_snippet: Optional[str] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

class Claim(BaseModel):
    claim_id: UUID = Field(default_factory=uuid4)
    prospect_id: UUID
    claim_text: str
    category: ClaimCategory = ClaimCategory.ROLE_TENURE
    materiality: Materiality = Materiality.MEDIUM
    status: ClaimStatus = ClaimStatus.UNVERIFIED
    primary_source_id: Optional[UUID] = None
    primary_source_url: Optional[str] = None
    secondary_source_id: Optional[UUID] = None
    secondary_source_url: Optional[str] = None
    check1_passed: bool = False
    check2_passed: bool = False
    contradiction_detected: bool = False
    contradiction_details: Optional[str] = None
    refusal_code: Optional[str] = None
    refusal_reason: Optional[str] = None
    human_override: bool = False
    override_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

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

class AuditEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    prospect_id: UUID
    event_type: str
    actor: str = "SYSTEM_AGENT"
    event_payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
