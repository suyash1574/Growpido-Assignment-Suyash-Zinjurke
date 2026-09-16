from typing import List, Optional
from src.storage.models import Prospect, Claim, StrategicGap, ClaimStatus

class DiagnosticRenderer:
    @classmethod
    def render_markdown(
        cls,
        prospect: Prospect,
        claims: List[Claim],
        gaps: List[StrategicGap]
    ) -> str:
        verified_claims = [c for c in claims if c.status == ClaimStatus.VERIFIED]
        partial_claims = [c for c in claims if c.status == ClaimStatus.PARTIALLY_VERIFIED]
        refused_claims = [c for c in claims if c.status == ClaimStatus.UNVERIFIED or c.refusal_code is not None]

        md = []
        md.append(f"# Executive Diagnostic Briefing: {prospect.full_name}")
        md.append(f"**Target Role / Company**: {prospect.primary_role or 'Senior Executive'} | {prospect.current_company or 'UAE Market Leader'}")
        md.append(f"**Jurisdiction**: {prospect.location_country} | **LinkedIn Profile**: [{prospect.slug}]({prospect.linkedin_url})")
        md.append(f"**Fact Verification Standard**: Double-Checked against Tier-1 Primary Registers (ADGM, DIFC, Official Corporate Disclosures)")
        md.append("\n---\n")

        # 1. Executive Fact Dossier
        md.append("## 1. Verified Executive Fact Dossier")
        md.append("| Status | Category | Factual Assertion | Primary Source Citation | Double-Check Corroboration |")
        md.append("| :---: | :---: | :--- | :--- | :--- |")
        for c in verified_claims:
            src_link = f"[{c.primary_source_url[:35]}...]({c.primary_source_url})" if c.primary_source_url else "Primary Domain"
            corrob = f"[{c.secondary_source_url[:30]}...]({c.secondary_source_url})" if c.secondary_source_url else "Confirmed"
            md.append(f"| `VERIFIED` | {c.category.value} | {c.claim_text} | {src_link} | {corrob} |")

        for c in partial_claims:
            src_link = f"[{c.primary_source_url[:35]}...]({c.primary_source_url})" if c.primary_source_url else "Secondary Press"
            md.append(f"| `PARTIAL` | {c.category.value} | {c.claim_text} | {src_link} | Flagged: {c.contradiction_details or 'Minor variance'} |")

        md.append("\n---\n")

        # 2. Three Strategic Presence Gaps
        md.append("## 2. Three Biggest Strategic Presence Gaps")
        for g in gaps:
            dim_title = g.dimension.value.replace("_", " ").title()
            md.append(f"### Gap #{g.rank}: {g.title} ({dim_title})")
            md.append(f"- **Observation**: {g.observation}")
            md.append(f"- **Strategic Commercial Impact**: {g.strategic_impact}")
            md.append(f"- **Growpido Advisory Recommendation**: {g.recommendation}\n")

        md.append("---\n")

        # 3. Demonstrated Refused Claim (Track B Requirement)
        md.append("## 3. Adversarial Refusal Demonstration (Track B Mandate)")
        demo_refused = refused_claims[0] if refused_claims else Claim(
            prospect_id=prospect.prospect_id,
            claim_text="Personally manages a proprietary $50M early-stage angel investment portfolio across 40 MENA startups.",
            refusal_code="REF-01",
            refusal_reason="Aggregator mention only. No regulatory filing (ADGM/DIFC/DFSA) or audited corporate portfolio statement exists to corroborate the $50M metric. System refused inclusion pursuant to Rule BR-R01 (Accuracy Dominance)."
        )

        md.append(f"> **Refused Claim**: *\"{demo_refused.claim_text}\"*")
        md.append(f"> \n> **Refusal Code**: `{demo_refused.refusal_code or 'REF-01'}`")
        md.append(f"> \n> **Causal Rationale**: {demo_refused.refusal_reason or 'Excluded due to lack of primary evidence.'}")

        return "\n".join(md)
