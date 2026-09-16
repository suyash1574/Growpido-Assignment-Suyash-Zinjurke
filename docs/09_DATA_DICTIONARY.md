# Data Dictionary & Entity Catalog
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Document Purpose
This Data Dictionary defines every data entity, table, attribute, data type, validation rule, constraint, and description used across the Growpido Prospect to Diagnostic Engine.

---

### 2. Entity Catalog & Field Definitions

#### 2.1 Entity: `Prospect`
Represents the target executive identified by public LinkedIn parameters.

| Field Name | Type | Nullable | Primary / Foreign Key | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `prospect_id` | UUID (v4) | No | Primary Key | Unique system identifier for the prospect entity. |
| `linkedin_url` | String (255) | No | Unique | Canonical HTTPS LinkedIn profile URL. Must match regex. |
| `slug` | String (100) | No | Indexed | Clean URL identifier extracted from URL path. |
| `full_name` | String (150) | No | None | Canonical full name resolved from discovery sources. |
| `current_company`| String (150) | Yes | None | Primary active organization/fund affiliation. |
| `primary_role` | String (150) | Yes | None | Active corporate or executive title. |
| `location_country`| String (50) | No | Default: "UAE" | Geographic jurisdiction (must be UAE for Track B). |
| `status` | Enum (String)| No | None | `INITIALIZED`, `DISCOVERING`, `VERIFYING`, `AWAITING_REVIEW`, `APPROVED`. |
| `created_at` | Timestamp | No | Default: UTC Now | Record initialization timestamp. |
| `updated_at` | Timestamp | No | Auto-update | Last modification timestamp. |

---

#### 2.2 Entity: `EvidenceSource`
Represents any public web page, regulatory registry, or media article retrieved by the OSINT agent.

| Field Name | Type | Nullable | Primary / Foreign Key | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `source_id` | UUID (v4) | No | Primary Key | Unique identifier for the fetched evidence source. |
| `prospect_id` | UUID (v4) | No | Foreign Key (`Prospect.prospect_id`) | Associated prospect entity. |
| `url` | String (1024)| No | Indexed | Complete URL of the indexed public document. |
| `domain` | String (255) | No | Indexed | Fully qualified domain name (FQDN), e.g., `adgm.com`. |
| `source_tier` | Enum (String)| No | None | `TIER_1_PRIMARY`, `TIER_2_SECONDARY`, `TIER_3_AGGREGATOR`, `TIER_4_SOCIAL`. |
| `http_status` | Integer | Yes | None | HTTP response status code (e.g., 200, 301, 403). |
| `content_hash` | String (64) | No | None | SHA-256 hash of the cleaned text snapshot. |
| `raw_text_snippet`| Text | Yes | None | Extracted plaintext body snippet (up to 50KB). |
| `fetched_at` | Timestamp | No | Default: UTC Now | Exact retrieval timestamp. |

---

#### 2.3 Entity: `Claim`
Represents an isolated, atomic factual statement extracted from public evidence.

| Field Name | Type | Nullable | Primary / Foreign Key | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `claim_id` | UUID (v4) | No | Primary Key | Unique identifier for the extracted claim. |
| `prospect_id` | UUID (v4) | No | Foreign Key (`Prospect.prospect_id`) | Associated prospect entity. |
| `claim_text` | Text | No | None | Complete, self-contained factual assertion string. |
| `category` | Enum (String)| No | None | `ROLE_TENURE`, `FUNDING_FINANCIAL`, `EDUCATION`, `ACCOLADE`, `GOVERNANCE`. |
| `materiality` | Enum (String)| No | None | `HIGH`, `MEDIUM`, `LOW`. |
| `status` | Enum (String)| No | Indexed | `VERIFIED`, `PARTIALLY_VERIFIED`, `UNVERIFIED`. |
| `primary_source_id`| UUID (v4) | Yes | Foreign Key (`EvidenceSource.source_id`) | Tier-1 source anchoring the claim. |
| `secondary_source_id`| UUID (v4)| Yes | Foreign Key (`EvidenceSource.source_id`) | Corroborating Tier-1/2 source. |
| `check1_passed` | Boolean | No | Default: False | Status of primary authority and entailment check. |
| `check2_passed` | Boolean | No | Default: False | Status of corroboration and consistency check. |
| `contradiction_detected`| Boolean | No | Default: False | True if conflicting data exists across authoritative sources. |
| `refusal_code` | String (20) | Yes | None | Code if excluded: `REF-01`, `REF-02`, `REF-03`, `REF-04`. |
| `refusal_reason`| Text | Yes | None | Human-readable causal rationale for claim exclusion. |
| `human_override`| Boolean | No | Default: False | True if human advisor manually changed the status. |
| `override_notes`| Text | Yes | None | Mandatory advisor note explaining override rationale. |

---

#### 2.4 Entity: `StrategicGap`
Represents one of the three prioritized presence discrepancies synthesized for the executive diagnostic.

| Field Name | Type | Nullable | Primary / Foreign Key | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `gap_id` | UUID (v4) | No | Primary Key | Unique identifier for the strategic gap. |
| `prospect_id` | UUID (v4) | No | Foreign Key (`Prospect.prospect_id`) | Associated prospect entity. |
| `rank` | Integer | No | Check (1, 2, 3) | Priority ranking (1 = Highest Commercial Impact). |
| `dimension` | Enum (String)| No | None | `AUTHORITY_UNDER_INDEXING`, `CHANNEL_DIVERSITY_DEFICIT`, `NARRATIVE_FRAGMENTATION`. |
| `title` | String (150) | No | None | Concise, executive-ready headline for the gap. |
| `observation` | Text | No | None | Grounded factual evidence demonstrating the gap. |
| `strategic_impact`| Text | No | None | Why this gap hurts executive conversion or stature. |
| `recommendation`| Text | No | None | Actionable advisory solution offered by Growpido. |

---

#### 2.5 Entity: `AuditEvent`
Represents an immutable, append-only ledger entry tracking system execution, API calls, and human interactions.

| Field Name | Type | Nullable | Primary / Foreign Key | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `event_id` | UUID (v4) | No | Primary Key | Unique identifier for the audit event. |
| `prospect_id` | UUID (v4) | No | Foreign Key (`Prospect.prospect_id`) | Associated prospect entity. |
| `event_type` | String (50) | No | Indexed | `URL_INGESTED`, `QUERY_EXECUTED`, `CLAIM_EXTRACTED`, `CHECK_EVALUATED`, `CLAIM_REFUSED`, `HUMAN_OVERRIDE`, `DIAGNOSTIC_COMPILED`. |
| `actor` | String (50) | No | None | `SYSTEM_AGENT` or advisor username (e.g., `advisor_tariq`). |
| `event_payload` | JSON | No | None | Serialized structured parameters, diffs, or hashes. |
| `timestamp` | Timestamp | No | Default: UTC Now | High-precision event timestamp. |
