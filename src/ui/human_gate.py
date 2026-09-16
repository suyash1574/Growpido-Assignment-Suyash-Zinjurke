import streamlit as st
from typing import List
from src.storage.models import Claim, ClaimStatus
from src.storage.db import Database

class HumanGateUI:
    @classmethod
    def render_staging_table(cls, prospect_id: str, claims: List[Claim], db: Database) -> bool:
        st.subheader("🛡️ Sovereign Human-in-the-Loop Review Gate")
        st.markdown(
            "Advisors MUST inspect extracted findings, review source citations, and verify contradiction flags "
            "before compiling the final C-suite Diagnostic."
        )

        override_occurred = False

        for idx, claim in enumerate(claims):
            status_color = "green" if claim.status == ClaimStatus.VERIFIED else ("orange" if claim.status == ClaimStatus.PARTIALLY_VERIFIED else "red")
            with st.expander(f"Claim #{idx+1}: [{claim.status.value}] {claim.claim_text[:80]}...", expanded=(claim.status != ClaimStatus.VERIFIED)):
                st.write(f"**Full Claim**: {claim.claim_text}")
                st.write(f"**Category**: `{claim.category.value}` | **Materiality**: `{claim.materiality.value}`")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Check 1 (Primary)**: {'✅ PASSED' if claim.check1_passed else '❌ FAILED'}")
                    if claim.primary_source_url:
                        st.markdown(f"Primary URL: [{claim.primary_source_url}]({claim.primary_source_url})")
                with col2:
                    st.write(f"**Check 2 (Corroboration)**: {'✅ PASSED' if claim.check2_passed else '❌ FAILED'}")
                    if claim.secondary_source_url:
                        st.markdown(f"Secondary URL: [{claim.secondary_source_url}]({claim.secondary_source_url})")

                if claim.contradiction_detected:
                    st.warning(f"⚠️ Contradiction Detected: {claim.contradiction_details or 'Conflicting source data'}")

                if claim.refusal_code:
                    st.error(f"🚫 Refusal Code: `{claim.refusal_code}` — {claim.refusal_reason}")

                # Manual Override Controls
                with st.form(key=f"override_form_{claim.claim_id}"):
                    new_status = st.selectbox(
                        "Adjudicate Status",
                        options=[ClaimStatus.VERIFIED.value, ClaimStatus.PARTIALLY_VERIFIED.value, ClaimStatus.UNVERIFIED.value],
                        index=[ClaimStatus.VERIFIED.value, ClaimStatus.PARTIALLY_VERIFIED.value, ClaimStatus.UNVERIFIED.value].index(claim.status.value)
                    )
                    notes = st.text_input("Mandatory Override Rationale (if changed):", value=claim.override_notes or "")
                    submit_btn = st.form_submit_button("Record Override")
                    
                    if submit_btn:
                        if new_status != claim.status.value:
                            claim.status = ClaimStatus(new_status)
                            claim.human_override = True
                            claim.override_notes = notes or "Manual override by Advisor"
                            db.save_claims([claim])
                            st.success(f"Claim #{idx+1} status updated to {new_status}!")
                            override_occurred = True

        st.markdown("---")
        return st.button("✅ Approve & Compile One-Page Diagnostic", type="primary", use_container_width=True)
