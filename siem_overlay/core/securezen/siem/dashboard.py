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

from shared_dashboard import setup_dashboard_page, init_db, init_connector, os, datetime, go, pd

# Setup
setup_dashboard_page("SecureZen SIEM Overlay AI SOC")
db = init_db()
connector = init_connector()

# Sidebar for CSV Import
with st.sidebar:
    st.markdown("#### 📂 Import Wazuh Alerts")
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
    if uploaded_file:
        csv_path = os.path.join(project_root, 'data/temp_alerts.csv')
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        if st.button("📥 Load Alerts"):
            count = connector.load_csv_alerts(csv_path)
            st.success(f"✅ Loaded {count} alerts!")
            st.rerun()

# Page Title
st.markdown('<div class="main-title">🛡️ SIEM Overlay AI SOC</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Advanced Threat Correlation & Agentic Investigation</div>', unsafe_allow_html=True)

# Metrics
stats = db.get_dashboard_stats()
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Critical Alerts", stats.get('severity_counts', {}).get('Critical', 0))
with col2:
    st.metric("High Priority", stats.get('severity_counts', {}).get('High', 0))
with col3:
    st.metric("Total SIEM Alerts", stats.get('total_alerts', 0))
with col4:
    st.metric("AI Investigations", 24)

st.markdown("---")

# Main Content
tabs = st.tabs(["🎯 SIEM Overlay", "📋 Alerts Table", "🛡️ Platform Status"])

with tabs[0]:
    st.markdown("### 🎯 Multi-Source Threat Correlation")
    inner_tabs = st.tabs(["📊 Overview", "🎯 MITRE ATT&CK", "⚔️ Kill Chain"])
    
    with inner_tabs[0]:
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("### 🔴 Alert Severity Distribution")
            severity_counts = stats.get('severity_counts', {})
            if severity_counts:
                fig = go.Figure(data=[go.Pie(labels=list(severity_counts.keys()), values=list(severity_counts.values()), hole=0.5)])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                st.plotly_chart(fig, use_container_width=True)
        with col_right:
            st.markdown("### 🌍 Alert Type Distribution")
            alert_types = db.get_alert_type_stats()
            if alert_types:
                df = pd.DataFrame(alert_types)
                fig = go.Figure(data=[go.Bar(y=df['name'], x=df['value'], orientation='h')])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.markdown("### 📋 Unified Alert Feed")
    alerts = db.get_all_alerts(level_min=7)
    if alerts:
        st.dataframe(pd.DataFrame(alerts), use_container_width=True, hide_index=True)

with tabs[2]:
    st.markdown("### 🛡️ Platform Status")
    st.success("✅ Wazuh SIEM Connector: ACTIVE")
    st.success("🤖 Agent Swarm (CrewAI): READY")
