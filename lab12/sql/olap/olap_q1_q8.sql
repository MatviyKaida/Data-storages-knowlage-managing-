-- Q1 (ROLLUP / Drill-down по таксономії: клас -> підклас)
SELECT t.tax_class, t.tax_subclass, COUNT(*) AS sessions,
       ROUND(SUM(f.total_distance_m)/1000.0, 2) AS dist_km, ROUND(AVG(f.acwr_value), 3) AS avg_acwr
FROM fact_training_load f JOIN dim_taxonomy t ON f.tax_key = t.tax_key
GROUP BY ROLLUP (t.tax_class, t.tax_subclass)
ORDER BY dist_km DESC;

-- Q2 (CUBE / GROUPING SETS: тренер x фаза мікроциклу)
SELECT a.coach_name, m.phase_type, COUNT(*) AS sessions, SUM(f.trimp_score) AS total_trimp
FROM fact_training_load f
JOIN dim_athlete a ON f.athlete_key = a.athlete_key
JOIN dim_microcycle m ON f.mc_key = m.mc_key
GROUP BY CUBE (a.coach_name, m.phase_type)
ORDER BY total_trimp DESC;

-- Q3 (SLICE: лише ударні мікроцикли Shock)
SELECT a.coach_name, COUNT(*) AS shock_sessions, ROUND(AVG(f.acwr_value), 3) AS avg_acwr,
       ROUND(100.0 * SUM(CASE WHEN f.acwr_value > 1.30 THEN 1 ELSE 0 END) / COUNT(*), 1) AS overload_pct
FROM fact_training_load f
JOIN dim_athlete a ON f.athlete_key = a.athlete_key
JOIN dim_microcycle m ON f.mc_key = m.mc_key
WHERE m.phase_type = 'Shock'
GROUP BY a.coach_name ORDER BY overload_pct DESC;

-- Q4 (DICE: ACWR > 1.30 AND місяці 9-10 AND Швидкісно-силове)
SELECT d.month_name, t.tax_subclass, COUNT(*) AS high_risk_cnt, ROUND(AVG(f.readiness_score_pct), 1) AS avg_readiness
FROM fact_training_load f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_taxonomy t ON f.tax_key = t.tax_key
WHERE f.acwr_value > 1.30 AND d.month IN (9, 10) AND t.tax_class = 'Швидкісно-силове'
GROUP BY d.month_name, t.tax_subclass ORDER BY high_risk_cnt DESC;

-- Q5 (PIVOT: помісячна дистанція в км за класами таксономії)
SELECT d.month_name,
       ROUND(SUM(CASE WHEN t.tax_class='Швидкісно-силове' THEN f.total_distance_m ELSE 0 END)/1000.0, 1) AS speed_strength_km,
       ROUND(SUM(CASE WHEN t.tax_class='Аеробно-витривале' THEN f.total_distance_m ELSE 0 END)/1000.0, 1) AS aerobic_km,
       ROUND(SUM(CASE WHEN t.tax_class='Протокол Return-to-Play' THEN f.total_distance_m ELSE 0 END)/1000.0, 1) AS rtp_km
FROM fact_training_load f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_taxonomy t ON f.tax_key = t.tax_key
GROUP BY d.month_name ORDER BY d.month_name;

-- Q6 (Віконна: накопичувальний TRIMP по атлету)
SELECT a.athlete_code, d.full_date, f.trimp_score,
       SUM(f.trimp_score) OVER (PARTITION BY a.athlete_code ORDER BY d.full_date ROWS UNBOUNDED PRECEDING) AS cum_trimp
FROM fact_training_load f
JOIN dim_athlete a ON f.athlete_key = a.athlete_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE a.athlete_code = 'ATH-2026-001' ORDER BY d.full_date LIMIT 5;

-- Q7 (Віконна: RANK атлетів за сумарним HSR у межах тренера)
WITH agg AS (
  SELECT a.coach_name, a.athlete_code, SUM(f.hsr_distance_m) AS total_hsr
  FROM fact_training_load f JOIN dim_athlete a ON f.athlete_key = a.athlete_key
  GROUP BY a.coach_name, a.athlete_code
), ranked AS (
  SELECT coach_name, athlete_code, total_hsr, RANK() OVER (PARTITION BY coach_name ORDER BY total_hsr DESC) AS rnk
  FROM agg
)
SELECT coach_name, athlete_code, total_hsr, rnk FROM ranked WHERE rnk = 1 ORDER BY total_hsr DESC;

-- Q8 (Віконна: 7-сесійне ковзне середнє ACWR)
SELECT a.athlete_code, d.full_date, f.acwr_value,
       ROUND(AVG(f.acwr_value) OVER (PARTITION BY a.athlete_code ORDER BY d.full_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 3) AS ma7_acwr
FROM fact_training_load f
JOIN dim_athlete a ON f.athlete_key = a.athlete_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE a.athlete_code = 'ATH-2026-001' ORDER BY d.full_date DESC LIMIT 5;
