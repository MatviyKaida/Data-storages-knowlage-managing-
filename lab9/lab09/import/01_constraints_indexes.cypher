// Крок 2. Створення 4 унікальних обмежень (Constraints) та 4 індексів (Indexes)
CREATE CONSTRAINT constr_athlete_code IF NOT EXISTS FOR (a:Athlete) REQUIRE a.entityCode IS UNIQUE;
CREATE CONSTRAINT constr_session_code IF NOT EXISTS FOR (s:TrainingSession) REQUIRE s.entityCode IS UNIQUE;
CREATE CONSTRAINT constr_metric_code IF NOT EXISTS FOR (m:LoadRecoveryMetric) REQUIRE m.entityCode IS UNIQUE;
CREATE CONSTRAINT constr_sensor_code IF NOT EXISTS FOR (sn:BiometricSensor) REQUIRE sn.entityCode IS UNIQUE;

CREATE INDEX idx_metric_acwr_readiness IF NOT EXISTS FOR (m:LoadRecoveryMetric) ON (m.acwrValue, m.readinessScorePct);
CREATE INDEX idx_athlete_name IF NOT EXISTS FOR (a:Athlete) ON (a.name);
CREATE INDEX idx_session_date IF NOT EXISTS FOR (s:TrainingSession) ON (s.sessionDate);
CREATE INDEX idx_lab_ck IF NOT EXISTS FOR (l:LabTest) ON (l.creatineKinaseUL);

SHOW CONSTRAINTS;
SHOW INDEXES;
