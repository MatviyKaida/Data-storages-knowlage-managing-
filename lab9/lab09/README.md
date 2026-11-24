# Лабораторна робота №9 — Графова база знань у Neo4j
**Предметна область:** Управління спортивними знаннями (Sports Knowledge Management, проєкт *Domain Knowledge Hub*)  
**Виконав:** студент групи ФЕІ-42 Кайда Матвій  
**Перевірив:** ас. Патинко А.М.

## Структура репозиторію (гілка `lab09`)
- `data/nodes.csv` — 120 вузлів (10 міток, повний набір семантичних властивостей).
- `data/relationships.csv` — 245 зв'язків (10 типів, властивості походження `source`, `confidence`, `validFrom`).
- `docs/graph_schema.png` — графова схема LPG під CQ1–CQ10.
- `docs/cq_mapping.md` — відображення 10 CQ на шаблони Cypher та порівняння з онтологією ЛР №7.
- `import/01_constraints_indexes.cypher` — 4 унікальні обмеження та 4 індекси.
- `import/02_load_csv.cypher` — ідемпотентний імпорт вузлів і зв'язків через `LOAD CSV` + `APOC MERGE`.
- `import/03_verify_import.cypher` — перевірка кількостей (120/245), provenance та приклад порушення обмеження.
- `queries/queries_q1_q10.cypher` — 10 аналітичних запитів Cypher (вкл. 2 запити аналізу впливу глибиною 4–5).
- `queries/gds_and_profile.cypher` — PageRank, Louvain (зі збереженням `pagerank`/`community`) та `PROFILE` до/після.
- `docs/cypher_results.md` — результати Q1–Q10, інтерпретації та ручна перевірка 3 запитів на підграфі.
- `docs/gds_report.md` — звіт із PageRank, Louvain та оптимізації `PROFILE`.
- `docs/sparql_vs_cypher.md` — порівняння 5 питань у SPARQL/Cypher, таблиця критеріїв, аналіз Text-to-Cypher.
- `tests/t2c.jsonl` — 12 тестових питань Text-to-Cypher (EX = 75.0%, 3 проаналізовані помилки).
- `tests/run_t2c_eval.py` — скрипт валідації guardrails (`t2c_reader`, схема, `LIMIT 25`) та обчислення метрик.
- `llm_log/session_2026_11_17.json` — журнал взаємодії з LLM-експертом.
- `claims/claims.csv` — таблиця 10 тверджень (8 verified / 2 rejected).

## Середовище та залежності
- **СУБД:** Neo4j Community / Desktop 5.24.0 + APOC Core 5.24.0 + Neo4j Graph Data Science (GDS) 2.11.0
- **Python:** 3.11+ (`neo4j==5.24.0`, `pandas==2.2.2`)
- **Параметри LLM-експерта:** `temperature=0.0`, `seed=42`, `top_p=0.95` (ключі API передаються виключно через змінну середовища `LLM_API_KEY`).

## Запуск з нуля
```bash
# 1. Запуск Neo4j 5.24 з APOC та GDS
docker run -d --name neo4j-sports-km \
  -p 7474:7474 -p 7687:7687 \
  -v $(pwd)/data:/var/lib/neo4j/import \
  -e NEO4J_AUTH=neo4j/sports_km_2026 \
  -e NEO4J_PLUGINS='["apoc", "graph-data-science"]' \
  neo4j:5.24.0

# 2. Обмеження та індекси
cypher-shell -u neo4j -p sports_km_2026 -f import/01_constraints_indexes.cypher

# 3. Ідемпотентний імпорт (повторний запуск зберігає 120 вузлів та 245 зв'язків)
cypher-shell -u neo4j -p sports_km_2026 -f import/02_load_csv.cypher
cypher-shell -u neo4j -p sports_km_2026 -f import/03_verify_import.cypher

# 4. Запити Cypher та GDS/PROFILE
cypher-shell -u neo4j -p sports_km_2026 -f queries/queries_q1_q10.cypher
cypher-shell -u neo4j -p sports_km_2026 -f queries/gds_and_profile.cypher

# 5. Оцінювання Text-to-Cypher (офлайн-валідація або живий запуск з роллю t2c_reader)
python3 tests/run_t2c_eval.py --offline-validate
```
