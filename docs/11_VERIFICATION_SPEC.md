# Verification Specification & Refusal Logic
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. Document Overview
The Verification Specification represents the core operational engine of Growpido Track B. Fact integrity accounts for 25 points of the rubric, and failure handling/refusal mechanics account for an additional 10 points. 

This document codifies:
1. The Authoritative Source Hierarchy (Tiers 1–4).
2. The Double-Check Verification Protocol.
3. Contradiction and Divergence Detection Algorithms.
4. The Refusal Mechanism and Taxonomy of Rejection Codes.

---

### 2. Authoritative Source Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                 TIER 1: PRIMARY / REGISTRY                  │
│  • Gov & Free-Zone Registries: ADGM, DIFC, DFSA, UAE MoE    │
│  • Official Corporate Domains (AboutUs, Press Releases)     │
│  • Regulatory Filings (SEC 10-K, Prospectuses, DFM, ADX)    │
│  • Accredited University Registries & Alumni Portals        │
│  ===> QUALIFIES FOR IMMEDIATE VERIFICATION ANCHOR           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 TIER 2: REPUTABLE SECONDARY                 │
│  • Financial Press: Bloomberg, Reuters, Financial Times     │
│  • Established Regional Media: Gulf News, The National,     │
│    Arabian Business, Forbes Middle East                     │
│  ===> CORROBORATION ONLY; CANNOT OVERRULE TIER 1            │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 TIER 3: AGGREGATORS & DATABASES             │
│  • Wikipedia, Crunchbase mirrors, PitchBook public blurb    │
│  • Auto-scraped bio portals, RocketReach, ZoomInfo          │
│  ===> DISCOVERY QUERIES ONLY; ZERO VERIFICATION WEIGHT      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 TIER 4: UNVERIFIED & SOCIAL                 │
│  • Medium blogs, Twitter/X posts, Reddit, Reddit AMA, Quora │
│  • Personal promotional posts without corroborating links   │
│  ===> STRICTLY PROHIBITED FROM VERIFICATION PIPELINE        │
└─────────────────────────────────────────────────────────────┘
```

---

### 3. Double-Check Verification Protocol

To satisfy the brief mandate — *"verifies every factual claim against a primary source, and checks it twice"* — every candidate claim must pass through two independent algorithmic gates.

```
       [Candidate Claim]
               │
               ▼
      [CHECK 1: Primary Authority]
      • Is source URL in Tier 1 domain list?
      • Does retrieved snippet semantically entail claim?
               │
         ┌─────┴─────┐
         ▼           ▼
       [PASS]      [FAIL] ──► Status: UNVERIFIED ──► Send to Refusal Log
         │
         ▼
      [CHECK 2: Corroboration & Consistency]
      • Search for independent corroborating source.
      • Execute Contradiction Detection across all snippets.
         │
    ┌────┴─────────────────────────────┐
    ▼                                  ▼
[Both Pass & No Contradiction]   [Contradiction Detected OR 
    │                             Single Secondary Source]
    ▼                                  │
Status: VERIFIED                       ▼
                               Status: PARTIALLY_VERIFIED
```

#### 3.1 Check 1 Specification: Primary Authority Check
- **Domain Whitelist Validation:** URL host is checked against known government, regulatory, or corporate whitelist rules.
- **Semantic Entailment Evaluation:** NLI (Natural Language Inference) score:
  $$\text{Entailment}(P, H) \ge 0.85$$
  where $P$ is the scraped evidence text and $H$ is the atomic claim proposition.
- If $\text{Entailment}(P, H) < 0.85$, Check 1 fails.

#### 3.2 Check 2 Specification: Corroboration & Consistency Check
- **Domain Independence:** Corroborating source domain $D_2 \neq D_1$.
- **Temporal Consistency Check:** Verification of dates ($Y_{\text{start}}$, $Y_{\text{end}}$) across sources.
- **Metric Range Check:** Numerical claims (AUM, valuation, funding) must match within an exact margin of error ($0\%$ for discrete counts; $\pm 5\%$ for currency conversion discrepancies).

---

### 4. Contradiction Detection Algorithm
When multiple sources report on the same entity or event, divergences frequently occur.
- **Type A: Temporal Divergence:** Source A states company founded in 2005; Source B states 2006.
  - *Action:* Lock status to `PARTIALLY_VERIFIED`. Flag date divergence in audit record.
- **Type B: Role Divergence:** Source A states "Co-founder & CEO"; Source B states "Advisor / Non-Executive Director".
  - *Action:* Require Human Gate intervention.
- **Type C: Metric Divergence:** Source A states "$500M fund"; Source B states "$250M committed".
  - *Action:* Refuse highest ungrounded metric; qualify claim with lower verified figure or route to refusal.

---

### 5. Adversarial Refusal Mechanics & Taxonomy

The Growpido Engine enforces an uncompromising refusal policy: **Any claim failing verification is explicitly quarantined and logged with a standardized refusal code.**

#### Refusal Reason Code Reference:
| Code | Reason Title | Operational Trigger |
| :--- | :--- | :--- |
| **REF-01** | `NO_PRIMARY_EVIDENCE` | Claim appears only on Tier-3 aggregators or blogs; no Tier-1 corporate or government record exists. |
| **REF-02** | `UNRESOLVED_CONTRADICTION` | Authoritative sources contain irreconcilable factual discrepancies (e.g. conflicting dates or titles). |
| **REF-03** | `PR_PUFFERY_UNQUANTIFIED` | Subjective marketing claim ("leading Middle East innovator", "visionary") lacking independent institutional audit. |
| **REF-04** | `CORROBORATION_FAILURE` | Claim passed single primary check but second independent corroboration attempt failed or was unreachable. |
| **REF-05** | `STALE_OUTDATED_RECORD` | Record predates 5+ years and is superseded by newer regulatory dissolution filings. |

---

### 6. Golden Exemplar: Refusal Demonstration for Track B
The brief explicitly demands: *"Show us: the diagnostic for the person you picked, plus one claim your system refused to include and why it refused."*

#### System Refusal Record:
- **Prospect:** Ronaldo Mouchawar (VP Amazon MENA, Co-Founder Souq.com).
- **Extracted Claim:**
  > *"Personally manages a proprietary tech venture portfolio exceeding $50,000,000 across 40 early-stage MENA startups."*
- **Discovered Secondary Context:**
  Mentioned in third-party aggregator bio portals and blog event profiles (e.g., event speaker blurbs).
- **Verification Audit Execution:**
  1. *Check 1 (Primary Source Search):* Searched ADGM, DIFC, DFSA public registers and Amazon corporate disclosures for registered venture vehicles under candidate name. **Result: 0 primary regulatory filings located.**
  2. *Check 2 (Corroboration Search):* Searched regional financial press (Bloomberg, Reuters, The National). Found interviews referencing angel investments, but zero audited fund statements or portfolio valuation filings.
- **Refusal Code:** `REF-01: NO_PRIMARY_EVIDENCE`
- **Official Refusal Reason Output:**
  > *"Refused pursuant to Rule BR-R01 (Accuracy Dominance). While third-party speaker bios cite a $50M personal angel portfolio, no regulatory registry (ADGM/DIFC/DFSA), verified corporate balance sheet, or audited portfolio statement corroborates the metric. To prevent ungrounded financial assertions, the claim is excluded from the final diagnostic and logged in the refusal ledger."*
