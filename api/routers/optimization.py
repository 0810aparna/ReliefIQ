import sys
sys.path.append(".")
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.base import get_db
from database.models import District, Infrastructure, DisasterHistory
from services.prediction_service import RuleBasedPredictor
from services.decision_service import decide_action
from services.resource_service import forecast_resources
from services.priority_service import compute_priority_score
from services.optimization_service import LPOptimizer

router = APIRouter()
predictor = RuleBasedPredictor()
optimizer = LPOptimizer()


@router.post("/optimize")
def optimize(total_food_available: int = 5000, db: Session = Depends(get_db)):
    demands, priorities, shelter_caps, transport_limits = {}, {}, {}, {}

    disasters = db.query(DisasterHistory).all()
    for d in disasters:
        district = db.query(District).filter(District.district_id == d.district_id).first()
        infra = db.query(Infrastructure).filter(Infrastructure.district_id == d.district_id).first()

        prediction = predictor.predict({
            "rainfall_pct_of_normal": d.rainfall_pct_of_normal,
            "no_of_landslides": d.no_of_landslides,
            "rainfall_deviation_from_normal": d.rainfall_deviation_from_normal,
        })
        decision = decide_action(prediction)

        if decision["action"] == "RUN_OPTIMIZER":
            forecast = forecast_resources(prediction["severity"], district.population)
            priority = compute_priority_score(
                risk_score=prediction["risk_score"], population=district.population,
                hospitals=infra.hospitals, roads=infra.roads,
            )
            demands[d.district_id] = forecast["food_packets"]
            priorities[d.district_id] = priority
            shelter_caps[d.district_id] = infra.shelters * 1000
            transport_limits[d.district_id] = infra.roads * 50

    if not demands:
        return {"status": "NO_ACTION", "allocation": {}}

    return optimizer.optimize(demands, priorities, shelter_caps, transport_limits, total_food_available)