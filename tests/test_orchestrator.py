import sys

sys.path.append(".")
import pandas as pd
from pipeline.orchestrator import PipelineOrchestrator


class FakePredictor:
    """A minimal stand-in implementing the same interface as RuleBasedPredictor."""

    def predict(self, district_row: dict) -> dict:
        return {"severity": "Critical", "risk_score": 0.9, "confidence": 1.0}


class FakeOptimizer:
    """A minimal stand-in implementing the same interface as LPOptimizer."""

    def optimize(
        self, demands, priorities, shelter_caps, transport_limits, total_food_available
    ):
        return {"status": "Optimal", "allocation": {d: 100 for d in demands}}


def test_orchestrator_runs_full_cycle_with_fakes():
    disasters = pd.DataFrame(
        [
            {"district_id": 1, "district_name": "TestDistrict", "population": 100000},
        ]
    )
    infra = pd.DataFrame(
        [
            {
                "district_id": 1,
                "hospitals": 5,
                "shelters": 3,
                "roads": 100,
                "rescue_centers": 2,
            },
        ]
    )

    orchestrator = PipelineOrchestrator(
        predictor=FakePredictor(), optimizer=FakeOptimizer()
    )
    result = orchestrator.run_full_cycle(disasters, infra)

    assert result["district_results"][0]["decision"]["action"] == "RUN_OPTIMIZER"
    assert result["allocation"]["status"] == "Optimal"
    assert result["allocation"]["allocation"][1] == 100


def test_orchestrator_handles_prediction_failure_gracefully():
    class BrokenPredictor:
        def predict(self, district_row: dict) -> dict:
            raise ValueError("simulated model failure")

    disasters = pd.DataFrame(
        [{"district_id": 1, "district_name": "TestDistrict", "population": 100000}]
    )
    infra = pd.DataFrame(
        [
            {
                "district_id": 1,
                "hospitals": 5,
                "shelters": 3,
                "roads": 100,
                "rescue_centers": 2,
            }
        ]
    )

    orchestrator = PipelineOrchestrator(
        predictor=BrokenPredictor(), optimizer=FakeOptimizer()
    )
    result = orchestrator.run_full_cycle(disasters, infra)

    assert "error" in result["district_results"][0]
    assert result["allocation"] is None  # nothing to optimize since prediction failed
