"""Захисти агента: ізоляція контексту, фільтр прямих/непрямих ін'єкцій, RBAC, ліміт кроків та перевірка tool poisoning."""
import re

DIRECT_INJ = re.compile(r"(ігноруй\s+попередні|ignore\s+previous|системний\s+промпт|api[- ]?ключ|обійди\s+обмеження)", re.IGNORECASE)
INDIRECT_INJ = re.compile(r"(SYSTEM_OVERRIDE|IGNORE\s+ALL\s+RULES|EXFILTRATE|NEW\s+INSTRUCTION:)", re.IGNORECASE)
WRITE_KW = re.compile(r"\b(DELETE|DROP|CREATE|MERGE|UPDATE|INSERT|SET|REMOVE|DETACH|ALTER)\b", re.IGNORECASE)
ROLE_PERMS = {"guest": {"public"}, "coach": {"public", "internal"}, "doctor": {"public", "internal", "restricted"}}

def guard_request(query: str, role: str, tool_desc: str = "", retrieved_texts: list[str] | None = None, step: int = 1, max_steps: int = 5):
    if step > max_steps: return False, "BLOCKED_LOOP_LIMIT"
    if DIRECT_INJ.search(query): return False, "BLOCKED_DIRECT_INJECTION"
    if WRITE_KW.search(query): return False, "BLOCKED_WRITE_ATTEMPT"
    if tool_desc and INDIRECT_INJ.search(tool_desc): return False, "BLOCKED_TOOL_POISONING"
    if role != "doctor" and any(k in query.lower() for k in ["wada", "restricted", "чужі медичні", "кфк атлета"]):
        return False, "BLOCKED_RBAC_LEAK"
    for t in (retrieved_texts or []):
        if INDIRECT_INJ.search(t): return False, "BLOCKED_INDIRECT_INJECTION"
    return True, "ALLOWED"
