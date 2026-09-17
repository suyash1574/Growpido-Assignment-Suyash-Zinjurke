# Research & Architecture Decisions: Name-Based Search & Global Authority Verification

**Feature**: `002-name-search-verification`  
**Date**: 2026-09-17  
**Status**: Completed

---

## 1. Name-Based Prospect Search & Candidate Disambiguation

### Problem
Advisors previously had to leave Growpido, manually search Google or LinkedIn, copy the exact public profile URL (`https://www.linkedin.com/in/{slug}`), and paste it into the UI. This created workflow friction and was prone to copy-paste errors.

### Decision
Implement a two-step ingestion workflow:
1. **Search Phase (`POST /api/search/candidates`)**:
   - Input: `name: str`, `context_keywords: Optional[str] = None` (e.g. company, role, country).
   - Search Query: `site:linkedin.com/in/ "{name}" {context_keywords}` executed via OSINT discovery engine (`TavilyClient` / web search).
   - Parsing: Extracts up to 5 discrete `CandidateMatch` entities with:
     - `full_name`: Candidate's name extracted from title/headline
     - `headline`: Current title / summary (e.g. "Prime Minister of India", "VP at Amazon MENA")
     - `company`: Associated organization
     - `location`: Geographic location if available
     - `linkedin_url`: Canonical public LinkedIn URL
     - `snippet`: Public preview text
2. **Sovereign Candidate Confirmation Gate**:
   - UI displays candidate cards with avatar badges, current title chips, and source links.
   - Advisor inspects the candidates and clicks **"Confirm & Research Target"**.
   - The confirmed target's profile URL and inferred jurisdiction/sector are passed to the deep intelligence pipeline.
   - *Direct URL fallback*: Advisors who already have the exact LinkedIn URL can switch tabs or paste it directly.

### Alternatives Considered
- *Automatic Best-Match Execution*: Executing the pipeline directly on the top search result without human confirmation.
  - *Rejected*: Violates **Principle IV (Sovereign Human-in-the-Loop Gate)**. Common names or ambiguous queries could lead the system to audit the wrong individual, wasting API quotas and polluting database records.
- *LinkedIn Scraping*: Direct automated scraping of LinkedIn login sessions.
  - *Rejected*: Violates **Principle V (Strict Public OSINT Boundaries & Zero-Credential Policy)** and terms of service.

---

## 2. Global Tier-1 Primary Authority Classification & Verification Accuracy

### Problem
When testing public figures such as "Narendra Modi", substantiated public facts (e.g., *"Narendra Modi has served as the Prime Minister of India since 26 May 2014"*) were marked `UNVERIFIED` and quarantined under `REF-01` with `Check 1: FAILED` and `Check 2: FAILED`.

### Root Cause Analysis
1. `src/discovery/tier_classifier.py` had a narrow regional whitelist focusing strictly on UAE government domains (`.gov.ae`, `difc.ae`, `adgm.com`) and specific Middle East business press.
2. Deterministic rules failed to classify sovereign national government domains (`.gov`, `.gov.*` including `.gov.in`, `pmindia.gov.in`, `india.gov.in`, `sansad.in`, `.nic.in`, `.gov.uk`, `.gc.ca`, `.gov.au`, etc.) as `TIER_1_PRIMARY`. Instead, they fell through to default Tier-3 (Aggregator) or Tier-4 (Social).
3. In `src/verification/double_checker.py`, `evaluate_check1_primary` strictly filters `sources` for `s.source_tier == SourceTier.TIER_1_PRIMARY`. Because no source was recognized as Tier-1, Check 1 immediately returned `passed: False`, automatically triggering `REF-01` refusal.
4. OSINT search queries in `src/orchestrator.py` contained hardcoded UAE regional keywords (`"UAE executive"`, `"Dubai"`), skewing discovery away from sovereign national registers when auditing non-UAE figures.

### Decision
1. **Universal Sovereign Government Tier-1 Regex**:
   - Expand `TierClassifier.classify_tier(domain)` with regex patterns recognizing:
     - All sovereign government TLDs and second-level domains: `\.gov(\.[a-z]{2})?$`, `\.nic\.in$`, `\.parliament\.[a-z]{2,}$`, `\.gc\.ca$`, `\.mil(\.[a-z]{2})?$`
     - Official state registries, gazettes, ministries, and central banks (e.g. `pmindia.gov.in`, `whitehouse.gov`, `gov.uk`, `sec.gov`, `mca.gov.in`, `companieshouse.gov.uk`)
     - Accredited universities globally: `\.edu(\.[a-z]{2})?$`, `\.ac\.[a-z]{2}$`
     - Verified corporate press/investor relations domains (e.g., `press.aboutamazon.com`, `investor.*`, official root corporate domains matching the executive's verified company).
2. **Context-Aware Corroboration Search**:
   - Dynamic query formulation: construct discovery queries using the candidate's verified name, primary organization/role, and extracted proposition keywords without hardcoding "UAE".
   - Double-check entailment: prompt LLM to verify semantic entailment against discovered official records with lenient temporal/date formatting normalization.

### Alternatives Considered
- *Lowering Check 1 Threshold to accept Tier-2 (Financial Press) as Primary*:
  - *Rejected*: Violates **Principle II (Two-Stage Double-Check Primary Verification)**. Primary authority must remain anchored to official registries, gazettes, or verified corporate sources. Expanding Tier-1 recognition globally preserves constitutional rigor while fixing false negatives.

---

## 3. Dynamic Geographic & Sector Adaptation for Diagnostics

### Problem
The Executive Diagnostic header displayed `Founder & Executive | UAE Commercial Sector | UAE` and synthesized strategic gaps referencing `UAE market`, `Bloomberg UAE`, and `UAE-focused business podcasts` regardless of whether the prospect was based in India, the US, or Europe.

### Decision
1. **Dynamic Prospect Profile**:
   - Extract candidate location, primary role, and sector during candidate confirmation or OSINT ingest.
   - Store detected `location_country` (e.g. "India", "United Arab Emirates", "United States") and `sector` (e.g. "Public Governance & State Leadership", "Enterprise Technology & Cloud", "Retail & E-Commerce").
2. **Context-Aware Gap Synthesis**:
   - Pass the verified `location_country` and `sector` to `GapSynthesizer.synthesize_gaps(...)`.
   - The LLM prompt explicitly incorporates the prospect's real geography and industry sphere, preventing regional hallucinations in recommendations.

---

## 4. Dual-Engine LLM Reliability

### Decision
Maintain the newly established **Groq + NVIDIA Nemotron Dual-Engine** architecture (`src/llm_client.py`):
- Primary: Groq with conservative token limits (`max_tokens=300-800`) to prevent OTPM 429 rate-limit errors.
- Fallback: NVIDIA Integrate API (`nvidia/nemotron-3.5-lightning-30b-a3b` with `enable_thinking=False`, ~1.1s latency) on any Groq throttling or connection failure.
