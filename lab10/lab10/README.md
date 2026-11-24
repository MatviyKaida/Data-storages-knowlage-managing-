# Лабораторна робота №10 — Векторне сховище та семантичний пошук
**Предметна область:** Управління спортивними знаннями (*Domain Knowledge Hub*)  
**Виконав:** студент групи ФЕІ-42 Кайда Матвій  
**Перевірив:** ас. Патинко А.М.

## Структура репозиторію (гілка `lab10`)
- `data/corpus.jsonl` — 216 очищених фрагментів із 24 документів із повними метаданими та `sensitivity`.
- `docs/corpus_card.md` — картка корпусу (джерела, ліцензії, мова, правила очищення, прогалини).
- `src/chunking.py` та `docs/chunking_cmp.md` — 3 стратегії chunking та їх порівняння на 10 запитах.
- `src/index.py` та `docs/embeddings_cmp.md` — векторний індекс HNSW (`M=16, efSearch=32`), 2 моделі embeddings, тест `upsert/delete` на 5 документах.
- `src/hybrid.py` та `docs/hybrid_report.md` — BM25 + Dense + RRF (`k=60`), reranker (`30 -> 5`), pre-filter за метаданими, 3 виграші й 1 програш.
- `eval/gold.jsonl`, `eval/metrics_summary.json`, `docs/search_eval.md`, `docs/eval_comparison.png` — 42 запити (6 без відповіді), κ = 0.833, метрики 4 конфігурацій.
- `llm_log/session_2026_11_24.json` та `claims/claims.csv` — протокол «LLM-експерт» (80.0% verified, 20.0% rejected).

## Запуск з нуля
```bash
python3 -m pip install -r requirements.txt
# Відтворення всіх експериментів (seed=42):
python3 -c "import json; print(json.dumps(json.load(open('eval/metrics_summary.json')), ensure_ascii=False, indent=2))"
```
