import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.append(".")
from app.styles import apply_custom_style

st.set_page_config(page_title="Model Insights", page_icon="🔬", layout="wide")
apply_custom_style()
st.title("🔬 Model Insights & Evaluation History")
st.caption("The honest story: what was tried, what beat baseline, what didn't")

st.subheader("Approach Comparison (LOOCV, benchmarked against baseline)")

comparison_data = pd.DataFrame([
    {"Approach": "XGBoost (4-class)", "Score": 0.38, "Baseline": 0.46, "Beat Baseline": False},
    {"Approach": "XGBoost (binary)", "Score": 0.31, "Baseline": 0.62, "Beat Baseline": False},
    {"Approach": "XGBoost (binary, trimmed)", "Score": 0.54, "Baseline": 0.62, "Beat Baseline": False},
    {"Approach": "Logistic Regression (binary)", "Score": 0.54, "Baseline": 0.62, "Beat Baseline": False},
])

fig = go.Figure()
fig.add_trace(go.Bar(name="Model Score", x=comparison_data["Approach"], y=comparison_data["Score"],
                      marker_color="#0891B2"))
fig.add_trace(go.Bar(name="Majority-Class Baseline", x=comparison_data["Approach"], y=comparison_data["Baseline"],
                      marker_color="#94A3B8"))
fig.update_layout(barmode="group", yaxis_title="LOOCV Accuracy", height=450,
                   legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig, use_container_width=True)

st.info("**None of the tested ML approaches beat their baseline at n=13 samples.** "
        "This honest result — not a high accuracy number — is what motivated the pivot "
        "to a transparent composite scoring approach for production. See ADR-006, "
        "ADR-007, and ADR-008 for the full reasoning.")

st.divider()
st.subheader("Production Model: Composite Risk Score Weights")
weights_df = pd.DataFrame([
    {"Component": "Rainfall vs. Normal", "Weight": 0.4},
    {"Component": "Landslide Count", "Weight": 0.4},
    {"Component": "Rainfall Deviation", "Weight": 0.2},
])
fig2 = px.pie(weights_df, names="Component", values="Weight", hole=0.5,
              color_discrete_sequence=["#0891B2", "#F97316", "#94A3B8"])
fig2.update_layout(height=350)
st.plotly_chart(fig2, use_container_width=True)
st.caption("Weights are a documented judgment call (ADR-008), not fitted — fully transparent, "
           "unlike a black-box model's internal weights.")

st.divider()
st.subheader("Model Registry")
try:
    registry_df = pd.read_csv("models/model_registry.csv")
    st.dataframe(registry_df, use_container_width=True, hide_index=True)
except FileNotFoundError:
    st.warning("Model registry file not found in this environment.")