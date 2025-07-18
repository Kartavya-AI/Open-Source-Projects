__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
sys.modules["sqlite3.dbapi2"] = sys.modules["pysqlite3.dbapi2"]

import streamlit as st
from src.open_source.crew import OpenSourceCrew

st.set_page_config(
    page_title="AI Open Source Researcher",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="auto"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* --- Base Styles --- */
    body {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }

    /* --- Main Content Area --- */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    /* --- Header --- */
    .header {
        font-size: 52px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
        background: -webkit-linear-gradient(45deg, #58a6ff, #a371f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subheader {
        text-align: center;
        color: #8b949e;
        font-size: 1.2rem;
        margin-bottom: 4rem;
        font-weight: 400;
    }

    /* --- Input Text Area --- */
    .stTextArea textarea {
        background-color: #161b22;
        color: #e6edf3;
        border: 1px solid #30363d;
        border-radius: 12px;
        min-height: 200px;
        font-size: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }
    .stTextArea textarea:focus {
        border-color: #58a6ff;
        box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.3);
    }

    /* --- Button --- */
    .stButton>button {
        width: 100%;
        background-image: linear-gradient(45deg, #58a6ff 0%, #a371f7 100%);
        color: white;
        border: none;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 18px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px rgba(88, 166, 255, 0.25);
        cursor: pointer;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(88, 166, 255, 0.35);
    }

    /* --- Glassmorphism Cards --- */
    .card {
        background: rgba(22, 27, 34, 0.6);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(48, 54, 61, 0.5);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .card h4 {
        color: #58a6ff;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .card li {
        color: #c9d1d9;
    }
    
    /* --- Results Box --- */
    .results-box {
        white-space: pre-wrap;
        font-family: 'SF Mono', 'Consolas', 'Liberation Mono', Menlo, Courier, monospace;
        background-color: #010409;
        color: #c9d1d9;
        border: 1px solid #30363d;
        padding: 25px;
        border-radius: 10px;
        margin-top: 20px;
        font-size: 14px;
        line-height: 1.6;
    }

    /* --- Warning Box --- */
    .warning-box {
        background-color: #1f2937;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 20px;
        color: #f59e0b;
        font-size: 14px;
    }

</style>
""", unsafe_allow_html=True)

st.markdown('<p class="header">🌌 AI Open Source Researcher</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Describe your vision. Our AI agents will navigate the digital cosmos to find your project\'s perfect match.</p>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1.2], gap="large")

with col1:
    st.markdown("### ✨ Your Project Blueprint")
    business_requirement = st.text_area(
        "Label is collapsed",
        label_visibility="collapsed",
        placeholder="Example: I need a self-hostable, lightweight CRM system with a modern UI, a good API for integrations, and built with Python/Django.",
        height=200
    )
    research_button = st.button("🚀 Launch Agents")

with col2:
    st.markdown(
        """
        <div class="card">
        <h4>Mission Protocol</h4>
        <ol>
            <li><strong>Analyze:</strong> An AI agent dissects your blueprint into technical specifications.</li>
            <li><strong>Research:</strong> A specialized agent scours GitHub for projects matching the specs.</li>
            <li><strong>Evaluate:</strong> A final agent assesses the findings and provides a ranked recommendation.</li>
        </ol>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <div class="card">
        <h4>Navigation Tips</h4>
        <ul>
            <li><b>Be specific:</b> Mention languages, frameworks, or key features.</li>
            <li><b>Define the use case:</b> Is it for a personal project, a startup, or enterprise use?</li>
            <li><b>Mention constraints:</b> E.g., "must have a permissive license like MIT".</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

if research_button:
    if not business_requirement:
        st.warning("📝 Please provide a project blueprint before launching the agents.")
    else:
        st.markdown("---")
        
        try:
            with st.spinner("🌌 Agents are deploying... Navigating the open-source universe..."):
                crew = OpenSourceCrew(business_requirement)
                result = crew.run()

            st.balloons()
            st.markdown("### ✅ Mission Complete! Transmission Received:")
            st.markdown(f'<div class="results-box">{result}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ An error occurred during the mission: {e}")
            st.info("💡 Make sure your API keys are configured in secrets.toml and you have sufficient quota.")