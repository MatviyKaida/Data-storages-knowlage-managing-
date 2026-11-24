# Результат 3. REST API (FastAPI + OpenAPI + RBAC + Rate Limit)

- **Ендпоінти (`api/main.py`, схема `docs/openapi.json`):**
  1. `GET /health` — статус сервісу та кількість проіндексованих фрагментів (`200 OK`).
  2. `POST /ask` — запитання (Pydantic-валідація `min_length=3, max_length=500`, `top_k: 1..10`) → відповідь, джерела, валідність цитат, затримка.
  3. `GET /sources/{id}` — отримання першоджерела за ID з перевіркою прав `sensitivity`.
- **Автентифікація й ролі:** заголовок `X-API-Key` (ключі через змінні середовища `HUB_KEY_COACH`, `HUB_KEY_DOCTOR`, `HUB_KEY_GUEST`). Роль `coach` бачить `public + internal` (отримує `403 Forbidden` на `restricted`-джерело `CH-0028`), роль `doctor` бачить усі рівні включно з `restricted` (`200 OK`).
- **Перевірені коди помилок (FastAPI `TestClient`):** `200 OK`, `401 Unauthorized` (без ключа), `403 Forbidden` (брак прав), `404 Not Found`, `422 Unprocessable Entity` (коротка строка `"ab"`), `429 Too Many Requests` (6-й запит за хвилину при ліміті 5).

## Приклади запитів `curl`
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/ask -H "X-API-Key: $HUB_KEY_DOCTOR" -H "Content-Type: application/json" \
  -d '{"question": "Який поріг креатинкінази КФК?", "top_k": 5, "use_graph": true}'
curl -H "X-API-Key: $HUB_KEY_COACH" http://localhost:8000/sources/CH-0028  # -> 403 Forbidden
```
