# Demo & Loom Presentation Script (5-Minute Walkthrough)
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Presentation Strategy & Rubric Alignment
The brief mandates: *"Show us: the diagnostic for the person you picked, plus one claim your system refused to include and why it refused."*
This script ensures our 5-minute video delivers maximum punch, demonstrating engineering rigor, fact integrity, algorithmic refusal, and output quality without drowning in code syntax.

**Time Budget:** Exactly 5:00 Minutes.

---

### 2. Shot-by-Shot Presentation Script

#### [0:00 – 0:30] The High-Stakes Problem & Core Principle
- **Visual:** Split screen: Growpido Logo + High-profile UAE Executive (Ronaldo Mouchawar, VP Amazon MENA / Co-founder Souq.com).
- **Speaker:**
  > *"Welcome to our presentation of Growpido Track B: Prospect to Diagnostic. When Growpido pitches high-caliber founders and fund managers in Dubai or Abu Dhabi, credibility is everything. A single hallucinated metric or fake credential ruins the meeting.*
  > *That’s why our engine is built on one inviolable law: **Accuracy takes absolute precedence over completeness.** If a claim cannot be proven against authoritative primary evidence, our engine refuses it."*

---

#### [0:30 – 1:00] Architecture & The Double-Check Protocol
- **Visual:** Display Architecture Diagram from `06_HLD.md`.
- **Speaker:**
  > *"Instead of generic RAG, we built an Adversarial Multi-Agent Pipeline. Our Discovery Agent gathers public OSINT across four strict source tiers—prioritizing Tier-1 government registers and corporate filings.*
  > *Our Claim Auditor isolates atomic claims. Then our Verification Engine checks every claim **twice**: Check 1 validates primary authority and semantic entailment; Check 2 cross-examines independent sources to catch contradictions. If both don't pass, it's refused."*

---

#### [1:00 – 2:00] Live Execution: Ingestion to Discovery
- **Visual:** Screen recording of Streamlit Web Application.
- **Action:**
  1. Paste target LinkedIn URL: `https://www.linkedin.com/in/ronaldo-mouchawar-souq`.
  2. Click **"Execute Intelligence Pipeline"**.
  3. Live progress indicators show: Target Ingestion ➔ OSINT Search ➔ Claim Audit ➔ Double-Check Verification.
- **Speaker:**
  > *"Let’s run the engine live for Ronaldo Mouchawar, one of the most prominent tech leaders in the UAE. Notice we don't scrape LinkedIn private data or require logins; we ingest the public identifier and immediately orchestrate multi-vector searches across UAE registries, corporate press archives, and reputable financial news.*
  > *In under 30 seconds, the engine has extracted 8 distinct claims, fetched primary evidence, and computed verification statuses."*

---

#### [2:00 – 3:00] The Human Gate & Evidence Inspection
- **Visual:** Human Gate review dashboard in the UI.
- **Action:**
  1. Hover over `VERIFIED` claim: *"Co-founded Souq.com in 2005"*. Click the source chip showing Tier-1 corporate domain and ADGM corroboration.
  2. Show a `PARTIALLY_VERIFIED` claim with slight date discrepancy.
  3. Show the Human Override button with audit logging.
- **Speaker:**
  > *"Here is our Human Gate—a required editorial checkpoint before any diagnostic is compiled. Advisors can inspect every evidence snippet, check the primary URL, and view confidence scores.*
  > *Every claim is strictly classified: Verified, Partially Verified, or Unverified. Advisors can manually adjust ratings with an audit comment, ensuring human accountability."*

---

#### [3:00 – 4:00] The Refused Claim: Adversarial Integrity
- **Visual:** Zoom in on the dedicated **"Refusal & Exclusion Ledger"** on screen.
- **Action:** Expand the refused claim card: *"Manages a $50M personal angel investment portfolio across 40 startups."*
- **Speaker:**
  > *"Now to the heart of the brief: the claim our system refused to include and why.*
  > *During discovery, secondary bio aggregators and blog posts claimed that Ronaldo manages a '$50M personal angel portfolio'. A generic LLM would happily parrot this fluff.*
  > *Our system flagged it under Refusal Code `REF-01: NO_PRIMARY_EVIDENCE`. Our Verification Engine searched ADGM, DIFC, and corporate financial disclosures—zero audited filings corroborate this $50M figure. Because accuracy dominates completeness, our engine refused this claim, quarantined it from the diagnostic, and generated an explicit causal rationale."*

---

#### [4:00 – 4:30] The One-Page Diagnostic & The 3 Gaps
- **Visual:** Final One-Page Executive Diagnostic rendered in clean, printable UI.
- **Action:** Highlight the 3 Strategic Presence Gaps:
  1. *Authority Under-Indexing:* Legendary $580M exit track record is under-documented on his direct personal domain.
  2. *Channel Diversification Deficit:* Heavy reliance on passive LinkedIn; absent from Tier-1 executive podcasts and global fireside keynotes.
  3. *Narrative Fragmentation:* Ambiguity between Amazon VP corporate duties and independent angel investing.
- **Speaker:**
  > *"Here is the final output: an executive-ready, scannable One-Page Diagnostic. It features verified facts, verifiable citations, and the three biggest gaps in how Ronaldo shows up publicly—providing Growpido advisors with an immediate, high-value advisory pitch."*

---

#### [4:30 – 5:00] Honest Paragraph & Engineering Transparency
- **Visual:** Display `18_LIMITATIONS.md` / Slide showing "Engineering Reality & Limitations".
- **Speaker:**
  > *"To conclude with complete transparency: what broke, and what would we improve?*
  > *First, live web search providers hit aggressive rate limits on certain news portals, requiring our fallback engine. Second, free-zone registries in the UAE occasionally use image-based PDF certificates that require OCR pre-processing. In our next iteration, we will implement native Arabic OCR and automated DIFC API connectors.*
  > *From business requirements to unit tests, our engine proves that high-stakes AI can be deterministic, audit-backed, and honest. Thank you!"*
