import requests
import streamlit as st

API_BASE_URL = "http://localhost:8000"


@st.cache_data(ttl=300)
def get_districts():
    response = requests.get(f"{API_BASE_URL}/districts")
    response.raise_for_status()
    return response.json()


def predict_district(district_id: int):
    response = requests.post(f"{API_BASE_URL}/predict", json={"district_id": district_id})
    response.raise_for_status()
    return response.json()


def run_optimization(total_food_available: int = 5000):
    response = requests.post(f"{API_BASE_URL}/optimize", params={"total_food_available": total_food_available})
    response.raise_for_status()
    return response.json()