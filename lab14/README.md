# Лабораторна робота №14 — Якість, очищення та оцінювання сховища знань
**Предметна область:** Управління спортивними знаннями (*Domain Knowledge Hub*)  
**Виконав:** студент групи ФЕІ-42 Кайда Матвій · **Перевірив:** ас. Патинко А.М.

## Запуск з нуля (`seed=42`)
```bash
python3 -m pip install -r requirements.txt
pytest quality/tests/ -v
python3 quality/ci_gate.py
```
