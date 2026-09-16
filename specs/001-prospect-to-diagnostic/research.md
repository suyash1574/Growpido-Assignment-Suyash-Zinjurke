# Phase 0 Research: Technical Context & Architectural Decisions

**Feature**: `001-prospect-to-diagnostic`  
**Date**: 2026-09-16  
**Status**: Completed  

---

## 1. Research Objectives & Problem Statement
The Growpido Prospect to Diagnostic Engine requires an adversarial, zero-hallucination OSINT architecture that incepts a UAE executive LinkedIn URL, discovers live web records, extracts discrete atomic factual claims, conducts a two-stage double-check primary verification, flags contradictions, enforces deterministic claim refusal, computes exactly three strategic presence gaps, and renders an executive One-Page Diagnostic backed by an interactive Human Gate.

---

## 2. Technology Choices & Concrete Decisions

### Decision 1: LLM Orchestration & Provider Choice
- **Decision**: Primary inference powered by **Groq (Llama 3.3 70B Versatile)** with native JSON mode and strict schema validation; secondary fallback to OpenAI/Gemini if configured.
- **Rationale**: Groq LPU inference provides ultra-low latency (~200–400ms per request), which is critical when extracting claims, running NLI entailment checks, and evaluating contradictions across multiple sources without exceeding the 90-second total pipeline budget.
- **Alternatives Considered**: 
  - Standard OpenAI GPT-4o: High quality but higher cost and 3–5x greater latency per claim check.
  - Local Ollama: Resource-intensive on consumer machines and slower generation speeds.

### Decision 2: Live Web OSINT Search Strategy
- **Decision**: **Live multi-engine discovery** prioritizing Tavily Search API with direct URL crawling and resilient HTTP client failover to DuckDuckGo live HTML parsing.
- **Enforced Clarification Rule**: Zero offline mock data failovers. If live search fails or credentials are missing, raise explicit `ERR_LIVE_SEARCH_FAILED` to guarantee only authentic, real-time public web facts are processed.
- **Rationale**: Complies with user directive: *"we don't need the fix way we need the true info from internet so don't add offline failover."*
- **Alternatives Considered**: Mock data fixtures (explicitly rejected by user).

### Decision 3: Dual-Mode Persistence Architecture (SQLite + PostgreSQL Ready)
- **Decision**: Unified SQL repository pattern with default embedded **SQLite (WAL mode)** for immediate, zero-config local operation, fully compatible with external cloud **PostgreSQL** via connection string toggle (`DATABASE_URL`).
- **Rationale**: Allows instant local running and testing for hackathon evaluators without database infrastructure setup, while preserving instant cloud persistence once the PostgreSQL server is active.
- **Alternatives Considered**: Pure Postgres-only (fails to run if remote database is offline/unreachable).

### Decision 4: Deterministic Double-Check Verification Algorithm
- **Decision**: Two-stage algorithmic gating:
  - **Check 1 (Primary Grounding & Entailment)**: Validates source domain tier against whitelisted registries (Tier 1 Gov/Corporate) and checks NLI semantic entailment ($\ge 0.85$).
  - **Check 2 (Independent Corroboration & Consistency)**: Queries an independent domain to corroborate the assertion and executes date/numerical contradiction detection.
  - **Outcome**: Both pass ➔ `VERIFIED`; Tier 2 only or minor contradiction ➔ `PARTIALLY_VERIFIED`; Tier 3/4 only or primary missing ➔ `UNVERIFIED` (routed to Refusal Engine).
- **Rationale**: Directly satisfies the Track B brief mandate ("verifies every factual claim against a primary source, and checks it twice") and 25-point Fact Integrity rubric.

### Decision 5: Adversarial Refusal Mechanics
- **Decision**: Systematic exclusion of unverified claims using standardized codes (`REF-01` to `REF-05`) with clear, human-readable causal rationales.
- **Rationale**: Satisfies the Track B requirement to showcase *"one claim your system refused to include and why it refused"*.

### Decision 6: Presentation Tier & Human Gate
- **Decision**: **Streamlit** reactive web interface with an interactive Human Gate staging table before diagnostic export.
- **Rationale**: Streamlit enables rapid Python-native stateful UI development, interactive dataframes with status overrides, live citation inspection, and single-click One-Page Diagnostic rendering.
