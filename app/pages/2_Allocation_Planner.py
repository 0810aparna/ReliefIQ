import streamlit as st
import pandas as pd
import plotly.express as px
import sys
sys.path.append(".")
from app.api_client import get_districts, run_optimization
from app.styles import apply_custom_style, render_theme_toggle, plotly_template

st.set_page_config(page_title="Allocation Planner", page_icon="📦", layout="wide")
render_theme_toggle()
apply_custom_style()

st.title("📦 Allocation Planner")
st.caption("Runs predict -> decide -> forecast -> optimize across all districts.")

total_food_available = st.slider("Total food packets available", 1000, 20000, 5000, 500)

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
                     template=plotly_template(), color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.caption("Note: no single district can receive more than 40% of total available stock "
               "in one round (equity cap).")