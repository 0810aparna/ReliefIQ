"""
Implements SeverityPredictor by wrapping the composite rule-based score
(ADR-008). Swapping this for a real ML model later means writing a new
class with the same .predict() method — nothing else in the system changes.
"""

from services.rule_based_predictor import predict_severity_rule


class RuleBasedPredictor:
    def predict(self, district_row: dict) -> dict:
        return predict_severity_rule(
            rainfall_pct_of_normal=district_row["rainfall_pct_of_normal"],
            no_of_landslides=district_row["no_of_landslides"],
            rainfall_deviation_from_normal=district_row[
                "rainfall_deviation_from_normal"
            ],
        )
