import streamlit as st
import pandas as pd
import plotly.express as px
import sys
sys.path.append(".")
from app.styles import apply_custom_style

st.set_page_config(page_title="Historical Trends", page_icon="📈", layout="wide")
apply_custom_style()
st.title("📈 Historical Rainfall Trends — Kerala (1901–2015)")
st.caption("Real data: data/raw/rainfall_india.csv")

@st.cache_data(ttl=3600)
def load_rainfall_history():
    # Note: adjust this if running the dashboard against a deployed API
    # rather than local files — for now this reads the same CSV used
    # to seed the database, since this is slow-changing reference data.
    df = pd.read_csv("data/raw/rainfall_india.csv")
    kerala = df[df["SUBDIVISION"].str.upper() == "KERALA"]
    return kerala

kerala_df = load_rainfall_history()

col1, col2 = st.columns(2)
with col1:
    fig1 = px.line(kerala_df, x="YEAR", y="ANNUAL",
                    title="Annual Rainfall Over Time",
                    labels={"ANNUAL": "Rainfall (mm)", "YEAR": "Year"})
    fig1.update_traces(line_color="#0891B2")
    fig1.add_hline(y=kerala_df["ANNUAL"].mean(), line_dash="dash",
                    annotation_text="Long-term average", line_color="#EF4444")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.line(kerala_df, x="YEAR", y="Jun-Sep",
                    title="Monsoon Season Rainfall (Jun–Sep)",
                    labels={"Jun-Sep": "Rainfall (mm)", "YEAR": "Year"})
    fig2.update_traces(line_color="#F97316")
    fig2.add_vline(x=2018, line_dash="dot", annotation_text="2018 Floods",
                    line_color="#EF4444")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.subheader("Monthly Rainfall Pattern (Average Across All Years)")
monthly_avg = kerala_df[["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]].mean()
fig3 = px.bar(x=monthly_avg.index, y=monthly_avg.values,
              labels={"x": "Month", "y": "Avg Rainfall (mm)"},
              color=monthly_avg.values, color_continuous_scale="Blues")
fig3.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig3, use_container_width=True)
st.caption("Confirms the Jun–Sep monsoon pattern used in the risk scoring model's assumptions.")