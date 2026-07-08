import sys
sys.path.append(".")
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.base import get_db
from database.models import District, DisasterHistory, PredictionLog, DecisionLog
from database.schemas import PredictRequest, PredictResponse
from services.prediction_service import RuleBasedPredictor
from services.decision_service import decide_action

router = APIRouter()
predictor = RuleBasedPredictor()


@router.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest, db: Session = Depends(get_db)):
    district = db.query(District).filter(District.district_id == request.district_id).first()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")

    disaster = db.query(DisasterHistory).filter(
        DisasterHistory.district_id == request.district_id
    ).first()
    if not disaster:
        raise HTTPException(status_code=404, detail="No disaster history for this district")

    district_row = {
        "rainfall_pct_of_normal": disaster.rainfall_pct_of_normal,
        "no_of_landslides": disaster.no_of_landslides,
        "rainfall_deviation_from_normal": disaster.rainfall_deviation_from_normal,
    }
    prediction = predictor.predict(district_row)
    decision = decide_action(prediction)

    pred_log = PredictionLog(
        district_id=district.district_id, severity=prediction["severity"],
        risk_score=prediction["risk_score"], confidence=prediction["confidence"],
    )
    db.add(pred_log)
    db.commit()
    db.refresh(pred_log)

    db.add(DecisionLog(
        district_id=district.district_id, prediction_id=pred_log.prediction_id,
        action=decision["action"], alert_level=decision["alert_level"],
    ))
    db.commit()

    return PredictResponse(
        district_id=district.district_id, district_name=district.district_name,
        severity=prediction["severity"], risk_score=prediction["risk_score"],
        confidence=prediction["confidence"], decision_action=decision["action"],
        alert_level=decision["alert_level"], components=prediction["components"],
    )