# Результат 2. Звіт про завантаження даних (ELT) та якість (DQ)

- **Версія датасету:** `v1.0.0` (детермінований генератор `seed = 42`, формат Apache Parquet Snappy, PyArrow 26.0.0).
- **Обсяг:** `fact_training_load.parquet` — **1 200 рядків**; 5 файлів вимірів (`dim_date`: 90, `dim_athlete`: 24, `dim_taxonomy`: 6, `dim_sensor`: 4, `dim_microcycle`: 12).
- **Перевірка «сиріт»:** 0 порушень по всіх 5 зовнішніх ключах (`date_key`, `athlete_key`, `tax_key`, `sensor_key`, `mc_key`).
- **6 перевірок якості (усі 0 порушень):** `NOT NULL` ключів і мір, унікальність `fact_id`, `ACWR ∈ [0.5, 2.5]`, `Readiness ∈ [0, 100]`, `RPE ∈ [1, 10]`, `HSR <= Total Distance`.
