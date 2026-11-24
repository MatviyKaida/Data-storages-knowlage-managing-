# Результат 5. Порівняння SPARQL (ЛР №8) vs Cypher (ЛР №9) та Text-to-Cypher

## 1. Порівняння 5 питань у SPARQL та Cypher

Для порівняння обрано 5 типових компетентнісних питань (CQ1, CQ3, CQ4, CQ7, CQ9) та виконано їх обома мовами на еквівалентних даних предметної області «Управління спортивними знаннями»:

| № | Питання | SPARQL (ЛР №8, `skm:`) | Cypher (ЛР №9, Neo4j) | Збіг результатів та пояснення розбіжностей |
| :---: | :--- | :--- | :--- | :--- |
| 1 | **CQ1:** Атлети з `ACWR > 1.30`, готовністю `< 65%` і їхні тренери | `SELECT ?code ?acwr ?rd WHERE { ?a a skm:Athlete; skm:entityCode ?code; skm:coachedBy ?c; skm:hasMetricRecord ?m. ?m skm:acwrValue ?acwr; skm:readinessScorePct ?rd. FILTER(?acwr > 1.30 && ?rd < 65) }` | `MATCH (c:Coach)<-[:COACHED_BY]-(a:Athlete)-[r:HAS_METRIC_RECORD]->(m:LoadRecoveryMetric) WHERE m.acwrValue > 1.30 AND m.readinessScorePct < 65 AND r.confidence >= 0.95 RETURN ...` | **Повний збіг (8 записів)**. У Cypher фільтрація `r.confidence >= 0.95` записується в одному реченні, тоді як у SPARQL потребує RDF-star або додаткових 3 триплетів реїфікації. |
| 2 | **CQ3:** Сумарна дистанція та кількість сесій на атлета | `SELECT ?a (COUNT(?s) AS ?cnt) (SUM(?d) AS ?tot) WHERE { ?a skm:performsSession ?s. ?s skm:totalDistanceM ?d. } GROUP BY ?a ORDER BY DESC(?tot)` | `MATCH (c:Coach)<-[:COACHED_BY]-(a:Athlete)-[:PERFORMS_SESSION]->(s:TrainingSession) WITH c, a, count(s) AS cnt, sum(s.totalDistanceM) AS tot RETURN ... ORDER BY tot DESC` | **Повний збіг (24 атлети, топ — `ATH-2026-015`, 35 130 м)**. У Cypher групування неявне за неагрегованими полями в `WITH`/`RETURN`, а в SPARQL потрібен явний `GROUP BY`. |
| 3 | **CQ4:** Лабтести з `CK > 350` або `LSI < 90` | `SELECT ?a ?l ?ck ?lsi WHERE { ?a skm:undergoesLabTest ?l. ?l skm:creatineKinaseUL ?ck; skm:lsiSymmetryPct ?lsi. FILTER(?ck > 350 || ?lsi < 90) }` | `MATCH (a:Athlete)-[r:UNDERGOES_LAB_TEST]->(l:LabTest) WHERE l.creatineKinaseUL > 350 OR l.lsiSymmetryPct < 90 RETURN ...` | **Повний збіг (10 записів, лідер — `LAB-2026-089`, CK=540, LSI=84%)**. |
| 4 | **CQ7:** Кількість зв'язків і середня достовірність по джерелах | Потребує іменованих графів `GRAPH ?g { ?x ?p ?y }` або реїфікації `rdf:Statement` + `prov:wasGeneratedBy` | `MATCH ()-[r]->() WITH r.source AS dataSource, count(r) AS cnt, round(avg(r.confidence), 3) AS avgConf RETURN ...` | **Незначна структурна розбіжність**: у RDF-сховищі ЛР №8 метадані достовірності зберігалися на рівні графа джерела, а в LPG — індивідуально на кожному ребрі, що дало точніші середні (`0.971–1.000`). |
| 5 | **CQ9:** Каскадний вплив `MC-2026-W42` до протоколів RTP (глибина 5) | 5 послідовних триплет-шаблонів із явними змінними `?s ?m ?a ?inj ?rtp` (11 рядків) | Єдиний візуальний шаблон шляху `MATCH path = (mc)<-[:PART_OF_MICROCYCLE]-(s)<-[:RECORDED_FROM_SESSION]-(m)<-[:HAS_METRIC_RECORD]-(a)-[:HAS_INJURY_DIAGNOSIS]->(inj)-[:TREATED_BY_PROTOCOL]->(rtp)` | **Повний збіг (12 унікальних шляхів впливу, 5 травмованих атлетів)**. Cypher повертає сам об'єкт `path` і його довжину `length(path) = 5` нативно. |

## 2. Порівняльна таблиця SPARQL vs Cypher (6 критеріїв)

| Критерій | SPARQL 1.1 (RDF/OWL, ЛР №8) | Cypher 5 (Neo4j LPG, ЛР №9) |
| :--- | :--- | :--- |
| **1. Читабельність** | Нижча на глибоких шляхах через велику кількість URI-префіксів і повторюваних змінних | Висока завдяки ASCII-art нотації `(a)-[:REL]->(b)`, наочній для інженерів і тренерів |
| **2. Довжина запиту** | У середньому на 30–45% довші запити (префікси `PREFIX`, явний `GROUP BY`, реїфікація) | Компактніші на 30–45%, особливо для `shortestPath`, `[*1..3]` і властивостей ребер |
| **3. Час виконання (на 120/245)** | ~8–15 мс (in-memory RDFlib / GraphDB) для простих запитів; деградує на глибоких шляхах | ~2–5 мс завдяки index-free adjacency та RANGE-індексам |
| **4. Зручність аналізу шляхів та агрегацій** | Немає нативного `shortestPath` із поверненням проміжних вузлів; property paths не повертають сам шлях | Нативні `shortestPath`, `[*1..3]`, `nodes(p)`, `relationships(p)`, конвеєр `WITH` |
| **5. Атрибути на зв'язках (Provenance)** | Потребує реїфікації, RDF-star або Named Graphs | Вбудовані властивості ребер (`source`, `confidence`, `validFrom`) без додаткових вузлів |
| **6. Обмеження та логічне виведення** | Сильна сторона — стандарти W3C, OWL/RDFS-виведення та федеративні запити (`SERVICE`), але слабша підтримка GDS | Немає вбудованого OWL-різонера (потрібні мульти-мітки), натомість потужна бібліотека GDS (PageRank, Louvain) |

## 3. Реалізація Text-to-Cypher (безпека, схема, LIMIT)

Для безпечного перетворення природномовних питань у Cypher реалізовано трирівневий захист (код перевірки у `tests/run_t2c_eval.py`, набір з 12 тестів у `tests/t2c.jsonl`):
1. **Read-only роль у Neo4j:** створено роль `t2c_reader` (`DENY WRITE ON GRAPH * TO t2c_reader`, сесія з `default_access_mode="READ"`) + regex-фільтр заборонених операторів (`CREATE`, `MERGE`, `DELETE`, `DETACH`, `SET`, `REMOVE`, `DROP`, `LOAD CSV`).
2. **Ін'єкція схеми в системну підказку та перевірка схеми:** у промпт `v2.0-text-to-cypher` (`temperature=0.0`, `seed=42`) передано повний перелік 10 міток, 10 спрямованих типів ребер і властивостей; валідатор `validate_guardrails()` перевіряє відсутність невідомих міток і витоків RDF-префіксів `skm:`.
3. **Примусовий `LIMIT 25`:** системна інструкція та валідатор вимагають наявності `LIMIT <= 25` у кожному згенерованому запиті для захисту від перевантаження пам'яті.

## 4. Метрики Text-to-Cypher (12 питань) та аналіз 3 помилок

- **Execution Accuracy (EX, частка коректних запитів):** **75.0%** (9 із 12)
- **Syntax Validity:** **91.7%** (11 із 12)
- **Schema Validity:** **83.3%** (10 із 12)
- **Середній час генерації:** **1.42 с** (діапазон 1.08–2.38 с)

### Аналіз 3 типових помилок генерації:
1. **`T2C-10` — `E1_ReversedRelationshipDirection` (інверсія напрямку ребра):** модель згенерувала `(:TrainingSession)-[:PERFORMS_SESSION]->(:Athlete)` замість `(:Athlete)-[:PERFORMS_SESSION]->(:TrainingSession)`. Запит синтаксично коректний, але повертає 0 рядків. *Зменшення ризику:* явне подання орієнтованих трійок `(SourceLabel)-[:REL]->(TargetLabel)` у системному промпті та перевірка напрямку ребер валідатором.
2. **`T2C-11` — `E2_RDFNamespacePrefixLeakage` (витік префіксу RDF):** під впливом формулювання питання модель вставила `m.\`skm:acwrValue\`` замість `m.acwrValue`. *Зменшення ризику:* правило в промпті «ніколи не використовувати префікси URI» + автоматична перевірка властивостей за списком схеми.
3. **`T2C-12` — `E3_AggregationInWhereClause` (агрегація у `WHERE` без `WITH`):** модель записала `WHERE count(a) > 4` без проміжного `WITH c, count(a) AS cnt`, що викликало `Neo.ClientError.Statement.SyntaxError`. *Зменшення ризику:* додавання few-shot прикладу патерну `WITH ... WHERE` у системну підказку та автоматичний retry на синтаксичній помилці.
