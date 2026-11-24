"""Інструмент propose_fact із SHACL-валідацією, класифікацією ризику (low/medium/high) та Human-in-the-Loop."""
import json

def classify_risk(field: str) -> str:
    if field in ("sensor_alias", "ui_label"): return "low"
    if field in ("planned_trimp_limit", "microcycle_note"): return "medium"
    return "high"

def propose_fact(fact_id: str, entity: str, field: str, value, source: str, human_decision: str | None = None, reviewer: str = "") -> dict:
    if not entity or not source:
        raise ValueError("SHACL Validation Failed: обов'язкові поля entity та source")
    risk = classify_risk(field)
    if risk == "low":
        status, reviewer = "AUTO_APPROVED", "auto_policy"
    else:
        if human_decision not in ("approve", "reject"):
            return {"fact_id": fact_id, "risk_level": risk, "status": "PENDING_HUMAN_APPROVAL"}
        status = "HUMAN_APPROVED" if human_decision == "approve" else "HUMAN_REJECTED"
    return {
        "fact_id": fact_id, "entity": entity, "field": field, "proposed_value": value,
        "source": source, "risk_level": risk, "status": status, "reviewer": reviewer,
    }
