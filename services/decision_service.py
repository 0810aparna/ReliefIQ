"""
Pure business logic — no ML, no optimization, fully independent and
fast to unit-test.
"""


def decide_action(prediction: dict) -> dict:
    if prediction["severity"] == "Critical":
        return {"action": "RUN_OPTIMIZER", "alert_level": "Critical"}
    elif prediction["severity"] == "High":
        return {"action": "RUN_OPTIMIZER", "alert_level": "High"}
    else:
        return {"action": "MONITOR_ONLY", "alert_level": "Low"}
