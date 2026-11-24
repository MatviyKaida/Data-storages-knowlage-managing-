"""Метод А: витяг сутностей і відношень правилами, словниками та регулярними виразами (NER/Regex)."""
import json, re

THRESH_RE = re.compile(r"(?:>=|>|<)\s*\d+(?:\.\d+)?(?:\s*(?:%|Од/л|уд/хв|балів|ммоль/л))?")

def extract_from_text(doc_id: str, text: str, lexicon: list[tuple]) -> list[dict]:
    found = []
    for canon, etype, aliases in lexicon:
        for al in aliases:
            m = re.search(re.escape(al), text, re.IGNORECASE)
            if m:
                found.append((m.start(), m.end(), canon, etype))
                break
    for m in THRESH_RE.finditer(text):
        found.append((m.start(), m.end(), f"THRESH:{m.group(0).strip()}", "THRESHOLD"))
    claims = []
    for h in found:
        if h[3] != "BIOMARKER": continue
        for t in found:
            if t[3] in ("THRESHOLD", "DEVICE"):
                rel = "HAS_THRESHOLD" if t[3] == "THRESHOLD" else "MEASURED_BY"
                s_pos, e_pos = min(h[0], t[0]), max(h[1], t[1])
                claims.append({
                    "doc_id": doc_id, "head": h[2], "relation": rel, "tail": t[2],
                    "offset_start": s_pos, "offset_end": e_pos,
                    "evidence": text[max(0, s_pos-20):min(len(text), e_pos+20)],
                    "model": "rules_regex_v1.2", "prompt_version": "n/a", "confidence": 0.90,
                })
    return claims

if __name__ == "__main__":
    with open("data/pred_rules.jsonl", "r", encoding="utf-8") as f:
        print("Method A predictions loaded:", sum(1 for _ in f))
