import streamlit as st
import asyncio
from src.storage.db import Database
from src.orchestrator import Orchestrator
from src.ui.human_gate import HumanGateUI
from src.ui.diagnostic_view import DiagnosticView
from src.storage.models import ProspectStatus

st.set_page_config(
    page_title="Growpido — Prospect Intelligence Engine (Track B)",
    page_icon="🔍",
    layout="wide"
)

# Initialize singletons in session state
if "db" not in st.session_state:
    st.session_state.db = Database()
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = Orchestrator(st.session_state.db)
if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None
if "approved" not in st.session_state:
    st.session_state.approved = False

st.title("🔍 Growpido Track B — Prospect to Diagnostic Intelligence Engine")
st.caption("Adversarial OSINT Research • Double-Checked Primary Verification • Sovereign Human Gate • One-Page Diagnostic")

# Sidebar candidate fast-picker
with st.sidebar:
    st.header("🎯 Candidate Selection")
    st.markdown("**Assessment Target (UAE Track B):**")
    st.markdown("• **Ronaldo Mouchawar** (VP Amazon MENA, Co-Founder Souq.com)")
    st.caption("Pioneer of Middle East tech; $580M Amazon acquisition.")
    
    prefill = st.button("Use Ronaldo Mouchawar LinkedIn")
    st.markdown("---")
    st.markdown("**Inviolable Law:**")
    st.info("Accuracy takes absolute precedence over completeness. Unverified claims are quarantined.")

default_url = "https://www.linkedin.com/in/ronaldo-mouchawar-souq" if prefill else ""

# Target Ingestion Form
st.subheader("1. Ingest Prospect LinkedIn URL")
with st.form(key="ingest_form"):
    target_url = st.text_input(
        "Public LinkedIn URL:",
        value=default_url or "https://www.linkedin.com/in/ronaldo-mouchawar-souq",
        placeholder="https://www.linkedin.com/in/..."
    )
    submit_run = st.form_submit_button("🚀 Run Intelligence Pipeline", type="primary")

if submit_run:
    if not target_url or "linkedin.com/in/" not in target_url:
        st.error("Please provide a valid public LinkedIn profile URL (e.g. https://www.linkedin.com/in/ronaldo-mouchawar-souq)")
    else:
        with st.spinner("Executing Live OSINT Discovery, Claim Audit & Double-Check Verification via Groq..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                res = loop.run_until_complete(st.session_state.orchestrator.execute_research(target_url))
                st.session_state.pipeline_result = res
                st.session_state.approved = False
                st.rerun()
            except Exception as e:
                st.error(f"Pipeline Execution Failed: {str(e)}")

# Staged Human Gate Stage
if st.session_state.pipeline_result and not st.session_state.approved:
    res = st.session_state.pipeline_result
    st.markdown("---")
    approved = HumanGateUI.render_staging_table(str(res["prospect"].prospect_id), res["claims"], st.session_state.db)
    if approved:
        st.session_state.approved = True
        st.rerun()

# Final One-Page Diagnostic View
if st.session_state.pipeline_result and st.session_state.approved:
    res = st.session_state.pipeline_result
    st.markdown("---")
    DiagnosticView.render(res["prospect"], res["claims"], res["gaps"])
