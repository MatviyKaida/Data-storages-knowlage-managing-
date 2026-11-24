# Domain Knowledge Hub — ЛР №16: Рекомендаційна система та фінальний демонстратор

## Передумови
- Python 3.10+ (`numpy`, `matplotlib`, `fastapi`, `uvicorn`) або Docker / Docker Compose v2+.
- Змінні середовища: скопіюйте `.env.example` у `.env` (ключі API не зберігаються в репозиторії).
- Фіксований `SEED=42` для відтворюваності експериментів.

## Запуск однією командою
### Варіант A (Docker Compose — повний стек Neo4j + FastAPI)
```bash
docker compose up --build
```
Перевірка працездатності: `curl http://localhost:8000/health` та `curl "http://localhost:8000/recommend?query=ACWR&role=coach"`.

### Варіант B (Локальний CLI-запуск без Docker)
```bash
python3 reco/eval.py && python3 reco/explain.py && python3 app/api.py
```

## Тестові дані та структура
- `data/catalog.json` — 34 документи (30 базових + 4 холодних), теги `verified`, `updated_days_ago`, `sensitivity`.
- `data/interactions.jsonl` — 60 користувачів, 16 тижнів взаємодій (часове розбиття W1–12 train → W13–16 test).
- `reco/` — рекомендаційні алгоритми (`recommender.py`), офлайн-оцінка (`eval.py`), пояснення (`explain.py`).
- `docs/` — `reco_design.md`, `reco_eval.md`, `cold_start.md`, `demo_script.md`, **`whitepaper.pdf`**.
- `llm_log/` та `claims/claims.csv` — протокол «LLM-експерт» (топ-20 тверджень).
