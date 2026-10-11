"""
Theme and custom CSS styling injector for EduPro platform.
Provides a modern SaaS UI with rich gradient cards, colored metric badges,
sleek dark-slate sidebar, glowing accents, and smooth hover transitions.
"""

import streamlit as st

CUSTOM_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #F1F5F9;
    }
    ::-webkit-scrollbar-thumb {
        background: #94A3B8;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #64748B;
    }

    /* Main App Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 50%, #F1F5F9 100%);
    }

    /* Sidebar Custom Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
        color: #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] strong {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #60A5FA !important;
        font-weight: 700;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.15) !important;
    }

    /* Sidebar Code & Tag Badges - High Contrast Cyan on Dark */
    section[data-testid="stSidebar"] code {
        background-color: #0F172A !important;
        color: #38BDF8 !important; /* Vivid Cyan Blue */
        border: 1px solid #0284C7 !important;
        border-radius: 6px !important;
        padding: 3px 8px !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        display: inline-block !important;
    }

    /* Global Content Code Blocks */
    code {
        color: #1E40AF !important;
        background-color: #EFF6FF !important;
        border: 1px solid #BFDBFE !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
    }

    /* Sidebar Info Alert Box */
    section[data-testid="stSidebar"] div[data-testid="stAlert"] {
        background-color: rgba(30, 58, 138, 0.45) !important;
        border: 1px solid rgba(96, 165, 250, 0.4) !important;
        border-radius: 10px !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stAlert"] * {
        color: #DBEAFE !important;
    }

    /* Top Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 50%, #3B82F6 100%);
        border-radius: 16px;
        padding: 2rem 2.2rem;
        color: #FFFFFF !important;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25);
        margin-bottom: 1.8rem;
        position: relative;
        overflow: hidden;
    }
    .hero-banner h1 {
        color: #FFFFFF !important;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.02em;
    }
    .hero-banner p {
        color: #DBEAFE !important;
        font-size: 1.05rem;
        margin: 0;
        max-width: 900px;
        line-height: 1.5;
    }

    /* Gradient KPI Metric Cards */
    .kpi-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 1.3rem 1.4rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 16px 28px -6px rgba(37, 99, 235, 0.18), 0 0 10px rgba(96, 165, 250, 0.15);
        border-color: #93C5FD;
    }
    .kpi-card-blue { border-top: 4px solid #2563EB; }
    .kpi-card-emerald { border-top: 4px solid #10B981; }
    .kpi-card-purple { border-top: 4px solid #8B5CF6; }
    .kpi-card-amber { border-top: 4px solid #F59E0B; }

    .kpi-value {
        font-size: 2rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.1;
        margin: 0.3rem 0;
    }
    .kpi-title {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748B;
    }
    .kpi-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-top: 0.4rem;
    }
    .badge-blue { background: #EFF6FF; color: #1D4ED8; }
    .badge-emerald { background: #ECFDF5; color: #047857; }
    .badge-purple { background: #F5F3FF; color: #6D28D9; }
    .badge-amber { background: #FFFBEB; color: #B45309; }

    /* Modern Glass Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 14px;
        padding: 1.4rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 1rem;
    }

    /* Course Recommendation Cards */
    .course-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 1.3rem;
        margin-bottom: 1rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .course-card:hover {
        border-color: #3B82F6;
        box-shadow: 0 10px 22px -4px rgba(59, 130, 246, 0.16);
        transform: translateY(-3px);
    }
    .match-tag {
        background: linear-gradient(135deg, #10B981, #059669);
        color: white;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        letter-spacing: 0.02em;
    }

    /* Plotly Chart Card Containers */
    div[data-testid="stPlotlyChart"] {
        background: #FFFFFF !important;
        border-radius: 14px !important;
        padding: 12px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 8px -2px rgba(0, 0, 0, 0.03) !important;
        margin-bottom: 1rem !important;
        transition: border-color 0.2s ease !important;
    }
    div[data-testid="stPlotlyChart"]:hover {
        border-color: #CBD5E1 !important;
    }

    /* Dataframe & Table Styling */
    div[data-testid="stDataFrame"] {
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        overflow: hidden !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
        background: #FFFFFF !important;
    }

    /* Streamlit Expander Styling */
    div[data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02) !important;
        margin-bottom: 1.2rem !important;
    }
    div[data-testid="stExpander"] summary {
        font-weight: 600 !important;
        color: #1E293B !important;
    }

    /* Input & Selectbox Styling */
    div[data-baseweb="select"] > div {
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        transition: all 0.2s ease !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: #3B82F6 !important;
    }

    /* Streamlit Tabs Modern Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F1F5F9;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 20px;
        border-radius: 8px;
        font-weight: 600;
        color: #64748B;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #2563EB !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }

    /* Button Enhancements */
    div.stButton > button:first-child {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
        transition: all 0.2s ease;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        border: none;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25);
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(37, 99, 235, 0.35);
    }

    /* Download Buttons */
    div.stDownloadButton > button {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 10px rgba(5, 150, 105, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    div.stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(5, 150, 105, 0.35) !important;
    }

    /* Streamlit Page Link Cards on Home Page */
    [data-testid="stPageLink-NavLink"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stPageLink-NavLink"]:hover {
        border-color: #3B82F6 !important;
        background: #EFF6FF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(59, 130, 246, 0.12) !important;
    }
</style>
"""


def apply_theme():
    """Injects the rich, modern CSS styling into the active Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
