"""
Contract for anything that predicts flood severity. The orchestrator only
ever talks to this interface — it doesn't know or care whether the real
implementation is a rule-based score, an ML model, or anything else.
"""

from typing import Protocol, TypedDict


class PredictionResult(TypedDict):
    severity: str
    risk_score: float
    confidence: float


class SeverityPredictor(Protocol):
    def predict(self, district_row: dict) -> PredictionResult: ...
