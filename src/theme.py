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

    /* Main App Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 50%, #F1F5F9 100%);
    }

    /* Sidebar Custom Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    section[data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #60A5FA !important;
        font-weight: 700;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.15) !important;
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
        transition: all 0.25s ease-in-out;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px -5px rgba(37, 99, 235, 0.15);
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
        transition: all 0.2s ease-in-out;
    }
    .course-card:hover {
        border-color: #3B82F6;
        box-shadow: 0 8px 16px -4px rgba(59, 130, 246, 0.12);
        transform: translateY(-2px);
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

    /* Streamlit Page Link Cards on Home Page */
    [data-testid="stPageLink-NavLink"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stPageLink-NavLink"]:hover {
        border-color: #3B82F6 !important;
        background: #EFF6FF !important;
        transform: translateY(-2px) !important;
    }
</style>
"""


def apply_theme():
    """Injects the rich, modern CSS styling into the active Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
