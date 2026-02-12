import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import sys
import os

# Add project root and utils to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'utils'))

from database import ThreatDatabase
from wazuh_connector import WazuhConnector

# ===== SHARED DASHBOARD SETUP =====
def setup_dashboard_page(title: str):
    st.set_page_config(
        page_title=title,
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
        .main { background-color: #0a0e27; }
        .stApp { background-color: #0a0e27; }
        .main-title { font-size: 2.5rem; font-weight: 700; color: #00d4ff; text-align: center; margin-bottom: 0.5rem; text-shadow: 0 0 10px rgba(0, 212, 255, 0.5); }
        .sub-title { font-size: 1rem; color: #8b949e; text-align: center; margin-bottom: 2rem; }
        [data-testid="stMetricValue"] { font-size: 2.5rem; font-weight: 700; color: #00d4ff; }
        [data-testid="stMetricLabel"] { color: #8b949e; font-size: 0.9rem; }
        .dashboard-card { background: linear-gradient(135deg, #1a1f3a 0%, #0f1729 100%); border: 1px solid #2d3748; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5); }
        .stTabs [data-baseweb="tab-list"] { gap: 2rem; background-color: #1a1f3a; padding: 0.5rem; border-radius: 10px; }
        .stTabs [data-baseweb="tab"] { color: #8b949e; font-weight: 600; }
        .stTabs [aria-selected="true"] { color: #00d4ff; border-bottom: 2px solid #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def init_db():
    return ThreatDatabase(db_path=os.path.join(project_root, "data/wazuh_alerts.db"))

@st.cache_resource
def init_connector():
    return WazuhConnector()
