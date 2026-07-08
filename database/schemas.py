"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel


class DistrictOut(BaseModel):
    district_id: int
    district_name: str
    state: str
    latitude: float
    longitude: float
    population: int

    class Config:
        from_attributes = True


class PredictRequest(BaseModel):
    district_id: int


class PredictResponse(BaseModel):
    district_id: int
    district_name: str
    severity: str
    risk_score: float
    confidence: float
    decision_action: str
    alert_level: str
    components: dict