"""
v1 severity estimator — a transparent, weighted composite score, not ML
and not a single-feature threshold. See docs/adr/ADR-008 for full reasoning.
"""


def compute_risk_score(rainfall_pct_of_normal: float, no_of_landslides: int,
                        rainfall_deviation_from_normal: float) -> dict:
    rainfall_component = min(rainfall_pct_of_normal / 3.0, 1.0)
    landslide_component = min(no_of_landslides / 10.0, 1.0)
    deviation_component = min(max(rainfall_deviation_from_normal, 0) / 3000, 1.0)

    score = (0.4 * rainfall_component) + (0.4 * landslide_component) + (0.2 * deviation_component)
    return {
        "score": round(score, 3),
        "components": {
            "rainfall": round(0.4 * rainfall_component, 3),
            "landslides": round(0.4 * landslide_component, 3),
            "rainfall_deviation": round(0.2 * deviation_component, 3),
        },
    }


def predict_severity_rule(rainfall_pct_of_normal: float, no_of_landslides: int,
                           rainfall_deviation_from_normal: float) -> dict:
    result = compute_risk_score(rainfall_pct_of_normal, no_of_landslides, rainfall_deviation_from_normal)
    score = result["score"]

    if score >= 0.7:
        severity = "Critical"
    elif score >= 0.5:
        severity = "High"
    elif score >= 0.3:
        severity = "Medium"
    else:
        severity = "Low"

    return {
        "severity": severity,
        "risk_score": score,
        "confidence": 1.0,
        "components": result["components"],
    }