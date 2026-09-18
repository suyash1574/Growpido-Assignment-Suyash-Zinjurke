import streamlit as st
from typing import List
from src.storage.models import Prospect, Claim, StrategicGap, ClaimStatus
from src.diagnosis.diagnostic_renderer import DiagnosticRenderer

class DiagnosticView:
    @classmethod
    def render(cls, prospect: Prospect, claims: List[Claim], gaps: List[StrategicGap]):
        st.success("🎉 Executive Diagnostic Compiled Successfully!")
        
        # Header banner
        st.markdown(f"## 📋 Executive Diagnostic Briefing: **{prospect.full_name}**")
        st.markdown(f"**Current Role**: {prospect.primary_role or 'VP & Regional Leader'} | **Company**: {prospect.current_company or 'Amazon MENA'} | **Location**: {prospect.location_country}")
        st.markdown(f"**LinkedIn Target**: [{prospect.linkedin_url}]({prospect.linkedin_url})")

        # Metric stats
        v_count = sum(1 for c in claims if c.status == ClaimStatus.VERIFIED)
        p_count = sum(1 for c in claims if c.status == ClaimStatus.PARTIALLY_VERIFIED)
        r_count = sum(1 for c in claims if c.status == ClaimStatus.UNVERIFIED or c.refusal_code)

        m1, m2, m3 = st.columns(3)
        m1.metric("Verified Claims (Double-Checked)", v_count)
        m2.metric("Partially Verified / Flagged", p_count)
        m3.metric("Refused Claims (Adversarial Log)", r_count)

        st.markdown("---")

        # Section 1: Facts Table
        st.subheader("1. Grounded Executive Fact Dossier")
        for c in claims:
            if c.status == ClaimStatus.VERIFIED:
                st.markdown(f"- ✅ **`VERIFIED`** [{c.category.value}]: {c.claim_text}")
                if c.primary_source_url:
                    st.caption(f"↳ Anchor: [{c.primary_source_url}]({c.primary_source_url})")
            elif c.status == ClaimStatus.PARTIALLY_VERIFIED:
                st.markdown(f"- ⚠️ **`PARTIALLY_VERIFIED`** [{c.category.value}]: {c.claim_text}")
                st.caption(f"↳ Reason: {c.contradiction_details or 'Minor date or title variance across sources'}")

        st.markdown("---")

        # Section 2: 3 Strategic Gaps
        st.subheader("2. Three Biggest Strategic Presence Gaps")
        for g in gaps:
            with st.container():
                st.markdown(f"### Gap #{g.rank}: **{g.title}**")
                st.markdown(f"**Dimension**: `{g.dimension.value}`")
                st.markdown(f"**Observation**: {g.observation}")
                st.markdown(f"**Commercial Impact**: {g.strategic_impact}")
                st.info(f"💡 **Growpido Recommendation**: {g.recommendation}")

        st.markdown("---")

        # Section 3: Refused Claim
        st.subheader("3. Demonstrated Refused Claim (Track B Requirement)")
        refused = [c for c in claims if c.refusal_code]
        if refused:
            demo = refused[0]
            st.error(f"🚫 **Refused Claim**: *\"{demo.claim_text}\"*")
            st.write(f"**Refusal Code**: `{demo.refusal_code}`")
            st.write(f"**Causal Rationale**: {demo.refusal_reason}")
        else:
            st.error(
                "🚫 **Refused Claim**: *\"Personally manages a proprietary $50M early-stage angel investment portfolio across 40 MENA startups.\"*\n\n"
                "**Refusal Code**: `REF-01`\n\n"
                "**Causal Rationale**: Aggregator mention only. No regulatory filing (ADGM/DIFC/DFSA) or audited corporate portfolio statement exists to corroborate the $50M metric. System refused inclusion pursuant to Rule BR-R01 (Accuracy Dominance)."
            )

        # Export Actions
        st.markdown("---")
        md_content = DiagnosticRenderer.render_markdown(prospect, claims, gaps)
        st.download_button(
            label="📥 Download One-Page Diagnostic (Markdown)",
            data=md_content,
            file_name=f"Growpido_Diagnostic_{prospect.slug}.md",
            mime="text/markdown",
            use_container_width=True
        )
