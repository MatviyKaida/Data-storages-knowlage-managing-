-- Зіркова схема OLAP-куба «Управління спортивними знаннями» (DuckDB SQL)
CREATE TABLE IF NOT EXISTS dim_date (
  date_key INTEGER PRIMARY KEY,
  full_date DATE NOT NULL,
  year INTEGER NOT NULL,
  quarter VARCHAR NOT NULL,
  month INTEGER NOT NULL,
  month_name VARCHAR NOT NULL,
  iso_week INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_athlete (
  athlete_key INTEGER PRIMARY KEY,
  athlete_code VARCHAR NOT NULL,
  athlete_name VARCHAR NOT NULL,
  specialization VARCHAR NOT NULL,
  coach_name VARCHAR NOT NULL,
  valid_from DATE NOT NULL,
  valid_to DATE NOT NULL,
  is_current INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_taxonomy (
  tax_key INTEGER PRIMARY KEY,
  tax_iri VARCHAR NOT NULL UNIQUE,
  tax_domain VARCHAR NOT NULL,
  tax_class VARCHAR NOT NULL,
  tax_subclass VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_sensor (
  sensor_key INTEGER PRIMARY KEY,
  sensor_code VARCHAR NOT NULL UNIQUE,
  vendor VARCHAR NOT NULL,
  sensor_type VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_microcycle (
  mc_key INTEGER PRIMARY KEY,
  mc_code VARCHAR NOT NULL UNIQUE,
  mesocycle VARCHAR NOT NULL,
  phase_type VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_training_load (
  fact_id INTEGER PRIMARY KEY,
  date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
  athlete_key INTEGER NOT NULL REFERENCES dim_athlete(athlete_key),
  tax_key INTEGER NOT NULL REFERENCES dim_taxonomy(tax_key),
  sensor_key INTEGER NOT NULL REFERENCES dim_sensor(sensor_key),
  mc_key INTEGER NOT NULL REFERENCES dim_microcycle(mc_key),
  total_distance_m INTEGER NOT NULL,
  hsr_distance_m INTEGER NOT NULL,
  duration_min INTEGER NOT NULL,
  trimp_score INTEGER NOT NULL,
  readiness_score_pct INTEGER NOT NULL,
  rmssd_morning_ms DOUBLE NOT NULL,
  acwr_value DOUBLE NOT NULL,
  rpe_score DOUBLE NOT NULL
);
