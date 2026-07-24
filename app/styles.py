"""Shared CSS + light/dark theme system, applied consistently across all pages."""
import streamlit as st

LIGHT = {
    "bg": "#FFFFFF", "bg_secondary": "#F0F9FF", "text": "#0F172A",
    "text_secondary": "#475569", "primary": "#0891B2", "primary_hover": "#0E7490",
    "border": "#BAE6FD", "card_shadow": "rgba(0,0,0,0.06)", "plotly_template": "plotly_white",
}
DARK = {
    "bg": "#0F172A", "bg_secondary": "#1E293B", "text": "#F1F5F9",
    "text_secondary": "#94A3B8", "primary": "#22D3EE", "primary_hover": "#06B6D4",
    "border": "#334155", "card_shadow": "rgba(0,0,0,0.4)", "plotly_template": "plotly_dark",
}


def _init_theme_state():
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False


def render_theme_toggle():
    _init_theme_state()
    st.session_state.dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)


def current_theme() -> dict:
    _init_theme_state()
    return DARK if st.session_state.dark_mode else LIGHT


def plotly_template() -> str:
    return current_theme()["plotly_template"]


def apply_custom_style():
    _init_theme_state()
    t = current_theme()
    css = f"""
    <style>
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{ background-color: {t['bg']}; }}
    [data-testid="stSidebar"] {{ background-color: {t['bg_secondary']}; }}
    h1, h2, h3, h4, p, span, label, .stMarkdown {{ color: {t['text']} !important; }}
    .stCaption, [data-testid="stCaptionContainer"] {{ color: {t['text_secondary']} !important; }}
    [data-testid="stMetric"] {{
        background: {t['bg_secondary']}; border: 1px solid {t['border']};
        border-radius: 12px; padding: 16px 20px; box-shadow: 0 1px 3px {t['card_shadow']};
    }}
    [data-testid="stMetricValue"] {{ font-size: 2rem; font-weight: 700; color: {t['primary']}; }}
    [data-testid="stMetricLabel"] {{ color: {t['text_secondary']} !important; }}
    .stButton > button {{
        border-radius: 8px; border: none; background-color: {t['primary']};
        color: white; font-weight: 600; padding: 0.5rem 1.5rem;
        box-shadow: 0 2px 4px {t['card_shadow']}; transition: all 0.2s ease;
    }}
    .stButton > button:hover {{ background-color: {t['primary_hover']}; transform: translateY(-1px); }}
    hr {{ margin: 2rem 0; border-color: {t['border']}; }}
    [data-testid="stDataFrame"] {{ border-radius: 10px; overflow: hidden; }}
    [data-testid="stSelectbox"] > div > div, [data-testid="stSlider"] {{ background-color: {t['bg_secondary']}; }}
    [data-testid="stAlert"] {{ color: {t['text']} !important; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)