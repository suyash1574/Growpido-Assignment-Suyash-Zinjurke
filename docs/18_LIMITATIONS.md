# Known Limitations & Honest Engineering Paragraph
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Document Purpose & Philosophy
The Growpido rubric dedicates **10 points to an "Honest Paragraph"** (assessing self-awareness, technical honesty, disclosure of what broke during development, and concrete paths for iteration). 

Engineering high-stakes AI systems requires acknowledging the messy reality of public web indices, anti-bot mechanisms, unstructured natural language ambiguities, and rate-limited third-party APIs. We reject "demo theater" and present an honest post-mortem of our system's current limitations.

---

### 2. The Honest Paragraph (Submission Excerpt)

> *"During testing of the Growpido Prospect to Diagnostic Engine against real-world UAE executive footprints, our adversarial verification layer succeeded in preventing hallucinated corporate metrics, but exposed three acute operational bottlenecks: First, regional search APIs frequently hit 429 rate limits when querying multiple UAE government registers in rapid succession, necessitating our graceful fallback to secondary search providers. Second, several authoritative corporate filings and gazette announcements in the UAE are published as non-indexed, image-only PDFs or Arabic-language trade registry scans, which our current English-centric text sanitizer cannot parse without dedicated OCR pipelines; consequently, certain legitimate executive credentials were conservatively downgraded to `PARTIALLY_VERIFIED` or refused under `REF-01` rather than falsely confirmed. Third, disambiguating executives with common names across the Gulf region required strict multi-token search strings, which slightly increased pipeline latency to ~75 seconds. Our next engineering iteration will introduce native Arabic OCR pre-processing, direct DIFC/ADGM public registry API integrations, and async query batching to eliminate these friction points."*

---

### 3. Detailed Breakdown of Real Limitations & Technical Debt

#### 3.1 Unindexed & Image-Based UAE Public Registries
- **The Reality:** While ADGM and DIFC provide public company registers, detailed commercial trade licenses issued by mainland economic departments (e.g. Dubai Economy & Tourism - DED) are frequently rendered behind session-based portals or returned as scanned Arabic PDFs.
- **System Impact:** The engine cannot deterministically verify mainland trade licenses without an OCR and translation module.
- **Conservative Guardrail:** Adhering to Rule BR-R01 (*Accuracy over Completeness*), the engine refuses to guess, downgrading uncorroborated mainland claims to `PARTIALLY_VERIFIED` or `UNVERIFIED`.

#### 3.2 Dynamic Search Engine Throttling
- **The Reality:** Aggressive OSINT queries against corporate domains often trigger HTTP 403 / 429 blocks from Cloudflare-protected media portals (e.g. Arabian Business, Bloomberg).
- **System Impact:** Intermittent failures when fetching full-text page payloads.
- **Mitigation Implemented:** Resilient fallback from Tavily to DuckDuckGo search snippets, caching raw HTML to SQLite, and exponential backoff retry routines.

#### 3.3 Temporal Ambiguity in Secondary Reporting
- **The Reality:** Journalistic press often loosely reports executive tenure dates (e.g. reporting a 2017 Amazon acquisition as the "start date" of an executive's role, whereas the integration was formalized in 2018).
- **System Impact:** Triggers false-positive contradiction flags in Check 2.
- **Mitigation Implemented:** Automated routing of temporal discrepancies to the Human Gate for advisor sign-off with clear side-by-side snippet comparisons.

---

### 4. Roadmap & Future Iterations

| Phase | Enhancement Title | Technical Implementation | Target Milestone |
| :--- | :--- | :--- | :--- |
| **v1.1** | Arabic OCR & Legal NLP | Integration of Tesseract / EasyOCR and Arabic NER models for DED/MoE trade register scans. | Q4 2026 |
| **v1.2** | Direct Registry Connectors | Formal B2B API integrations with ADGM & DIFC registry endpoints for instant corporate verification. | Q1 2027 |
| **v1.3** | Automated PDF Report Engine | Headless Chrome / WeasyPrint pipeline for generating branded executive PDF pitch decks. | Q1 2027 |
| **v1.4** | Continuous Monitoring Agent | Cron-based background monitor tracking public footprint drift and newly filed claims. | Q2 2027 |
