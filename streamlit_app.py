"""
Streamlit UI for the AI Video Compliance Audit Pipeline.
Run with: streamlit run streamlit_app.py
"""

import uuid
import json
import logging

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from backend.src.graph.workflow import create_graph

# ── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("llmops.compliance.streamlit")

# ── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Video Compliance Audit",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown(
    """
<style>
/* ─── Import Google Font ─── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif;
}

/* ─── Hero header ─── */
.hero {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    padding: 2.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,.35);
}
.hero h1 {
    color: #ffffff;
    font-size: 2.4rem;
    font-weight: 800;
    margin: 0 0 .4rem 0;
    letter-spacing: -0.5px;
}
.hero p {
    color: #b0b3c5;
    font-size: 1.05rem;
    margin: 0;
}

/* ─── Status badges ─── */
.badge {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 24px;
    font-weight: 700;
    font-size: .95rem;
    letter-spacing: .5px;
}
.badge-pass {
    background: linear-gradient(135deg, #00c853, #00e676);
    color: #0a2e14;
}
.badge-fail {
    background: linear-gradient(135deg, #ff1744, #ff5252);
    color: #ffffff;
}

/* ─── Violation cards ─── */
.violation-card {
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    margin-bottom: .75rem;
    transition: transform .15s ease, box-shadow .15s ease;
}
.violation-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0,0,0,.25);
}
.severity-critical {
    border-left: 4px solid #ff1744;
}
.severity-warning {
    border-left: 4px solid #ffc107;
}
.severity-tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 6px;
    font-size: .78rem;
    font-weight: 700;
    margin-right: 8px;
}
.tag-critical {
    background: rgba(255,23,68,.15);
    color: #ff1744;
}
.tag-warning {
    background: rgba(255,193,7,.15);
    color: #ffc107;
}
.category-label {
    font-weight: 600;
    font-size: .92rem;
    color: #ccc;
}

/* ─── Summary box ─── */
.summary-box {
    background: linear-gradient(135deg, rgba(48,43,99,.35), rgba(36,36,62,.55));
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 14px;
    padding: 1.5rem 1.6rem;
    line-height: 1.7;
    font-size: .95rem;
}

/* ─── Sidebar styling ─── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1730 0%, #0f0c29 100%);
}

/* ─── Input area ─── */
.input-area {
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/shield-with-a-checkmark.png",
        width=64,
    )
    st.markdown("### 🛡️ Compliance Auditor")
    st.markdown(
        "AI-powered FTC-style compliance audit for YouTube videos. "
        "Paste a URL, hit **Run Audit**, and get instant results."
    )
    st.divider()
    st.markdown("**Tech Stack**")
    st.markdown(
        """
- 🎙️ Whisper (Speech-to-Text)
- 🗂️ FAISS (Vector DB)
- 🤗 HuggingFace Embeddings
- 🔗 LangGraph (Orchestration)
- ⚡ Groq LLM (Structured JSON)
"""
    )
    st.divider()
    st.caption("Built with Streamlit · v1.0")

# ── Hero ─────────────────────────────────────────────────────────────────────

st.markdown(
    """
<div class="hero">
    <h1>🛡️ AI Video Compliance Audit</h1>
    <p>Automated FTC-style compliance analysis for YouTube video content</p>
</div>
""",
    unsafe_allow_html=True,
)

# ── Input Section ────────────────────────────────────────────────────────────

col_input, col_btn = st.columns([4, 1], vertical_alignment="bottom")

with col_input:
    video_url = st.text_input(
        "YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed",
    )

with col_btn:
    run_clicked = st.button("🚀 Run Audit", use_container_width=True, type="primary")

# ── Pipeline Execution ──────────────────────────────────────────────────────

if run_clicked:
    if not video_url.strip():
        st.warning("⚠️ Please enter a valid YouTube URL to proceed.")
        st.stop()

    session_id = str(uuid.uuid4())

    initial_inputs = {
        "video_url": video_url.strip(),
        "video_id": f"vid_{session_id[:8]}",
        "transcript": "",
        "ocr_text": "",
        "video_metadata": {},
        "compliance_issues": [],
        "final_status": "",
        "final_report": "",
        "errors": [],
    }

    with st.status("🔄 Running Compliance Audit Pipeline…", expanded=True) as status:

        # Step 1 — Build Graph
        st.write("⚙️ Compiling LangGraph workflow…")
        app = create_graph()

        # Step 2 — Execute
        st.write("📥 Downloading video & transcribing with Whisper…")
        st.write("🔍 Retrieving compliance rules via FAISS…")
        st.write("🤖 Auditing transcript with Groq LLM…")

        try:
            final_state = app.invoke(initial_inputs)
            status.update(label="✅ Audit Complete!", state="complete", expanded=False)
        except Exception as exc:
            status.update(label="❌ Pipeline Failed", state="error", expanded=False)
            st.error(f"**Pipeline Error:** {exc}")
            logger.error(f"Workflow execution failed: {exc}")
            st.stop()

    # ── Results ──────────────────────────────────────────────────────────────

    st.markdown("---")
    st.markdown("## 📋 Audit Results")

    # Meta row
    meta_col1, meta_col2, meta_col3 = st.columns(3)

    with meta_col1:
        st.metric("Video ID", final_state.get("video_id", "—"))

    with meta_col2:
        status_val = final_state.get("final_status", "FAIL").upper()
        badge_class = "badge-pass" if status_val == "PASS" else "badge-fail"
        st.markdown(
            f'<span class="badge {badge_class}">{status_val}</span>',
            unsafe_allow_html=True,
        )

    with meta_col3:
        issues = final_state.get("compliance_issues", [])
        st.metric("Violations Found", len(issues))

    st.markdown("")

    # Violations
    if issues:
        st.markdown("### 🚨 Violations Detected")
        for issue in issues:
            sev = issue.get("severity", "WARNING").upper()
            sev_class = "severity-critical" if sev == "CRITICAL" else "severity-warning"
            tag_class = "tag-critical" if sev == "CRITICAL" else "tag-warning"
            icon = "🔴" if sev == "CRITICAL" else "🟡"

            st.markdown(
                f"""
<div class="violation-card {sev_class}">
    <span class="severity-tag {tag_class}">{icon} {sev}</span>
    <span class="category-label">{issue.get('category', 'General')}</span>
    <p style="margin:.6rem 0 0 0; color:#ddd; font-size:.9rem;">{issue.get('description', '')}</p>
</div>
""",
                unsafe_allow_html=True,
            )
    else:
        st.success("✅ No compliance violations detected — this video passed all checks!")

    # Final Report
    st.markdown("### 📝 Final Summary")
    report = final_state.get("final_report", "No report generated.")
    st.markdown(
        f'<div class="summary-box">{report}</div>',
        unsafe_allow_html=True,
    )
