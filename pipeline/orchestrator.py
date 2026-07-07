"""
Coordinates the full cycle: predict -> decide -> (forecast + optimize if
triggered), across all districts in one run. Each stage is independently
logged and error-handled — one district's failure doesn't kill the run.
"""

import logging
import pandas as pd

from services.decision_service import decide_action
from services.resource_service import forecast_resources
from services.priority_service import compute_priority_score

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("reliefiq.pipeline")


class PipelineOrchestrator:
    def __init__(self, predictor, optimizer, total_food_available: int = 5000):
        # predictor: anything implementing SeverityPredictor
        # optimizer: anything implementing ResourceOptimizer
        self.predictor = predictor
        self.optimizer = optimizer
        self.total_food_available = total_food_available

    def run_full_cycle(self, disasters: pd.DataFrame, infra: pd.DataFrame) -> dict:
        district_results = []
        demands, priorities, shelter_caps, transport_limits = {}, {}, {}, {}

        for _, row in disasters.iterrows():
            try:
                prediction = self.predictor.predict(row.to_dict())
            except Exception as e:
                logger.error(f"Prediction failed for {row.district_name}: {e}")
                district_results.append(
                    {"district": row.district_name, "error": str(e)}
                )
                continue

            decision = decide_action(prediction)
            logger.info(
                f"{row.district_name}: severity={prediction['severity']} -> {decision['action']}"
            )

            entry = {
                "district": row.district_name,
                "prediction": prediction,
                "decision": decision,
            }

            if decision["action"] == "RUN_OPTIMIZER":
                try:
                    forecast = forecast_resources(
                        prediction["severity"], row.population
                    )
                    infra_row = infra[infra.district_id == row.district_id].iloc[0]
                    priority = compute_priority_score(
                        risk_score=prediction["risk_score"],
                        population=row.population,
                        hospitals=infra_row.hospitals,
                        roads=infra_row.roads,
                    )
                    demands[row.district_id] = forecast["food_packets"]
                    priorities[row.district_id] = priority
                    shelter_caps[row.district_id] = infra_row.shelters * 1000
                    transport_limits[row.district_id] = infra_row.roads * 50
                    entry["forecast"] = forecast
                    entry["priority"] = priority
                except Exception as e:
                    logger.error(
                        f"Forecast/priority step failed for {row.district_name}: {e}"
                    )
                    entry["error"] = str(e)

            district_results.append(entry)

        allocation = None
        if demands:
            try:
                allocation = self.optimizer.optimize(
                    demands,
                    priorities,
                    shelter_caps,
                    transport_limits,
                    self.total_food_available,
                )
                logger.info(f"Optimization status: {allocation['status']}")
            except Exception as e:
                logger.error(f"Optimization failed: {e}")
                allocation = {"status": "ERROR", "allocation": {}}

        return {"district_results": district_results, "allocation": allocation}
