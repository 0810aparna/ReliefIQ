# services/rule_based_predictor.py
"""
v1 severity estimator — a transparent, weighted composite score, not ML
and not a single-feature threshold. Chosen because: (1) LOOCV testing
showed no ML model beat the majority-class baseline at n=13, and (2)
rainfall_pct_of_normal alone shows no monotonic relationship with real
2018 severity labels (see docs/adr/ADR-008) — likely because flood
severity in this event was also driven by dam discharge and terrain
factors not present in this dataset. A composite score across available
real signals is more defensible than an arbitrary single cutoff.
"""


def compute_risk_score(
    rainfall_pct_of_normal: float,
    no_of_landslides: int,
    rainfall_deviation_from_normal: float,
) -> float:
    """
    Weighted 0-1 composite. Weights are a documented judgment call, not
    fitted — disclosed explicitly rather than presented as learned.
    """
    rainfall_component = min(
        rainfall_pct_of_normal / 3.0, 1.0
    )  # normalize, cap at 3x normal
    landslide_component = min(
        no_of_landslides / 10.0, 1.0
    )  # normalize, cap at 10 landslides
    deviation_component = min(max(rainfall_deviation_from_normal, 0) / 3000, 1.0)

    score = (
        (0.4 * rainfall_component)
        + (0.4 * landslide_component)
        + (0.2 * deviation_component)
    )
    return round(score, 3)


def predict_severity_rule(
    rainfall_pct_of_normal: float,
    no_of_landslides: int,
    rainfall_deviation_from_normal: float,
) -> dict:
    score = compute_risk_score(
        rainfall_pct_of_normal, no_of_landslides, rainfall_deviation_from_normal
    )
    if score >= 0.7:
        severity = "Critical"
    elif score >= 0.5:
        severity = "High"
    elif score >= 0.3:
        severity = "Medium"
    else:
        severity = "Low"
    return {"severity": severity, "risk_score": score, "confidence": 1.0}
