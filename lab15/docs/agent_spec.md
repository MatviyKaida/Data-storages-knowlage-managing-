# Результат 1. Специфікація LLM-агента (Domain Knowledge Hub)

- **Мета:** надання тренерському та медичному штабу точних, цитованих відповідей шляхом оркестрації трьох джерел знань (векторний корпус, граф Neo4j, OLAP-куб).
- **Користувачі та ролі:** `guest` (`public`), `coach` (`public + internal`), `doctor` (`public + internal + restricted`).
- **Рівні автономності:** L2 (автономний read-only пошук і синтез із перевіркою цитат); L1 (Human-in-the-Loop для запису знань середнього/високого ризику).
- **4 інструменти (JSON-схеми в `mcp_server/server.py`):**
  1. `search_docs(query, role, top_k<=10)` — read-only, pre-filter `sensitivity`.
  2. `query_graph(entity_code, role, max_edges<=6)` — read-only, блокує медичні ребра для `coach`/`guest`.
  3. `query_olap(metric, role)` — read-only, доступ лише до затверджених метрик семантичного шару (`LIMIT 5`).
  4. `propose_fact(entity, field, value, source)` — запис через SHACL-валідацію, оцінку ризику та HITL.
- **Ліміти:** `max_steps = 5`, `max_tokens = 2000`, `timeout_sec = 10.0`, `rate_limit = 10 req/min`.
- **Заборонені дії:** прямі SQL/Cypher `DELETE`/`DROP`/`CREATE`/`MERGE`, розкриття системного промпту/API-ключів, обхід RBAC, нескінченні цикли.
- **Типи пам’яті та TTL:** робоча/сесійна (буфер діалогу, `TTL = 30 хв`), епізодична (журнал трасування `logs/agent_traces.jsonl`, `TTL = 30 днів`), семантична (граф + векторний індекс + OLAP, постійно з версіонуванням).
