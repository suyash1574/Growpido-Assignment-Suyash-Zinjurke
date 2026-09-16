# Failure Handling Specification & Operational Runbook
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Document Overview
Real-world OSINT and agentic LLM pipelines encounter frequent point failures: anti-bot rate limits, stale DNS records, hallucinated citation URLs, ambiguous dates, and API timeouts. 

This document defines the **Failure Handling Matrix**, standard recovery flows, fallback behaviors, and operational runbook procedures ensuring the system fails gracefully, transparently, and deterministically.

---

### 2. Operational Failure Handling Matrix

| Failure ID | Failure Mode | Root Cause | Detection Mechanism | Immediate System Recovery Action | Audit Action & User Notification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FL-001** | Search Provider Rate Limit | 429 Too Many Requests from primary search engine (e.g. Tavily). | HTTP Status Code `429` caught in client handler. | Exponential backoff with jitter (1s, 2s, 4s). Auto-failover to secondary provider (DuckDuckGo / SerpAPI). | Log warning in `audit_log`. Display subtle toast: *"Primary search throttled, using secondary provider."* |
| **FL-002** | Target Page Gated / Bot Block | Target news or bio site blocks scraper with Cloudflare / 403 Forbidden. | HTTP Status Code `403` or challenge page detected. | Skip target URL; decrement source authority count; do not crash pipeline. | Mark source as `SOURCE_UNREACHABLE` in evidence table. |
| **FL-003** | LLM Hallucinated Citation URL | Model invents a URL that does not exist in the fetched search evidence set. | Regex check comparing output URL against `available_sources` whitelist. | **Hard Intercept:** If URL was not retrieved during discovery, invalidate citation immediately. | Assign refusal code `REF-01` and alert auditor at Human Gate. |
| **FL-004** | Conflicting Factual Records | Source A states Souq founded in 2005; Source B states 2006. | Temporal/numerical discrepancy detector triggers divergence threshold. | Lock claim status to `PARTIALLY_VERIFIED`. Highlight both conflicting citations side-by-side. | Route claim to Human Gate with prominent warning chip: `CONTRADICTION_FLAGGED`. |
| **FL-005** | LLM Structured Output Parse Error | Model returns non-JSON or malformed schema payload. | Pydantic `ValidationError` raised during schema decoding. | Trigger zero-shot repair prompt (max 2 retries); if still failing, isolate affected claim into `UNVERIFIED`. | Log exception traceback to SQLite audit ledger. |
| **FL-006** | Zero Search Results / Niche Footprint | Prospect has virtually zero public web footprint. | Search query yields 0 indexed results across all vectors. | Graceful degradation: Synthesize diagnostic indicating severe lack of public authority indexing. | Render Gap #1 as: *"Invisible Digital Footprint across UAE commercial registries."* |
| **FL-007** | Network Disconnection / Timeout | OSINT fetcher exceeds 10-second connection timeout. | `httpx.TimeoutException` caught. | Terminate socket connection, mark URL unreachable, continue with remaining sources. | Record timeout event in audit log. |

---

### 3. Step-by-Step Failure Recovery Flows

```
                   [HTTP Request / LLM Call]
                               │
                      ┌────────┴────────┐
                      ▼                 ▼
                  [Success]          [Error]
                      │                 │
                      ▼         ┌───────┴───────────────────────┐
               [Proceed Pipeline]│ 429 Throttle?                 │
                                ├─► Backoff & Switch Provider   │
                                │ 403 Forbidden?                │
                                ├─► Drop URL & Mark Unreachable │
                                │ LLM Schema Mismatch?          │
                                ├─► Retry with JSON Corrector   │
                                │ Hallucinated URL?             │
                                └─► Force Invalidation & Refusal│
```

---

### 4. Operational Runbook & Troubleshooting Guide

#### Issue 1: "The application hangs on Search Execution"
- **Diagnosis:** Primary search API key is invalid, exhausted, or network socket is blocked.
- **Resolution:**
  1. Inspect local `.env` to ensure `TAVILY_API_KEY` is present and valid.
  2. Toggle `USE_FALLBACK_SEARCH=True` in `.env` to route through DuckDuckGo search without API key dependency.
  3. Restart Streamlit server: `streamlit run src/app.py`.

#### Issue 2: "Every claim is being classified as UNVERIFIED"
- **Diagnosis:** The primary source whitelist regex is too restrictive or fetched pages returned empty text bodies.
- **Resolution:**
  1. Inspect `data/evidence_cache/` to see if scraped files contain readable text.
  2. Check `09_DATA_DICTIONARY.md` and `11_VERIFICATION_SPEC.md` to confirm the target domain is recognized under Tier 1.
  3. Use the Human Gate dashboard to review raw evidence snippets and apply manual overrides if necessary.

#### Issue 3: "Streamlit UI displays SQLite database locked"
- **Diagnosis:** Multiple concurrent threads attempting write transactions without connection timeouts.
- **Resolution:**
  1. Ensure SQLite connection strings utilize `timeout=30.0` and WAL mode (`PRAGMA journal_mode=WAL;`).
  2. Re-initialize database: `python -m src.storage.db --init`.
