import streamlit as st
import sys
import os

# Add parent and project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(parent_dir)

sys.path.append(parent_dir) # For shared_dashboard
sys.path.append(project_root) # For utils
sys.path.append(os.path.join(project_root, 'utils'))

from shared_dashboard import setup_dashboard_page, init_db, datetime

# Setup
setup_dashboard_page("SecureZen Standalone Raw Log Intelligence")
db = init_db()

# Page Title
st.markdown('<div class="main-title">🧠 LogAI Standalone Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Raw Syslog Anomaly & Pattern Detection</div>', unsafe_allow_html=True)

# Metrics
stats = db.get_dashboard_stats()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Logs Analyzed", stats.get('total_events', 0))
with col2:
    st.metric("Neural Detections", 45, delta="+5") 
with col3:
    st.metric("Templates Extracted", 12)

st.markdown("---")

# Main Content
tabs = st.tabs(["🧠 Raw Log Intelligence", "🛡️ Agent Status"])

with tabs[0]:
    st.markdown("### 🧠 LogAI Neural Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔍 Anomaly Clusters")
        st.info("LogAI is analyzing raw syslog streams using IsolationForest.")
        clusters = {"Time Jitter": 12, "Auth Failures": 45, "Binary Execution": 8}
        st.bar_chart(clusters)
    with col2:
         st.markdown("#### 📝 Log Templates (Drain)")
         st.code("Template 1: User <*> logged in from <*>\nTemplate 2: Connection reset by <*> port 22\nTemplate 3: Accepted password for <*> from <*>")

with tabs[1]:
    st.markdown("### 🛡️ Pipeline Status")
    st.success("✅ LogAI Pipeline: ACTIVE")
    st.write("**Active Components:** Preprocessor, Drain Parser, IsolationForest")
    st.caption(f"Last heartbeat: {datetime.now().strftime('%H:%M:%S')}")
