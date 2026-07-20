import streamlit as st
import pandas as pd
import plotly.express as px
import sys
sys.path.append(".")
from app.api_client import get_districts, run_optimization

st.set_page_config(page_title="Allocation Planner", page_icon="📦", layout="wide")

from app.styles import apply_custom_style
apply_custom_style()

st.title("📦 Allocation Planner")

st.caption("Runs the full pipeline (predict -> decide -> forecast -> optimize) across all "
           "districts and shows the priority-weighted, equity-capped allocation plan.")

total_food_available = st.slider(
    "Total food packets available", min_value=1000, max_value=20000, value=5000, step=500,
    help="Adjust to see how the allocation plan changes with more or less inventory."
)

if st.button("Run Optimization", type="primary"):
    with st.spinner("Running priority-weighted allocation..."):
        try:
            result = run_optimization(total_food_available)
        except Exception as e:
            st.error(f"Optimization failed: {e}")
            st.stop()

    if result["status"] == "NO_ACTION":
        st.success("No districts currently flagged for resource allocation.")
        st.stop()

    st.subheader(f"Status: {result['status']}")

    districts = {d["district_id"]: d["district_name"] for d in get_districts()}
    allocation = result["allocation"]

    df = pd.DataFrame([
        {"District": districts.get(int(k), k), "Allocated Food Packets": v}
        for k, v in allocation.items() if v > 0
    ]).sort_values("Allocated Food Packets", ascending=False)

    if df.empty:
        st.info("Optimizer ran, but no allocation was assigned at this inventory level.")
        st.stop()

    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(df, x="District", y="Allocated Food Packets", color="District",
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.caption(f"Note: no single district can receive more than 40% of total available stock "
               f"in one round (equity cap — see docs/optimization_writeup.md).")