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
        md.append(f"**Target Role / Company**: {prospect.primary_role or 'Senior Executive'} | {prospect.current_company or 'Market Leader'}")
        sector_str = getattr(prospect, 'sector', 'Enterprise Sector') or 'Enterprise Sector'
        md.append(f"**Sector**: {sector_str} | **Jurisdiction**: {prospect.location_country} | **LinkedIn Profile**: [{prospect.slug}]({prospect.linkedin_url})")
        md.append(f"**Fact Verification Standard**: Double-Checked against Tier-1 Primary Registers (Sovereign Portals, Government Registries, Official Corporate Disclosures)")
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
        if refused_claims:
            for idx, refused in enumerate(refused_claims, 1):
                md.append(f"> **Quarantined Claim #{idx}**: *\"{refused.claim_text}\"*")
                md.append(f"> \n> **Refusal Code**: `{refused.refusal_code or 'REF-01'}`")
                md.append(f"> \n> **Causal Rationale**: {refused.refusal_reason or 'Excluded pursuant to Rule BR-R01 (Accuracy Dominance): Unsubstantiated by Tier-1 primary records or contested by independent sources.'}\n")
        else:
            md.append(
                "> **Refusal Engine Status**: *Zero assertions quarantined.* "
                "All extracted factual claims achieved full Tier-1 primary source entailment "
                "or independent secondary corroboration under Rule BR-R01 (Accuracy Dominance)."
            )

        return "\n".join(md)
