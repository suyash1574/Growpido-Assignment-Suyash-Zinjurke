# Functional Requirements Document (FRD)
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Introduction & Traceability Overview
The Functional Requirements Document (FRD) bridges high-level business goals (BRD) and product features (PRD) with engineering specifications. Each requirement is assigned a standardized, permanent identifier (`FR-XXX-YYY`) to ensure 100% forward traceability to design components, test cases, and verification rules.

---

### 2. Functional Requirements Matrix

#### 2.1 Ingestion & Target Resolution (ING)
| Req ID | Title | Description | Priority | Rationale | Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-ING-001** | Public URL Ingest | The system shall accept a public LinkedIn profile URL via standard input field. | P0 | Starting point defined by Track B brief. | Accepts valid `https://*.linkedin.com/in/*` format; rejects malformed URLs. |
| **FR-ING-002** | Target Canonicalization | The system shall parse the URL slug and resolve the subject's canonical executive name and company. | P0 | Ensures disambiguation in search queries. | Correctly parses slug (e.g., `john-doe-ceo`) and initiates seed profile entity. |
| **FR-ING-003** | Anti-Scrape Compliance | The system shall not require LinkedIn user login credentials, cookies, or session bypass. | P0 | Adheres to legal and platform terms of service. | Operates purely on publicly indexed search and OSINT web records. |

#### 2.2 Public Discovery & Footprint Search (DIS)
| Req ID | Title | Description | Priority | Rationale | Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-DIS-001** | Multi-Engine Search | The system shall query public web search APIs using structured query templates. | P0 | Breadth of OSINT discovery. | Queries include: `"[Name]" "[Company]" UAE`, `"[Name]" executive bio`, `site:adgm.com OR site:difc.ae "[Name]"`. |
| **FR-DIS-002** | Source Tier Categorization | The system shall tag every retrieved URL with an authoritative source tier (Tier 1 to 4). | P0 | Establishes basis for hierarchical fact verification. | Official registries = Tier 1; Press = Tier 2; Aggregators = Tier 3; Social/Forums = Tier 4. |
| **FR-DIS-003** | Full-Text Snapshotting | The system shall retrieve and cache raw text payloads from accessible search result pages. | P0 | Enables deterministic NLP extraction without re-fetching. | Saves text, status code, timestamp, and MD5 hash of raw content. |

#### 2.3 Atomic Claim Extraction (CLM)
| Req ID | Title | Description | Priority | Rationale | Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-CLM-001** | Claim Decomposition | The system shall decompose collected public text into isolated atomic factual claims. | P0 | Complex sentences must be split to verify individual assertions. | Each claim contains a single predicate (e.g., "Founded Company X in 2019"). |
| **FR-CLM-002** | Category Tagging | The system shall categorize each claim into one of: `Role/Tenure`, `Company/AUM`, `Education`, `Accolades`, `ThoughtLeadership`. | P1 | Enables structured diagnostic mapping. | 100% of extracted claims receive exactly one primary category tag. |
| **FR-CLM-003** | Materiality Scoring | The system shall score claim materiality as `High`, `Medium`, or `Low`. | P1 | Focuses verification resources on high-stakes claims. | Claims involving financial metrics, board roles, or degrees are tagged `High`. |

#### 2.4 Primary Source & Double-Check Verification (VER)
| Req ID | Title | Description | Priority | Rationale | Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-VER-001** | Primary Source Anchoring | The system shall attempt to verify every material factual claim against a Tier-1 primary source. | P0 | Core rubric criteria (25 pts Fact Integrity). | Claims cannot be verified solely through Tier-3 aggregator links. |
| **FR-VER-002** | Check #1: Authority & Support | First verification check: Confirms the source domain has primary authority and semantic content explicitly entails the claim. | P0 | Prevents false-positive matches. | Returns boolean support flag, snippet quote, and semantic similarity score. |
| **FR-VER-003** | Check #2: Corroboration & Consistency | Second verification check: Confirms an independent source corroborates the assertion and checks for conflicting counter-statements. | P0 | Satisfies explicit brief rule: "checks it twice". | Requires independent domain confirmation OR definitive primary registry confirmation with no contradictions. |
| **FR-VER-004** | Contradiction Detection | The system shall flag claims where two authoritative sources present conflicting data. | P0 | Highlights high-risk ambiguities. | If Source A states tenure started 2020 and Source B states 2018, flag as `CONTRADICTION_DETECTED`. |
| **FR-VER-005** | Three-State Classification | The system shall assign each claim one status: `VERIFIED`, `PARTIALLY_VERIFIED`, `UNVERIFIED`. | P0 | Mandated by Growpido brief. | `VERIFIED`: 2 checks pass, Tier-1 source.<br>`PARTIALLY_VERIFIED`: 1 Tier-2 check or minor ambiguity.<br>`UNVERIFIED`: Tier 3/4 only, contradictory, or unsupported. |

#### 2.5 Refusal & Exclusion Engine (REF)
| Req ID | Title | Description | Priority | Rationale | Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-REF-001** | Adversarial Claim Refusal | The system shall refuse to include unverified or contradictory material claims in the core diagnostic. | P0 | Rubric requirement: "one claim your system refused to include and why". | At least one unverified/fluff claim is systematically withheld from the primary profile. |
| **FR-REF-002** | Standardized Refusal Reason | For every refused claim, the system shall assign a standardized refusal reason code and detailed explanation. | P0 | Transparency and advisor auditing. | Reason codes include: `ERR_NO_PRIMARY_SOURCE`, `ERR_UNRESOLVED_CONTRADICTION`, `ERR_AGGREGATOR_ONLY`, `ERR_DATE_DISCREPANCY`. |
| **FR-REF-003** | Refusal Audit Export | The system shall render refused claims in a dedicated "Refusal & Exclusion Log" section of the output. | P0 | Demonstrates rigorous adherence during evaluation. | Shows original claim text, source attempt, refusal code, and reason summary. |

#### 2.6 Three Strategic Presence Gaps (GAP)
| Req ID | Title | Description | Priority | Rationale | Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-GAP-001** | Gap Analysis Engine | The system shall evaluate the prospect's verified footprint against executive presence benchmarks. | P0 | Mandated by brief: "identifies the three biggest gaps in how they currently show up publicly". | Analyzes 3 strategic dimensions: Authority Positioning, Channel Distribution, Narrative Consistency. |
| **FR-GAP-002** | Prioritized Triad Output | The system shall select and rank exactly three highest-impact gaps. | P0 | Strict constraint to avoid overwhelming advisors. | Outputs Gap #1, Gap #2, Gap #3 with Impact Score, Evidence Rationale, and Strategic Recommendation. |

#### 2.7 Human Gate & Editorial Review (HGT)
| Req ID | Title | Description | Priority | Rationale | Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-HGT-001** | Staging Screen | The system shall present an interactive review table of extracted claims before final diagnostic compilation. | P0 | 15 pts Human Gate rubric requirement. | Advisor can view all claims, statuses, evidence quotes, and confidence scores. |
| **FR-HGT-002** | Manual Override Action | The system shall allow an advisor to promote, demote, edit, or reject any claim. | P0 | Human expertise balances algorithmic judgment. | Advisor can change `PARTIALLY_VERIFIED` to `VERIFIED` with mandatory override rationale comment. |
| **FR-HGT-003** | Sign-Off Authorization | The system shall require explicit advisor confirmation before generating the final One-Page Diagnostic. | P0 | Prevents unreviewed machine outputs from reaching clients. | "Approve & Compile Diagnostic" action unlocks final view. |

#### 2.8 Diagnostic Delivery & Export (OUT)
| Req ID | Title | Description | Priority | Rationale | Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-OUT-001** | One-Page Layout Constraint | The system shall format the diagnostic to fit on a single standard executive view/page. | P0 | Mandated by brief: "outputs a one-page diagnostic". | Clean typography, card-based layout, no unnecessary white-space bloat. |
| **FR-OUT-002** | Markdown & PDF Export | The system shall allow exporting the diagnostic as GitHub-flavored Markdown and printable PDF. | P1 | Portability for advisory presentations. | Generates valid Markdown file and clean PDF print stylesheet. |
| **FR-OUT-003** | Audit Traceability Export | The system shall produce a complete JSON audit log linking every claim to its source URLs and verification records. | P0 | Comprehensive proof of fact integrity. | Exportable JSON file containing full execution transcript and telemetry. |
