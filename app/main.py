import streamlit as st
import pandas as pd
import sys
sys.path.append(".")
from app.api_client import get_districts, predict_district

st.set_page_config(page_title="ReliefIQ", page_icon="🌊", layout="wide")

st.title("🌊 ReliefIQ")
st.caption("AI-powered flood relief decision support — Kerala, real 2018 flood data")

try:
    districts = get_districts()
except Exception:
    st.error("Could not reach the ReliefIQ API. Is the backend running? (`docker-compose up -d`)")
    st.stop()

with st.spinner("Loading district risk overview..."):
    predictions = [predict_district(d["district_id"]) for d in districts]

df = pd.DataFrame(predictions)
total_population = sum(d["population"] for d in districts)
high_risk_count = len(df[df["severity"].isin(["High", "Critical"])])

col1, col2, col3 = st.columns(3)
col1.metric("Districts Monitored", len(districts))
col2.metric("High / Critical Risk", high_risk_count)
col3.metric("Total Population Covered", f"{total_population:,}")

st.divider()

st.subheader("Current District Risk Overview")

severity_colors = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
df["Alert"] = df["severity"].map(severity_colors) + " " + df["severity"]

st.dataframe(
    df[["district_name", "Alert", "risk_score", "confidence"]].rename(
        columns={"district_name": "District", "risk_score": "Risk Score", "confidence": "Confidence"}
    ),
    use_container_width=True,
    hide_index=True,
)

st.caption("Use the sidebar to explore individual district risk factors or view the allocation plan.")