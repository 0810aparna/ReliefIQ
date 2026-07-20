"""Shared CSS injected across all pages for a consistent, polished look."""

CUSTOM_CSS = """
<style>
/* Card-style containers for metrics */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
    border: 1px solid #BAE6FD;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

/* Bigger, bolder metric values */
[data-testid="stMetricValue"] {
    font-size: 2rem;
    font-weight: 700;
    color: #0891B2;
}

/* Rounded buttons with a subtle shadow */
.stButton > button {
    border-radius: 8px;
    border: none;
    background-color: #0891B2;
    color: white;
    font-weight: 600;
    padding: 0.5rem 1.5rem;
    box-shadow: 0 2px 4px rgba(8, 145, 178, 0.3);
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background-color: #0E7490;
    box-shadow: 0 4px 8px rgba(8, 145, 178, 0.4);
    transform: translateY(-1px);
}

/* Section dividers with more breathing room */
hr {
    margin: 2rem 0;
    border-color: #E2E8F0;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #F8FAFC;
}

/* Dataframe/table rounded corners */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}
</style>
"""


def apply_custom_style():
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)