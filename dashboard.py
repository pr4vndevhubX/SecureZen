"""
Seceon-Style IP Threat Intelligence Dashboard
Complete working version
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from database import ThreatDatabase
from wazuh_connector import WazuhConnector

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="IP Threat Intelligence Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CUSTOM CSS - SECEON DARK THEME =====
st.markdown("""
<style>
    /* Dark background */
    .main {
        background-color: #0a0e27;
    }
    
    .stApp {
        background-color: #0a0e27;
    }
    
    /* Header */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00d4ff;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }
    
    .sub-title {
        font-size: 1rem;
        color: #8b949e;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Metric cards - Seceon style */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00d4ff;
    }
    
    [data-testid="stMetricLabel"] {
        color: #8b949e;
        font-size: 0.9rem;
    }
    
    /* Cards */
    .dashboard-card {
        background: linear-gradient(135deg, #1a1f3a 0%, #0f1729 100%);
        border: 1px solid #2d3748;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: #1a1f3a;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #8b949e;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        color: #00d4ff;
        border-bottom: 2px solid #00d4ff;
    }
    
    /* Dataframe */
    [data-testid="stDataFrame"] {
        background-color: #1a1f3a;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f1729;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #00d4ff;
        color: #0a0e27;
        font-weight: 600;
        border: none;
        border-radius: 5px;
    }
    
    .stButton > button:hover {
        background-color: #00b8e6;
        color: #0a0e27;
    }
</style>
""", unsafe_allow_html=True)

# ===== INITIALIZE =====
@st.cache_resource
def init_database():
    return ThreatDatabase()

@st.cache_resource
def init_connector():
    return WazuhConnector()

db = init_database()
connector = init_connector()

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("### 🛡️ Threat Intelligence")
    st.markdown("---")
    
    # Upload CSV
    st.markdown("#### 📂 Import Wazuh Alerts")
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'], label_visibility="collapsed")
    
    if uploaded_file:
        # Save temporarily
        csv_path = 'data/wazuh_alerts.csv'
        with open(csv_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("📥 Load Alerts", use_container_width=True):
            with st.spinner("Loading alerts..."):
                count = connector.load_csv_alerts(csv_path)
                st.success(f"✅ Loaded {count} alerts!")
                st.rerun()
    
    st.markdown("---")
    
    # Time range filter
    st.markdown("#### ⏱️ Time Range")
    time_range = st.selectbox(
        "Select",
        ["Last 7 Days", "Last 24 Hours", "Last 30 Days", "All Time"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Database stats
    st.markdown("#### 📊 Database Info")
    try:
        stats = db.get_dashboard_stats()
        st.metric("Total Alerts", stats.get('total_alerts', 0))
        st.metric("IPs Analyzed", sum(stats.get('threat_levels', {}).values()))
    except Exception as e:
        st.warning("Database empty")
    
    st.markdown("---")
    
    # Webhook info
    st.markdown("#### 🔗 Webhook URL")
    st.code("http://localhost:5000/webhook/wazuh", language="bash")
    
    st.markdown("---")
    st.caption("🔒 Powered by Krya Solutions")
    st.caption(f"v1.0.0 | {datetime.now().strftime('%Y-%m-%d')}")

# ===== HEADER =====
st.markdown('<div class="main-title">🛡️ IP Threat Intelligence Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Real-time MITRE ATT&CK & Cyber Kill Chain Analysis</div>', unsafe_allow_html=True)

# ===== LOAD DASHBOARD DATA =====
try:
    stats = db.get_dashboard_stats()
    has_data = stats.get('total_alerts', 0) > 0
except Exception as e:
    st.error(f"Database error: {e}")
    has_data = False
    stats = {}

# ===== ROW 1: METRICS =====
st.markdown("### 📊 Alert Overview")

col1, col2, col3, col4, col5 = st.columns(5)

severity_counts = stats.get('severity_counts', {})

with col1:
    st.metric(
        label="🔴 CRITICAL",
        value=severity_counts.get('Critical', 0),
        delta=f"+{max(0, severity_counts.get('Critical', 0) - 10)}"
    )

with col2:
    st.metric(
        label="🟠 HIGH",
        value=severity_counts.get('High', 0),
        delta=f"+{max(0, severity_counts.get('High', 0) - 30)}"
    )

with col3:
    st.metric(
        label="🟡 MEDIUM",
        value=severity_counts.get('Medium', 0),
        delta=f"+{max(0, severity_counts.get('Medium', 0) - 50)}"
    )

with col4:
    st.metric(
        label="📊 TOTAL ALERTS",
        value=stats.get('total_alerts', 0)
    )

with col5:
    threat_counts = stats.get('threat_levels', {})
    st.metric(
        label="⚠️ IPs ANALYZED",
        value=sum(threat_counts.values()) if threat_counts else 0
    )

st.markdown("---")

# ===== TABS =====
if not has_data:
    st.warning("⚠️ No data available. Please upload Wazuh alerts CSV using the sidebar.")
    st.info("👈 Use the **Upload CSV** button in the sidebar to get started.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "🎯 MITRE ATT&CK",
    "⚔️ Kill Chain",
    "📋 Alerts Table"
])

# ===== TAB 1: OVERVIEW =====
with tab1:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("### 🔴 Alert Severity Distribution")
        
        if severity_counts:
            fig_severity = go.Figure(data=[
                go.Pie(
                    labels=list(severity_counts.keys()),
                    values=list(severity_counts.values()),
                    hole=0.5,
                    marker=dict(
                        colors=['#dc2626', '#ea580c', '#fbbf24'],
                        line=dict(color='#0a0e27', width=2)
                    ),
                    textinfo='label+percent',
                    textfont=dict(color='white', size=14)
                )
            ])
            
            fig_severity.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=True,
                legend=dict(
                    font=dict(color='white')
                )
            )
            
            st.plotly_chart(fig_severity, use_container_width=True)
        else:
            st.info("No severity data available.")
    
    with col_right:
        st.markdown("### 🌍 Alert Type Distribution")
        
        # Get alert types from database
        alerts = db.get_all_alerts(level_min=7)
        
        if alerts:
            df_alerts = pd.DataFrame(alerts)
            type_counts = df_alerts['rule_description'].value_counts().head(5).to_dict()
            
            fig_types = go.Figure(data=[
                go.Bar(
                    y=list(type_counts.keys()),
                    x=list(type_counts.values()),
                    orientation='h',
                    marker=dict(
                        color='#00d4ff',
                        line=dict(color='#0a0e27', width=1)
                    ),
                    text=list(type_counts.values()),
                    textposition='auto',
                    textfont=dict(color='white')
                )
            ])
            
            fig_types.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(
                    gridcolor='#2d3748',
                    showgrid=True
                ),
                yaxis=dict(
                    gridcolor='#2d3748'
                )
            )
            
            st.plotly_chart(fig_types, use_container_width=True)
        else:
            st.info("No alert data available.")

# ===== TAB 2: MITRE ATT&CK =====
with tab2:
    st.markdown("### 🎯 MITRE ATT&CK Techniques")
    
    top_mitre = stats.get('top_mitre', [])
    
    if top_mitre and len(top_mitre) > 0:
        df_mitre = pd.DataFrame(
            top_mitre,
            columns=['Technique ID', 'Technique Name', 'Tactic', 'Count']
        )
        
        # Filter out empty techniques
        df_mitre = df_mitre[df_mitre['Technique ID'] != '']
        
        if not df_mitre.empty:
            fig_mitre = go.Figure(data=[
                go.Bar(
                    y=df_mitre['Technique ID'] + ': ' + df_mitre['Technique Name'],
                    x=df_mitre['Count'],
                    orientation='h',
                    marker=dict(
                        color=df_mitre['Count'],
                        colorscale='Reds',
                        showscale=True,
                        colorbar=dict(
                            title="Alert Count",
                            titlefont=dict(color='white'),
                            tickfont=dict(color='white')
                        )
                    ),
                    text=df_mitre['Count'],
                    textposition='auto',
                    textfont=dict(color='white', size=12)
                )
            ])
            
            fig_mitre.update_layout(
                height=600,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis_title="Alert Count",
                yaxis_title="MITRE Technique",
                xaxis=dict(
                    gridcolor='#2d3748',
                    showgrid=True
                ),
                yaxis=dict(
                    gridcolor='#2d3748'
                )
            )
            
            st.plotly_chart(fig_mitre, use_container_width=True)
        else:
            st.info("No MITRE techniques detected in alerts.")
    else:
        st.info("No MITRE techniques detected yet. Upload alerts with MITRE mappings.")

# ===== TAB 3: KILL CHAIN =====
with tab3:
    st.markdown("### ⚔️ Cyber Kill Chain Analysis")
    
    # Sample kill chain data (can be enhanced with real data later)
    kill_chain = {
        'Reconnaissance': 25,
        'Weaponization': 15,
        'Delivery': 40,
        'Exploitation': 55,
        'Installation': 30,
        'Command & Control': 65,
        'Actions on Objectives': 35
    }
    
    df_kc = pd.DataFrame({
        'Phase': list(kill_chain.keys()),
        'Percentage': [(v/max(kill_chain.values()))*100 for v in kill_chain.values()],
        'Count': list(kill_chain.values())
    })
    
    fig_kc = go.Figure(data=[
        go.Bar(
            y=df_kc['Phase'],
            x=df_kc['Percentage'],
            orientation='h',
            marker=dict(
                color=df_kc['Percentage'],
                colorscale='Blues',
                showscale=True,
                colorbar=dict(
                    title="Detection %",
                    titlefont=dict(color='white'),
                    tickfont=dict(color='white')
                )
            ),
            text=[f"{p:.1f}% ({c})" for p, c in zip(df_kc['Percentage'], df_kc['Count'])],
            textposition='auto',
            textfont=dict(color='white', size=12)
        )
    ])
    
    fig_kc.update_layout(
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=14),
        xaxis_title="Detection Rate (%)",
        yaxis_title="Kill Chain Phase",
        xaxis=dict(
            range=[0, 100],
            gridcolor='#2d3748',
            showgrid=True
        ),
        yaxis=dict(
            gridcolor='#2d3748'
        )
    )
    
    st.plotly_chart(fig_kc, use_container_width=True)
    
    st.info("💡 Kill Chain data is currently sample data. Will be populated with real analysis results.")

# ===== TAB 4: ALERTS TABLE =====
with tab4:
    st.markdown("### 📋 Wazuh Alerts (Level ≥ 7)")
    
    alerts = db.get_all_alerts(level_min=7)
    
    if alerts:
        df_alerts = pd.DataFrame(alerts)
        
        # Format for display
        display_cols = ['timestamp', 'alert_id', 'rule_description', 'severity', 'src_ip', 'agent_name']
        
        # Add MITRE column if exists
        if 'rule_mitre_id' in df_alerts.columns:
            display_cols.append('rule_mitre_id')
        
        df_display = df_alerts[display_cols].copy()
        df_display['timestamp'] = pd.to_datetime(df_display['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Rename columns for better display
        df_display.columns = ['Time', 'Alert ID', 'Description', 'Severity', 'Source IP', 'Entity'] + (['MITRE ID'] if 'rule_mitre_id' in display_cols else [])
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        st.caption(f"Showing {len(alerts)} alerts (Level ≥ 7)")
        
        # Download button
        csv = df_alerts.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"wazuh_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No alerts found. Upload CSV to populate data.")

# ===== FOOTER =====
st.markdown("---")
col_f1, col_f2 = st.columns([3, 1])
with col_f1:
    st.caption("🔒 Powered by CrewAI + MITRE ATT&CK + Wazuh SIEM")
with col_f2:
    st.caption(f"© 2025 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")