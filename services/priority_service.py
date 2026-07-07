"""
Combines risk score, population, and infrastructure into a single 0-1
priority score used to weight the optimizer's objective. Weights are a
documented judgment call (matching the same honest-disclosure approach
as the rule-based predictor), not fitted.
"""

def compute_priority_score(risk_score: float, population: int, hospitals: int, roads: int) -> float:
    pop_norm = min(population / 5_000_000, 1.0)
    hosp_norm = 1 - min(hospitals / 20, 1.0)   # fewer hospitals -> higher priority
    road_norm = 1 - min(roads / 300, 1.0)      # fewer roads -> higher priority (less accessible)

    priority = (0.5 * risk_score) + (0.25 * pop_norm) + (0.15 * hosp_norm) + (0.10 * road_norm)
    return round(priority, 3)