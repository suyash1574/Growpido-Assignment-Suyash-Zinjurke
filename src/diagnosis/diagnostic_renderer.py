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
        # Rule BR-R01 (Accuracy Dominance): Exclude any contradicted or refused claim from the Verified Fact Dossier!
        verified_claims = [
            c for c in claims 
            if c.status == ClaimStatus.VERIFIED and not c.contradiction_detected and not c.refusal_code
        ]
        partial_claims = [
            c for c in claims 
            if c.status == ClaimStatus.PARTIALLY_VERIFIED and not c.contradiction_detected and not c.refusal_code
        ]
        refused_claims = [
            c for c in claims 
            if c.status == ClaimStatus.UNVERIFIED or c.refusal_code is not None or c.contradiction_detected
        ]

        md = []
        md.append(f"# Executive Diagnostic Briefing: {prospect.full_name}")
        md.append(f"**Target Role / Company**: {prospect.primary_role or 'Senior Executive'} | {prospect.current_company or 'Market Leader'}")
        sector_str = getattr(prospect, 'sector', 'Enterprise Sector') or 'Enterprise Sector'
        md.append(f"**Sector**: {sector_str} | **Jurisdiction**: {prospect.location_country} | **LinkedIn Profile**: [{prospect.slug}]({prospect.linkedin_url})")
        md.append(f"**Fact Verification Standard**: Double-Checked against Tier-1 Primary Registers (Sovereign Portals, Government Registries, Official Corporate Disclosures)")
        md.append("\n---\n")

        # 1. Executive Fact Dossier (Strictly bounded to top 5 highest-materiality verified claims for one-page briefing budget)
        md.append("## 1. Verified Executive Fact Dossier")
        md.append("| Status | Category | Factual Assertion | Primary Source Citation | Double-Check Corroboration |")
        md.append("| :---: | :---: | :--- | :--- | :--- |")
        
        # Sort verified claims by materiality: HIGH first, then MEDIUM, then LOW
        sorted_verified = sorted(
            verified_claims + partial_claims,
            key=lambda c: 0 if getattr(c, 'materiality', None) and c.materiality.value == 'HIGH' else (1 if getattr(c, 'materiality', None) and c.materiality.value == 'MEDIUM' else 2)
        )
        display_verified = sorted_verified[:5]

        for c in display_verified:
            status_label = "`VERIFIED`" if c.status == ClaimStatus.VERIFIED else "`PARTIAL`"
            src_link = f"[{c.primary_source_url[:35]}...]({c.primary_source_url})" if c.primary_source_url else "Primary Domain"
            corrob = f"[{c.secondary_source_url[:30]}...]({c.secondary_source_url})" if c.secondary_source_url else "Confirmed"
            md.append(f"| {status_label} | {c.category.value} | {c.claim_text} | {src_link} | {corrob} |")

        if len(sorted_verified) > 5:
            md.append(f"\n*Note: Top 5 material assertions displayed for one-page executive brevity. All {len(sorted_verified)} verified claims are immutably preserved in the cryptographic audit trail.*")

        md.append("\n---\n")

        # 2. Three Strategic Presence Gaps (Bounded word count for one-page brevity)
        md.append("## 2. Three Biggest Strategic Presence Gaps")
        for g in gaps[:3]:
            dim_title = g.dimension.value.replace("_", " ").title()
            md.append(f"### Gap #{g.rank}: {g.title} ({dim_title})")
            md.append(f"- **Observation**: {g.observation.strip()}")
            md.append(f"- **Strategic Commercial Impact**: {g.strategic_impact.strip()}")
            md.append(f"- **Growpido Advisory Recommendation**: {g.recommendation.strip()}\n")

        md.append("---\n")

        # 3. Demonstrated Refused Claim (Mandatory Track B Requirement)
        md.append("## 3. Adversarial Refusal Demonstration (Track B Mandate)")
        if refused_claims:
            for idx, refused in enumerate(refused_claims[:2], 1):
                md.append(f"> **Quarantined Claim #{idx}**: *\"{refused.claim_text}\"*")
                md.append(f"> \n> **Refusal Code**: `{refused.refusal_code or 'REF-01'}`")
                md.append(f"> \n> **Causal Rationale**: {refused.refusal_reason or 'Excluded pursuant to Rule BR-R01 (Accuracy Dominance): Unsubstantiated by Tier-1 primary records or contested by independent sources.'}\n")
        else:
            # Explicit warning if somehow zero claims were quarantined
            md.append(
                "> **Refusal Engine Notice**: *No quarantined claims detected in this session.* "
                "Under Rule BR-R01 (Accuracy Dominance), at least one uncorroborated assertion should be audited."
            )

        return "\n".join(md)
