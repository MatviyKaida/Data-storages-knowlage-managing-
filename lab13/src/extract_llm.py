"""Метод Б: витяг знань із LLM за JSON-схемою, закритим словником, перевіркою evidence та >= 2 повторами."""
import json, os

ALLOWED_ENTITY_TYPES = {"BIOMARKER", "THRESHOLD", "DEVICE", "PROTOCOL", "INJURY", "METHOD"}
ALLOWED_REL_TYPES = {"MEASURED_BY", "HAS_THRESHOLD", "INDICATES_RISK", "TREATED_BY", "ASSOCIATED_WITH", "APPLIED_IN"}

JSON_SCHEMA = {
    "type": "object",
    "required": ["claims"],
    "properties": {
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["head", "head_type", "relation", "tail", "tail_type", "evidence"],
                "properties": {
                    "head": {"type": "string"}, "head_type": {"enum": sorted(ALLOWED_ENTITY_TYPES)},
                    "relation": {"enum": sorted(ALLOWED_REL_TYPES)},
                    "tail": {"type": "string"}, "tail_type": {"enum": sorted(ALLOWED_ENTITY_TYPES)},
                    "evidence": {"type": "string", "minLength": 10},
                },
            },
        }
    },
}

def validate_llm_output(payload: dict, source_text: str) -> tuple[bool, list[str]]:
    errors = []
    if not isinstance(payload, dict) or "claims" not in payload:
        return False, ["Відсутній ключ claims"]
    for i, c in enumerate(payload["claims"]):
        if c.get("relation") not in ALLOWED_REL_TYPES:
            errors.append(f"claim[{i}]: недозволене відношення {c.get('relation')}")
        ev = c.get("evidence", "")
        if not ev or ev[:25].lower() not in source_text.lower():
            errors.append(f"claim[{i}]: цитата evidence не підтверджена в тексті")
    return (len(errors) == 0, errors)

def extract_with_retries(doc_id: str, text: str, llm_call, max_retries: int = 2) -> list[dict]:
    last_err = []
    for attempt in range(max_retries + 1):
        raw = llm_call(doc_id, text, schema=JSON_SCHEMA, prev_errors=last_err)
        ok, errs = validate_llm_output(raw, text)
        if ok:
            return raw["claims"]
        last_err = errs
    return []

if __name__ == "__main__":
    with open("data/pred_llm.jsonl", "r", encoding="utf-8") as f:
        print("Method B predictions loaded:", sum(1 for _ in f))
