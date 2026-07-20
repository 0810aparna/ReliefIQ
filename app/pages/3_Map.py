import streamlit as st
import pandas as pd
import plotly.express as px
import sys
sys.path.append(".")
from app.api_client import get_districts, predict_district
from app.styles import apply_custom_style

st.set_page_config(page_title="Risk Map", page_icon="🗺️", layout="wide")
apply_custom_style()
st.title("🗺️ Kerala District Risk Map")
st.caption("Real district coordinates, live risk assessment overlaid")

districts = get_districts()

with st.spinner("Loading risk data for map..."):
    rows = []
    for d in districts:
        try:
            pred = predict_district(d["district_id"])
            rows.append({**d, **pred})
        except Exception:
            rows.append({**d, "severity": "Unknown", "risk_score": None})

df = pd.DataFrame(rows)

severity_color_map = {
    "Low": "#22C55E", "Medium": "#EAB308",
    "High": "#F97316", "Critical": "#EF4444", "Unknown": "#94A3B8",
}

fig = px.scatter_mapbox(
    df, lat="latitude", lon="longitude",
    color="severity", size="population",
    hover_name="district_name",
    hover_data={"risk_score": True, "population": True, "latitude": False, "longitude": False},
    color_discrete_map=severity_color_map,
    zoom=6.3, center={"lat": 10.5, "lon": 76.3},
    mapbox_style="carto-positron",
    height=600,
)
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), legend_title_text="Risk Level")
st.plotly_chart(fig, use_container_width=True)

st.caption("Marker size reflects population. Click the legend to isolate a risk level.")