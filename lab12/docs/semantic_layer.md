# Результат 4. Семантичний шар (`semantic/metrics.yml`)

Описано 5 затверджених метрик (`total_distance_km`, `avg_acwr`, `overload_rate_pct`, `avg_readiness_pct`, `total_trimp`) із повними метаданими (власники, формули, одиниці, обмеження, `review_date: 2026-11-24`, `status: approved`). Функція `compile_metric_sql()` (`semantic/compiler.py`) автоматично генерує SQL із потрібними `JOIN`. Перевірка узгодженості на 2 питаннях (`total_distance_km` по класу таксономії та `overload_rate_pct` у фазі `Shock` по тренерах) показала **100% збіг** із прямими OLAP-запитами.
