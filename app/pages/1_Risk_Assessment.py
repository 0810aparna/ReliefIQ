import streamlit as st
import plotly.graph_objects as go
import sys
sys.path.append(".")
from app.api_client import get_districts, predict_district

st.set_page_config(page_title="Risk Assessment", page_icon="🔍", layout="wide")
st.title("🔍 Risk Assessment")

districts = get_districts()
district_names = {d["district_name"]: d["district_id"] for d in districts}

selected_name = st.selectbox("Select a district", sorted(district_names.keys()))
selected_id = district_names[selected_name]

if st.button("Run Prediction", type="primary"):
    with st.spinner(f"Assessing risk for {selected_name}..."):
        try:
            result = predict_district(selected_id)
        except Exception as e:
            st.error(f"Prediction failed: {e}")
            st.stop()

    severity_colors = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
    st.subheader(f"{severity_colors[result['severity']]} {result['severity']} Risk")

    col1, col2, col3 = st.columns(3)
    col1.metric("Risk Score", result["risk_score"])
    col2.metric("Confidence", f"{result['confidence']*100:.0f}%")
    col3.metric("Decision", result["decision_action"].replace("_", " ").title())

    st.divider()
    st.subheader("What's driving this score?")
    st.caption("ReliefIQ's v1 predictor is a transparent, weighted composite score — every "
               "contribution below is fully traceable, not a black-box output. See ADR-008.")

    components = result["components"]
    fig = go.Figure(go.Bar(
        x=list(components.values()),
        y=["Rainfall vs. Normal", "Landslide Count", "Rainfall Deviation"],
        orientation="h",
        marker_color=["#1B4965", "#5FA8D3", "#BEE9E8"],
    ))
    fig.update_layout(
        xaxis_title="Contribution to Risk Score",
        yaxis_title="",
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    if result["decision_action"] == "RUN_OPTIMIZER":
        st.warning(f"This district is flagged for resource allocation ({result['alert_level']} alert level). "
                   f"See the Allocation Planner page.")