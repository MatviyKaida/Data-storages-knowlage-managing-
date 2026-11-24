// =========================================================================
// Результат 4. Графова аналітика (Neo4j GDS 2.11): PageRank, Louvain, PROFILE
// =========================================================================

// 1. Проєкція графа для спрямованого PageRank
CALL gds.graph.project(
  'sports_km_directed',
  ['Athlete', 'Coach', 'TrainingSession', 'SpeedStrengthSession', 'TrainingMicrocycle',
   'BiometricSensor', 'LoadRecoveryMetric', 'LabTest', 'SportsInjury',
   'ReturnToPlayProtocol', 'SportsDoctor'],
  '*'
);

// 2. Виконання PageRank (Top-10) та збереження властивості pagerank у графі
CALL gds.pageRank.stream('sports_km_directed', {dampingFactor: 0.85, maxIterations: 20})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).entityCode AS entityCode,
       labels(gds.util.asNode(nodeId))[0] AS label,
       gds.util.asNode(nodeId).name AS name,
       round(score, 4) AS pagerank
ORDER BY pagerank DESC LIMIT 10;

CALL gds.pageRank.write('sports_km_directed', {
  dampingFactor: 0.85,
  maxIterations: 20,
  writeProperty: 'pagerank'
}) YIELD nodePropertiesWritten, ranIterations;

// 3. Неорієнтована проєкція для алгоритму Louvain
CALL gds.graph.project(
  'sports_km_undirected',
  ['Athlete', 'Coach', 'TrainingSession', 'SpeedStrengthSession', 'TrainingMicrocycle',
   'BiometricSensor', 'LoadRecoveryMetric', 'LabTest', 'SportsInjury',
   'ReturnToPlayProtocol', 'SportsDoctor'],
  {ALL_RELS: {type: '*', orientation: 'UNDIRECTED'}}
);

// 4. Виконання Louvain та збереження властивості community у графі
CALL gds.louvain.stream('sports_km_undirected', {randomSeed: 42})
YIELD nodeId, communityId
RETURN communityId, count(*) AS size,
       collect(gds.util.asNode(nodeId).entityCode)[0..5] AS sampleNodes
ORDER BY size DESC;

CALL gds.louvain.write('sports_km_undirected', {
  randomSeed: 42,
  writeProperty: 'community'
}) YIELD communityCount, modularity, nodePropertiesWritten;

// Перевірка збережених властивостей у графі
MATCH (n)
WHERE n.pagerank IS NOT NULL AND n.community IS NOT NULL
RETURN count(n) AS enrichedNodes, round(max(n.pagerank), 4) AS maxPR, count(DISTINCT n.community) AS communities;

// 5. PROFILE для 2 запитів (Q1 і Q4) + оптимізація Q1 (до/після)
// 5.1. Q1 ДО оптимізації (без композитного індексу, фільтрація після розширення до Coach)
DROP INDEX idx_metric_acwr_readiness IF EXISTS;
PROFILE
MATCH (c:Coach)<-[:COACHED_BY]-(a:Athlete)-[r:HAS_METRIC_RECORD]->(m:LoadRecoveryMetric)
WHERE m.acwrValue > 1.30 AND m.readinessScorePct < 65 AND r.confidence >= 0.95
RETURN a.entityCode, c.name, m.acwrValue, m.readinessScorePct
ORDER BY m.acwrValue DESC;

// 5.2. Q1 ПІСЛЯ оптимізації (композитний RANGE-індекс + переписування: старт від m:LoadRecoveryMetric)
CREATE INDEX idx_metric_acwr_readiness IF NOT EXISTS FOR (m:LoadRecoveryMetric) ON (m.acwrValue, m.readinessScorePct);
PROFILE
MATCH (m:LoadRecoveryMetric)
WHERE m.acwrValue > 1.30 AND m.readinessScorePct < 65
MATCH (a:Athlete)-[r:HAS_METRIC_RECORD]->(m)
WHERE r.confidence >= 0.95
MATCH (a)-[:COACHED_BY]->(c:Coach)
RETURN a.entityCode, c.name, m.acwrValue, m.readinessScorePct
ORDER BY m.acwrValue DESC;

// 5.3. PROFILE для Q4 (з індексом idx_lab_ck)
PROFILE
MATCH (a:Athlete)-[r:UNDERGOES_LAB_TEST]->(l:LabTest)
WHERE l.creatineKinaseUL > 350 OR l.lsiSymmetryPct < 90
RETURN a.entityCode, l.entityCode, l.creatineKinaseUL, l.lsiSymmetryPct
ORDER BY l.creatineKinaseUL DESC;
