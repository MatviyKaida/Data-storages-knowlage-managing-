# Лабораторна робота №11 — Чат-бот на основі гібридного сховища (RAG + граф)
**Предметна область:** Управління спортивними знаннями (*Domain Knowledge Hub*)  
**Виконав:** студент групи ФЕІ-42 Кайда Матвій · **Перевірив:** ас. Патинко А.М.

## Запуск з нуля
```bash
python3 -m pip install -r requirements.txt
export HUB_KEY_COACH="your-coach-key"
export HUB_KEY_DOCTOR="your-doctor-key"
uvicorn api.main:app --host 0.0.0.0 --port 8000
```
