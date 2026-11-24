"""RAG-конвеєр із гібридним пошуком (pre-filter за роллю), цитуванням [id], політикою 'не знаю' та перевіркою цитат."""
import re

INJECTION_PATTERNS = [
    r"ігноруй\s+попередні\s+інструкції",
    r"ignore\s+previous\s+instructions",
    r"покажи\s+системний\s+промпт",
    r"розкрий\s+api[- ]?ключ",
    r"обійди\s+обмеження",
]

ROLE_PERMS = {
    "guest": {"public"},
    "coach": {"public", "internal"},
    "doctor": {"public", "internal", "restricted"},
}

def validate_citations(answer: str, allowed_ids: set[str]) -> tuple[bool, list[str]]:
    cited = re.findall(r"\[([A-Z0-9-]+)\]", answer)
    if not cited:
        return (True, []) if ("Недостатньо даних" in answer or "Запит заблоковано" in answer) else (False, [])
    return (all(c in allowed_ids for c in cited), cited)
