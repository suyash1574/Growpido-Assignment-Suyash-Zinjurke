# Security, Privacy & Ethical OSINT Specification
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Document Purpose & Guiding Principles
The Growpido Engine processes public information regarding high-profile executives, founders, CEOs, and fund managers in the United Arab Emirates (UAE). Although OSINT operates in the public domain, strict security, privacy boundaries, and ethical constraints must be enforced to prevent illegal data scraping, privacy violations, or defamatory publications.

**Core Data Principle:**
> **Public source $\neq$ Automatically trustworthy or legally unconstrained.** The system must treat all retrieved data with rigorous provenance tracking, zero credential abuse, and strict confidentiality protections.

---

### 2. Explicit System Boundaries & Prohibitions

#### 2.1 Credential & Authentication Boundaries
- **No Authenticated Scraping:** The system shall **never** require, store, or accept LinkedIn user login credentials, session cookies (`li_at`), or OAuth tokens.
- **No CAPTCHA Bypassing:** The system is strictly forbidden from utilizing CAPTCHA-solving farms or headless browser session hijacking to scrape restricted pages.
- **No Private Network Infiltration:** Any resource behind a paywall or login prompt is categorized as `UNREACHABLE_PRIVATE` and immediately bypassed.

#### 2.2 Prospect Interaction Boundaries
- **Zero Automated Outreach:** The system shall **never** send automated InMail, connection requests, emails, SMS messages, or pings to the prospect.
- **Zero Third-Party Inquiries:** The system shall **never** contact colleagues, investors, or references during the discovery phase.
- **Passive Intelligence Only:** The engine is 100% passive; it observes existing public web indices without disturbing the target entity.

#### 2.3 Sensitive Personal Data Boundaries
- **No PII Collection:** Home addresses, personal phone numbers, family member names, religious affiliations, health data, or political opinions are strictly filtered out by redaction pre-processors.
- **Financial Inference Prohibitions:** The system shall never speculate or infer personal net worth. Only audited, publicly registered corporate metrics (e.g., published fund AUM, registered capital) may be verified.

---

### 3. Compliance Framework & Legal Alignment

#### 3.1 UAE Federal Decree-Law No. 45 of 2021 on Personal Data Protection (PDPL)
- **Lawful Basis:** Processing is conducted for legitimate business advisory preparation utilizing exclusively public-domain corporate and commercial information.
- **Data Minimization:** Only factual data directly relevant to executive corporate presence, leadership, and public commercial standing is extracted.
- **Right to Rectification:** The Human Gate interface allows advisors to manually rectify, edit, or purge erroneous public data points before report generation.

#### 3.2 Platform Terms of Service (LinkedIn & Search Providers)
- Ingests only publicly viewable search snippets and openly indexed web records.
- Complies with `robots.txt` directives and respects HTTP 429 rate limits.

---

### 4. Technical Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      INGEST FILTER                          │
│   • Sanitizes input URL string (prevents SSRF / XSS)        │
│   • Strips suspicious tracking parameters & tokens          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   PII & PRIVACY REDACTOR                    │
│   • Regex filters for phone numbers, personal emails, SSNs  │
│   • Drops residential address tokens from extracted text    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   SECURE LOCAL PERSISTENCE                  │
│   • SQLite database stored locally in memory or local disk  │
│   • No third-party data telemetry or unauthorized syncing   │
│   • API keys loaded via environment variables (.env)        │
└─────────────────────────────────────────────────────────────┘
```

#### 4.1 Injection & SSRF Protection
- **Input Sanitization:** LinkedIn URLs are validated against strict whitelisted regex patterns before initiating any HTTP socket connection.
- **Network Boundaries:** Internal network IP ranges (`127.0.0.1`, `10.0.0.0/8`, `192.168.0.0/16`, `169.254.169.254`) are blocked from the web fetcher client to eliminate Server-Side Request Forgery (SSRF) vulnerabilities.

#### 4.2 API Key & Secret Management
- Zero hardcoded API keys. All LLM and search credentials (`TAVILY_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`) must be loaded from local environment files (`.env`) excluded via `.gitignore`.
