# Результат 1. Графова схема під компетентнісні питання (CQ1–CQ10)

**Предметна область:** Управління спортивними знаннями (*Domain Knowledge Hub*)  
**Діаграма схеми:** `docs/graph_schema.png`

## 1. Мітки вузлів (10 міток) та типи зв'язків (10 типів)

- **Мітки вузлів (10):** `:Athlete` (24), `:TrainingSession` (32, з них 17 з мульти-міткою `:SpeedStrengthSession`), `:SpeedStrengthSession` (17), `:BiometricSensor` (16), `:LoadRecoveryMetric` (16), `:TrainingMicrocycle` (8), `:LabTest` (8), `:SportsInjury` (5), `:Coach` (4), `:ReturnToPlayProtocol` (4), `:SportsDoctor` (3). Разом: **120 вузлів**.
- **Типи зв'язків (10):** `PERFORMS_SESSION` (64), `PART_OF_MICROCYCLE` (32), `RECORDED_FROM_SESSION` (32), `HAS_METRIC_RECORD` (32), `COACHED_BY` (24), `USES_SENSOR` (24), `UNDERGOES_LAB_TEST` (16), `HAS_INJURY_DIAGNOSIS` (9), `TREATED_BY_PROTOCOL` (6), `SUPERVISED_BY_DOCTOR` (6). Разом: **245 зв'язків**.

## 2. Властивості походження (Provenance) на всіх зв'язках

Кожне з 245 ребер графа містить три обов'язкові властивості походження:
- `source` (`String`) — ідентифікатор первинного джерела (`Catapult_OpenField_API`, `AMS_Planner_v2`, `Hardware_Registry`, `LNU_Sports_Roster`, `LNU_SportsMed_EHR`, `LNU_Biochem_Lab`).
- `confidence` (`Float`, діапазон `[0.95; 1.00]`) — оцінка достовірності факту.
- `validFrom` (`Date`, ISO-8601) — дата набрання чинності зв'язком.

## 3. Відображення 10 компетентнісних питань (CQ1–CQ10) на шаблони шляхів Cypher

| ID | Компетентнісне питання (CQ) | Шаблон Cypher-шляху |
| :--- | :--- | :--- |
| **CQ1** | Які атлети перебувають у зоні гострого перевантаження (`ACWR > 1.30`, готовність `< 65%`) і хто їх тренує? | `(c:Coach)<-[:COACHED_BY]-(a:Athlete)-[r:HAS_METRIC_RECORD]->(m:LoadRecoveryMetric)` |
| **CQ2** | Який повний профіль моніторингу кожного атлета (сенсор, наявність травм OSICS, протокол RTP)? | `(a:Athlete) OPTIONAL MATCH (a)-[:USES_SENSOR]->(sn:BiometricSensor) OPTIONAL MATCH (a)-[:HAS_INJURY_DIAGNOSIS]->(inj:SportsInjury)-[:TREATED_BY_PROTOCOL]->(rtp:ReturnToPlayProtocol)` |
| **CQ3** | Який сумарний обсяг дистанції, високошвидкісного бігу (HSR) та середнє RPE виконали атлети по тренерах? | `(c:Coach)<-[:COACHED_BY]-(a:Athlete)-[:PERFORMS_SESSION]->(s:TrainingSession)` |
| **CQ4** | У яких атлетів виявлено підвищену креатинкіназу (`CK > 350 Од/л`) або асиметрію кінцівок (`LSI < 90%`)? | `(a:Athlete)-[r:UNDERGOES_LAB_TEST]->(l:LabTest)` |
| **CQ5** | Який найкоротший шлях організаційної координації між двома атлетами (`ATH-2026-014` та `ATH-2026-015`)? | `shortestPath((a1:Athlete)-[*..4]-(a2:Athlete))` |
| **CQ6** | Які мікроцикли, протоколи RTP та лікарі досяжні від атлета `ATH-2026-014` на відстані 1–3 переходів? | `(a:Athlete {entityCode:'ATH-2026-014'})-[*1..3]->(target)` |
| **CQ7** | Яка кількість зв'язків, середня достовірність і найраніша дата фіксації для кожного джерела даних? | `()-[r]->()` з групуванням за `r.source` |
| **CQ8** | Які тренувальні мікроцикли мають середній індекс навантаження `meanAcwr > 1.25`? | `(mc:TrainingMicrocycle)<-[:PART_OF_MICROCYCLE]-(s:TrainingSession)<-[:RECORDED_FROM_SESSION]-(m:LoadRecoveryMetric)<-[:HAS_METRIC_RECORD]-(a:Athlete)` |
| **CQ9** | Який каскадний вплив ударного мікроциклу `MC-2026-W42` на перевантаження атлетів, травми та протоколи RTP (глибина 5)? | `(mc:TrainingMicrocycle)<-[:PART_OF_MICROCYCLE]-(s)<-[:RECORDED_FROM_SESSION]-(m)<-[:HAS_METRIC_RECORD]-(a)-[:HAS_INJURY_DIAGNOSIS]->(inj)-[:TREATED_BY_PROTOCOL]->(rtp)` |
| **CQ10** | На тренувальні плани яких тренерів впливають рішення спортивного лікаря `MED-03` (глибина 4)? | `(doc:SportsDoctor)<-[:SUPERVISED_BY_DOCTOR]-(rtp)<-[:TREATED_BY_PROTOCOL]-(inj)<-[:HAS_INJURY_DIAGNOSIS]-(a)-[:COACHED_BY]->(c:Coach)` |

## 4. Порівняння зі схемою онтології ЛР №7 (RDFS/OWL -> Neo4j LPG)

| Елемент онтології ЛР №7 (RDFS/OWL) | Відображення у Neo4j LPG (ЛР №9) | Обґрунтування трансформації |
| :--- | :--- | :--- |
| Класи верхнього рівня (`skm:Athlete`, `skm:Coach`, `skm:SportsDoctor`, `skm:LabTest` тощо) | Мітки вузлів (`:Athlete`, `:Coach`, `:SportsDoctor`, `:LabTest` — 10 міток) | Пряме індексування за мітками та лаконічний синтаксис шаблонів Cypher |
| Ієрархія підкласів `skm:SpeedStrengthSession rdfs:subClassOf skm:TrainingSession` | Мульти-мітка `:TrainingSession:SpeedStrengthSession` | Дозволяє виконувати запити як до базового класу сесій, так і до вузької спеціалізації без RDFS-виведення |
| Об'єктні властивості (`owl:ObjectProperty`, напр. `skm:performsSession`, `skm:coachedBy`) | Спрямовані типи зв'язків (`[:PERFORMS_SESSION]`, `[:COACHED_BY]` — 10 типів) | Уніфікований `UPPER_SNAKE_CASE` формат ребер, оптимізований під index-free adjacency |
| Властивості даних (`owl:DatatypeProperty`, напр. `skm:acwrValue`, `skm:creatineKinaseUL`) | Типізовані властивості вузлів (`Float`, `Integer`, `Date`, `String`) | Зберігаються всередині вузлів без створення окремих літеральних триплетів |
| Реїфікація походження (`rdf:Statement`, `prov:wasGeneratedBy`, `prov:generatedAtTime`) | Властивості безпосередньо на ребрах (`source`, `confidence`, `validFrom`) | Усуває вибух кількості допоміжних вузлів (blank nodes) і спрощує фільтрацію достовірності |
| Допоміжні класи-значення (`skm:SeverityGrade`, `skm:MicrocycleType`, `skm:RehabPhase`) | Властивості вузлів (`extraInfo`, `roleOrType`, `osicsCode`) | Уникнення надлишкових переходів у графі для простих категоріальних переліків |
| Індивіди ABox (`skm:ATH-2026-014` тощо) та префікси URI | Властивість `entityCode` з унікальним обмеженням `IS UNIQUE` | Короткі ідентифікатори без префіксів URI забезпечують швидкий індексний пошук |
