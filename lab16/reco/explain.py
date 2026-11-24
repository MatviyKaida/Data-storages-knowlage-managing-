"""Генерація пояснень рекомендацій зі шляху графа та автоматична перевірка сутностей."""
import re

ENTITY_RE = re.compile(r"\b(U-\d{3}|DOC-(?:NEW-)?\d{2}|PROTOCOL-[A-Z]+|MC-2026-W\d+|KPI-[A-Z]+|METRIC-[A-Z]+|SLEEP-IDX|LAB-[A-Z]+|PANEL-BLOOD|RTP-ACL-P\d|ATH-2026-\d{3}|SENS-CAT-\d{2}|LOAD-SPRINT|WADA-2026|TUE-FORM|MED-CLEAR|TAG-[A-Z]+-\d|ROLE:[a-z]+|TOPIC:[A-Z]+|FALLBACK:POPULAR)\b")

def explain_from_path(path_tuple):
    u_id, src, via, tgt = path_tuple
    if src.startswith("ROLE:"):
        return f"Рекомендовано {tgt} для нового користувача {u_id} ({src}) через профільний напрям {via}."
    return f"Рекомендовано {tgt} для {u_id}, оскільки ви раніше переглядали {src}, пов’язаний через сутність {via}."

def verify_explanation(text, path_tuple):
    allowed = set(path_tuple)
    found = set(ENTITY_RE.findall(text))
    ungrounded = sorted(found - allowed)
    return (len(ungrounded) == 0 and len(found) >= 2), sorted(found), ungrounded

if __name__ == "__main__":
    p = ("U-001", "DOC-01", "PROTOCOL-ACWR", "DOC-02")
    txt = explain_from_path(p)
    ok, found, bad = verify_explanation(txt, p)
    print("Valid explanation:", ok, "|", txt)
    ok2, _, bad2 = verify_explanation(txt + " Додатково WADA-2026.", p)
    print("Hallucination caught:", (not ok2), "| ungrounded:", bad2)
