# Feature Specification: Name-Based Prospect Search & Global Authority Verification

**Feature Branch**: `002-name-search-verification`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "we want application like when we enter the persons name he will retrive them from the linkdin and then match we will only enter the name of the person no the entire link of linkdin , whenw e enter the name there will get the human approval to confirm the right person with the first source of the linkdin also even for the correcct info it giving wrong answer ... Narendra Modi has served as the Prime Minister of India ... all unverified ..."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Name-Based Prospect Search & Human Confirmation Gate (Priority: P1)

As an executive research advisor, I want to enter only the prospect's name (with optional role or company keywords) instead of hunting for full profile URLs, so that the system searches public business networks, discovers candidate profiles, and presents a candidate confirmation gate where I can review and select the exact person before launching deep investigation.

**Why this priority**: Eliminates user friction of finding and copying profile URLs manually, while preserving sovereign human gate control to prevent investigating the wrong person.

**Independent Test**: Can be tested by typing "Ronaldo Mouchawar" or "Narendra Modi" into the name search field. The system retrieves candidate profile cards showing name, headline, location, and source link; the advisor clicks "Confirm & Research Target", which initiates deep intelligence discovery for that specific individual.

**Acceptance Scenarios**:

1. **Given** the search dashboard, **When** an advisor enters a name (e.g. "Ronaldo Mouchawar") and submits search, **Then** the system presents 1 to 5 matching candidate profiles with their current headline, organization, location, and verified profile URL.
2. **Given** multiple candidate matches, **When** the advisor identifies the desired target and clicks "Confirm Target", **Then** the candidate is locked as the active target and the deep intelligence pipeline begins.
3. **Given** ambiguous names with many public figures, **When** the advisor enters optional disambiguation context (e.g. company "Amazon" or role "Prime Minister"), **Then** the search ranks the most relevant matching profile first.
4. **Given** no public profile match found, **When** search completes, **Then** the system clearly displays a "No candidate profiles found" notification and invites the advisor to refine the name or supply additional keywords.

---

### User Story 2 - Global Tier-1 Authority Grounding & Accurate Verification (Priority: P1)

As a senior intelligence auditor, I want fact verification to correctly identify official national government registries, gazettes, state portals, and recognized corporate domains worldwide (not just UAE-specific endpoints), so that legitimate factual assertions (e.g., tenure of heads of state, international executives, ministers, public company directors) are accurately verified rather than falsely quarantined under refusal codes.

**Why this priority**: Directly resolves the critical accuracy defect where legitimate, public-record assertions (such as a prime minister's term or global executive's corporate role) were erroneously failed by Check 1 and Check 2 due to overly restrictive domain rules.

**Independent Test**: Can be tested by running verification on a prominent national or global figure (e.g., "Narendra Modi" or global corporate leader). Official government portals (`.gov`, `.gov.in`, `.gov.uk`, `.nic.in`) and official gazettes are recognized as Tier-1 primary sources, allowing substantiated assertions to achieve `VERIFIED` status with cited provenance.

**Acceptance Scenarios**:

1. **Given** an assertion supported by an official national government registry or state domain (e.g., `.gov`, `.gov.*`, `.nic.in`, `.parliament.*`), **When** Check 1 runs, **Then** the system classifies the domain as Tier-1 Primary Authority and evaluates entailment without geographic restriction.
2. **Given** an assertion confirmed by official government records and corroborated by secondary financial/news reporting, **When** Check 2 runs, **Then** the claim achieves `VERIFIED` status and renders in the Verified Fact Dossier with a clickable primary citation.
3. **Given** assertions with no primary government or corporate registry records, **When** verification fails, **Then** the claim is appropriately quarantined under the appropriate refusal code (`REF-01` through `REF-05`) with a specific causal explanation.

---

### User Story 3 - Adaptive Geography & Context-Aware Diagnostic Synthesis (Priority: P2)

As a strategic advisor, I want the Executive Diagnostic and Strategic Presence Gaps to dynamically adapt to the prospect's actual jurisdiction, sector, and operational theater (rather than assuming UAE commercial sector for all prospects), so that the diagnosis reflects the executive's true operating environment.

**Why this priority**: Avoids embarrassing misattributions (e.g., classifying a head of state or Silicon Valley CEO as a "UAE Commercial Sector Founder & Executive" or recommending UAE-specific podcasts).

**Independent Test**: Can be tested by evaluating a non-UAE prospect; the generated diagnostic header, sector baseline, and 3 Strategic Presence Gaps contextualize recommendations to the prospect's actual jurisdiction and leadership domain.

**Acceptance Scenarios**:

1. **Given** a confirmed target, **When** the system synthesizes the One-Page Diagnostic, **Then** the sector badge and jurisdiction reflect the prospect's true operational domain (e.g., "Public Governance / National Leadership | India" or "Technology & E-Commerce | Middle East").
2. **Given** the 3 Strategic Presence Gaps, **When** advisory recommendations are generated, **Then** channel diversification and thought leadership strategies target media and stakeholders appropriate to the prospect's specific region and industry.

---

## Edge Cases

- **Identical Common Names**: Multiple individuals sharing the same name in public business directories (e.g., "John Smith"). Handled by displaying headline, company, and location chips on candidate cards so advisors can disambiguate.
- **Direct LinkedIn URL Entry**: Advisors who already possess the exact profile URL can still paste the URL directly, bypassing the name disambiguation step.
- **State Domains with Unique TLDs**: National portals using non-standard ccTLDs (e.g., `nic.in`, `pmindia.gov.in`, `parliament.uk`, `gc.ca`, `admin.ch`). Deterministic classification recognizes national government naming conventions worldwide.
- **Figures with Broad Historical Tenures**: Claims with dates in multiple international formats (e.g., "26 May 2014" vs "May 26, 2014" vs "2014-05-26"). Token and entity extraction handles date variants during primary source entailment checks.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a Name Search interface allowing advisors to search prospects using full name and optional context keywords (company, role, or country).
- **FR-002**: System MUST retrieve public business profile candidates matching the query and extract canonical name, current headline, company, location, and verified profile URL.
- **FR-003**: System MUST render a Candidate Confirmation Gate displaying candidate match cards, enabling the advisor to review and explicitly select the intended person before initiating deep research.
- **FR-004**: System MUST preserve the option to enter a direct profile URL for advisors who already have the exact link.
- **FR-005**: System MUST classify sovereign national government portals (`.gov`, `.gov.*`, `.nic.in`, `.mil`, accredited state gazettes, official ministries) as Tier-1 Primary Authority worldwide without geographic bias.
- **FR-006**: System MUST classify accredited academic institutions (`.edu`, `.ac.*`), official regulatory filings, and corporate investor relations domains as Tier-1 Primary Authority globally.
- **FR-007**: System MUST perform Check 1 (Primary Authority Entailment) by searching and matching claims against discovered Tier-1 primary sources, accepting entailment when the assertion is directly supported by official records.
- **FR-008**: System MUST perform Check 2 (Independent Corroboration) against independent reputable sources, advancing substantiated assertions to `VERIFIED` status.
- **FR-009**: System MUST quarantine assertions lacking Tier-1 verification under standardized refusal codes (`REF-01` through `REF-05`) with human-readable justifications.
- **FR-010**: System MUST adapt prospect profile metadata (location, sector, domain) dynamically based on the verified profile rather than defaulting to hardcoded regional values.
- **FR-011**: System MUST tailor the 3 Strategic Presence Gaps (Authority Under-Indexing, Channel Diversity Deficit, Narrative Fragmentation) to the prospect's identified jurisdiction and leadership sphere.
- **FR-012**: System MUST support advisor status override on any claim at the Human Gate with mandatory audit rationale logging.

---

### Key Entities *(include if feature involves data)*

- **CandidateMatch**: Represents a potential prospect candidate returned from name search, including full name, headline/title, current company, geographic location, profile URL, and source snippet.
- **ProspectProfile**: Confirmed target entity containing full name, canonical profile URL, operational jurisdiction, sector, and lifecycle status.
- **Claim**: Extracted atomic proposition with category, materiality score, verification status (`VERIFIED`, `PARTIALLY_VERIFIED`, `UNVERIFIED`), primary source citation, corroboration status, and refusal code if quarantined.
- **StrategicPresenceGap**: Quantified presence gap with dimension, title, factual observation, strategic business impact, and tailored advisory action.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Advisors can discover and confirm the correct executive target by name in under 15 seconds without manually copying URLs.
- **SC-002**: For verified public figures with official national government or regulatory records, true factual claims achieve `VERIFIED` status with 0% false-negative refusal rate on verified primary assertions.
- **SC-003**: 100% of candidate disambiguation decisions require explicit human confirmation before initiating the multi-source audit pipeline.
- **SC-004**: Strategic Presence Gaps and executive briefing headers correctly reflect the prospect's verified jurisdiction in 100% of generated diagnostics.
- **SC-005**: The complete workflow from name entry to approved One-Page Diagnostic completes with zero rate-limit interruptions, supported by dual-engine failover.

---

## Assumptions

- Public web discovery respects zero-credential policy and operates exclusively on publicly accessible indexing.
- Name search leverages web search queries targeted at public business networks and official profiles.
- Human confirmation ensures that multiple individuals with identical or similar names are never conflated.
- The sovereign human-in-the-loop review gate remains the mandatory checkpoint prior to diagnostic compilation.
