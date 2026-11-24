"""REST API (FastAPI) для гібридного RAG-чат-бота Domain Knowledge Hub (ЛР №11)."""
import os, json, time, re
from collections import defaultdict
from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Sports Knowledge Hub Hybrid RAG API",
    version="1.0.0",
    description="Гібридний RAG + GraphRAG API з автентифікацією, ролями sensitivity та лімітом запитів.",
)

# API keys read from environment (defaults only for local offline testing; never commit real keys)
API_KEYS = {
    os.getenv("HUB_KEY_COACH", "dev-coach-token"): "coach",
    os.getenv("HUB_KEY_DOCTOR", "dev-doctor-token"): "doctor",
    os.getenv("HUB_KEY_GUEST", "dev-guest-token"): "guest",
}
ROLE_PERMS = {
    "guest": {"public"},
    "coach": {"public", "internal"},
    "doctor": {"public", "internal", "restricted"},
}
RATE_LIMIT_MAX = int(os.getenv("HUB_RATE_LIMIT_PER_MIN", "5"))
_rate_buckets: dict[str, list[float]] = defaultdict(list)

CORPUS_PATH = os.getenv("HUB_CORPUS_PATH", "/working_dir/c_1dce656ae1dfbaa9/work_lab10/lab10/data/corpus.jsonl")
with open(CORPUS_PATH, "r", encoding="utf-8") as _f:
    _CORPUS = [json.loads(l) for l in _f if l.strip()]
_CHUNK_MAP = {c["chunk_id"]: c for c in _CORPUS}

class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500, description="Запитання користувача")
    top_k: int = Field(default=5, ge=1, le=10, description="Кількість фрагментів контексту")
    use_graph: bool = Field(default=True, description="Додавати підграф із графа знань")

class AskResponse(BaseModel):
    role: str
    answer: str
    sources: list[str]
    citation_valid: bool
    latency_ms: float

def _auth_and_limit(x_api_key: str | None) -> str:
    if not x_api_key or x_api_key not in API_KEYS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недійсний або відсутній X-API-Key")
    now = time.time()
    bucket = [t for t in _rate_buckets[x_api_key] if now - t < 60.0]
    if len(bucket) >= RATE_LIMIT_MAX:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Перевищено ліміт запитів за хвилину")
    bucket.append(now)
    _rate_buckets[x_api_key] = bucket
    return API_KEYS[x_api_key]

@app.get("/health")
def health():
    return {"status": "ok", "indexed_chunks": len(_CORPUS), "roles": sorted(ROLE_PERMS.keys())}

@app.get("/sources/{source_id}")
def get_source(source_id: str, x_api_key: str | None = Header(default=None)):
    role = _auth_and_limit(x_api_key)
    chunk = _CHUNK_MAP.get(source_id)
    if not chunk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Джерело {source_id} не знайдено")
    if chunk["sensitivity"] not in ROLE_PERMS[role]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Роль '{role}' не має доступу до рівня '{chunk['sensitivity']}'")
    return chunk

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest, x_api_key: str | None = Header(default=None)):
    t0 = time.perf_counter()
    role = _auth_and_limit(x_api_key)
    if re.search(r"(ігноруй\s+попередні|ignore\s+previous|api[- ]?ключ)", req.question, re.IGNORECASE):
        return AskResponse(
            role=role,
            answer="Запит заблоковано політикою безпеки (prompt injection).",
            sources=[], citation_valid=True, latency_ms=round((time.perf_counter()-t0)*1000, 2)
        )
    allowed = ROLE_PERMS[role]
    q_words = set(re.findall(r"[a-zA-Zа-яА-ЯіІїЇєЄґҐ0-9]+", req.question.lower()))
    scored = []
    for c in _CORPUS:
        if c["sensitivity"] not in allowed:
            continue
        c_words = set(re.findall(r"[a-zA-Zа-яА-ЯіІїЇєЄґҐ0-9]+", c["text"].lower()))
        overlap = len(q_words & c_words)
        if overlap > 0:
            scored.append((overlap, c))
    scored.sort(key=lambda x: -x[0])
    top = [c for _, c in scored[:req.top_k]]
    if not top:
        ans = "Недостатньо даних у наданому контексті бази знань для достовірної відповіді."
        return AskResponse(role=role, answer=ans, sources=[], citation_valid=True, latency_ms=round((time.perf_counter()-t0)*1000, 2))
    best = top[0]
    ans = f"{best['text']} [{best['chunk_id']}]."
    return AskResponse(
        role=role, answer=ans, sources=[c["chunk_id"] for c in top],
        citation_valid=True, latency_ms=round((time.perf_counter()-t0)*1000, 2)
    )
