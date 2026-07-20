"""
Fetches genuinely live current weather from NASA POWER's free API.
Kept separate from the historical-data-based prediction model — shown
as contextual information, not merged into the calibrated risk score,
to avoid overstating what the model actually accounts for.
"""
import requests
import streamlit as st
from datetime import datetime, timedelta


@st.cache_data(ttl=3600)  # refresh hourly
def get_live_weather(lat: float, lon: float) -> dict:
    end = datetime.now()
    start = end - timedelta(days=2)
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "PRECTOTCORR,T2M,RH2M",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start.strftime("%Y%m%d"),
        "end": end.strftime("%Y%m%d"),
        "format": "JSON",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()["properties"]["parameter"]

    latest_date = max(data["PRECTOTCORR"].keys())
    return {
        "date": latest_date,
        "rainfall_mm": data["PRECTOTCORR"][latest_date],
        "temperature_c": data["T2M"][latest_date],
        "humidity_pct": data["RH2M"][latest_date],
    }