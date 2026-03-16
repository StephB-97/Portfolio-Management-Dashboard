import streamlit as st

def apply_theme():
    st.set_page_config(
        page_title="Portfolio Manager",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="auto",
    )
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Dark background */
    html, body, .stApp {
        background-color: #080B12 !important;
        color: #E2E8F0 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Hide Streamlit's default menu and footer */
    #MainMenu       { visibility: hidden; }
    footer          { visibility: hidden; }
    header          { visibility: hidden; }
    .stDeployButton { display: none; }
                
                /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #0066FF 0%, #0044CC 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.04em !important;
        padding: 10px 22px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 12px rgba(0, 102, 255, 0.25) !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 20px rgba(0, 102, 255, 0.4) !important;
    }

    /* ── Text inputs ── */
    .stTextInput > div > div > input,
    .stDateInput  > div > div > input {
        background-color: #0F1629 !important;
        color: #E2E8F0 !important;
        border: 1px solid #1E2D45 !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.9rem !important;
        padding: 10px 14px !important;
    }
    .stTextInput > div > div > input:focus,
    .stDateInput  > div > div > input:focus {
        border-color: #0066FF !important;
        box-shadow: 0 0 0 2px rgba(0, 102, 255, 0.15) !important;
    }

    /* ── Input labels ── */
    .stTextInput > label,
    .stDateInput  > label,
    .stNumberInput > label {
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: #4A5568 !important;
    }
                
                /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #0F1629 0%, #111827 100%);
        border: 1px solid #1E2D45;
        border-radius: 10px;
        padding: 18px 22px !important;
        position: relative;
        overflow: hidden;
    }
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 3px; height: 100%;
        background: linear-gradient(180deg, #00D4AA, #0066FF);
        border-radius: 3px 0 0 3px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: #4A5568 !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.6rem !important;
        font-weight: 600 !important;
        color: #F7FAFC !important;
    }
    [data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #0A0F1E !important;
        border-right: 1px solid #1E2D45 !important;
    }
    [data-testid="stSidebar"] label {
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: #4A5568 !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #0D1526 !important;
        border: 1px solid #1E2D45 !important;
        border-radius: 8px !important;
        padding: 4px !important;
        gap: 2px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #4A5568 !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        border-radius: 6px !important;
        padding: 8px 18px !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0066FF 0%, #0044CC 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(0, 102, 255, 0.3) !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar       { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #080B12; }
    ::-webkit-scrollbar-thumb { background: #1E2D45; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #2D4A6B; }
                
                /* ── DataFrames ── */
    [data-testid="stDataFrame"] {
        border: 1px solid #1E2D45 !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    [data-testid="stDataFrame"] th {
        background-color: #0D1526 !important;
        color: #4A5568 !important;
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        padding: 10px 14px !important;
        border-bottom: 1px solid #1E2D45 !important;
    }
    [data-testid="stDataFrame"] td {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.82rem !important;
        color: #CBD5E0 !important;
        padding: 9px 14px !important;
        border-bottom: 1px solid #111827 !important;
    }

    /* ── Alerts ── */
    [data-testid="stAlert"] {
        border-radius: 6px !important;
        border: none !important;
        font-size: 0.84rem !important;
    }
    div[data-baseweb="notification"] {
        background-color: #0A1F15 !important;
        border-left: 3px solid #00D4AA !important;
    }
    div[role="alert"] {
        background-color: #1F0A0A !important;
        border-left: 3px solid #FC4444 !important;
    }

    /* ── Dividers ── */
    hr {
        border: none !important;
        border-top: 1px solid #1E2D45 !important;
        margin: 20px 0 !important;
    }

    /* ── Headings ── */
    h1 {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #F7FAFC !important;
        letter-spacing: -0.02em !important;
    }
    h2 {
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        color: #4A5568 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        border-bottom: 1px solid #1E2D45 !important;
        padding-bottom: 8px !important;
        margin-top: 28px !important;
    }
    h3 {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: #A0AEC0 !important;
    }

    /* ── Section label utility ── */
    .section-label {
        font-size: 0.62rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
        color: #0066FF !important;
        margin-bottom: 12px !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }
    .section-label::after {
        content: '' !important;
        flex: 1 !important;
        height: 1px !important;
        background: linear-gradient(90deg, #1E2D45, transparent) !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background-color: #0D1526 !important;
        border: 1px solid #1E2D45 !important;
        border-radius: 6px !important;
        color: #A0AEC0 !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
    }
    .streamlit-expanderContent {
        background-color: #0A0F1E !important;
        border: 1px solid #1E2D45 !important;
        border-top: none !important;
        border-radius: 0 0 6px 6px !important;
        color: #A0AEC0 !important;
        font-size: 0.84rem !important;
        line-height: 1.7 !important;
    }
    </style>
    """, unsafe_allow_html=True)