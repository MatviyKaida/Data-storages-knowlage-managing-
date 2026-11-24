// Q1 (CQ1): Атлети у зоні гострого перевантаження (MATCH + WHERE + WITH + обчислення дельти rMSSD)
MATCH (c:Coach)<-[:COACHED_BY]-(a:Athlete)-[r:HAS_METRIC_RECORD]->(m:LoadRecoveryMetric)
WHERE m.acwrValue > 1.30 AND m.readinessScorePct < 65 AND r.confidence >= 0.95
WITH a, c, m, round((1.0 - m.rmssdMorningMs / a.rmssdBaseMs) * 100, 1) AS hrvDropPct
RETURN a.entityCode AS athleteCode, a.name AS athleteName, c.name AS coachName,
       m.acwrValue AS acwr, hrvDropPct, m.readinessScorePct AS readinessPct
ORDER BY acwr DESC;

// Q2 (CQ2): Повний профіль моніторингу атлетів з необов'язковими травмами та RTP (OPTIONAL MATCH)
MATCH (a:Athlete)
OPTIONAL MATCH (a)-[:USES_SENSOR]->(sn:BiometricSensor)
OPTIONAL MATCH (a)-[:HAS_INJURY_DIAGNOSIS]->(inj:SportsInjury)-[:TREATED_BY_PROTOCOL]->(rtp:ReturnToPlayProtocol)
RETURN a.entityCode AS code, a.name AS name, sn.entityCode AS sensor,
       coalesce(inj.osicsCode, 'Без травм') AS injuryCode,
       coalesce(rtp.entityCode, 'Загальна група') AS protocol, rtp.maxAllowedHrBpm AS maxHr
ORDER BY a.entityCode LIMIT 10;

// Q3 (CQ3): Агрегація тренувального обсягу та високошвидкісної роботи по тренерах (GROUP BY / COUNT / SUM / AVG)
MATCH (c:Coach)<-[:COACHED_BY]-(a:Athlete)-[:PERFORMS_SESSION]->(s:TrainingSession)
WITH c, a, count(s) AS sessionsCount, sum(s.totalDistanceM) AS totalDistM,
     sum(s.hsrDistanceM) AS totalHsrM, round(avg(s.rpeScore), 2) AS avgRpe
RETURN c.name AS coach, a.entityCode AS athleteCode, a.name AS athlete,
       sessionsCount, totalDistM, totalHsrM, avgRpe
ORDER BY totalDistM DESC;

// Q4 (CQ4): Виявлення біохімічного м'язового пошкодження та нервово-м'язової асиметрії (WHERE OR)
MATCH (a:Athlete)-[r:UNDERGOES_LAB_TEST]->(l:LabTest)
WHERE l.creatineKinaseUL > 350 OR l.lsiSymmetryPct < 90
RETURN a.entityCode AS code, a.name AS athlete, l.entityCode AS labTest,
       l.creatineKinaseUL AS ckLevelUL, l.lsiSymmetryPct AS lsiPct, r.source AS labSource
ORDER BY ckLevelUL DESC;

// Q5 (CQ5): Пошук найкоротшого шляху координації між двома атлетами у графі (shortestPath)
MATCH (a1:Athlete {entityCode: 'ATH-2026-014'}), (a2:Athlete {entityCode: 'ATH-2026-015'}),
      p = shortestPath((a1)-[*..4]-(a2))
RETURN [n IN nodes(p) | coalesce(n.entityCode, n.name)] AS pathNodes,
       [r IN relationships(p) | type(r)] AS pathRels, length(p) AS hops;

// Q6 (CQ6): Обхід шляхів змінної довжини (*1..3) від атлета до медичного та тренувального оточення
MATCH p = (a:Athlete {entityCode: 'ATH-2026-014'})-[*1..3]->(target)
WHERE any(lbl IN labels(target) WHERE lbl IN ['TrainingMicrocycle', 'ReturnToPlayProtocol', 'SportsDoctor'])
RETURN labels(target)[0] AS targetType, target.entityCode AS targetCode,
       length(p) AS pathLength, [r IN relationships(p) | type(r)] AS relChain
ORDER BY pathLength ASC;

// Q7 (CQ7): Аналіз достовірності джерел даних (Provenance filtering & aggregation)
MATCH ()-[r]->()
WITH r.source AS dataSource, collect(DISTINCT type(r)) AS coveredRelations,
     count(r) AS relCount, round(avg(r.confidence), 3) AS avgConfidence,
     min(r.validFrom) AS earliestRecord
RETURN dataSource, coveredRelations, relCount, avgConfidence, earliestRecord
ORDER BY relCount DESC;

// Q8 (CQ8): Багатоетапна конвеєрна фільтрація мікроциклів із перевищенням порогу ACWR (WITH + HAVING pattern)
MATCH (mc:TrainingMicrocycle)<-[:PART_OF_MICROCYCLE]-(s:TrainingSession)<-[:RECORDED_FROM_SESSION]-(m:LoadRecoveryMetric)<-[:HAS_METRIC_RECORD]-(a:Athlete)
WITH mc, count(DISTINCT s) AS sessionCnt, count(DISTINCT a) AS athletesAffected,
     round(avg(m.acwrValue), 2) AS meanAcwr, max(m.acwrValue) AS peakAcwr
WHERE meanAcwr > 1.25
RETURN mc.entityCode AS microcycle, mc.roleOrType AS cycleType, mc.plannedTrimp AS trimp,
       sessionCnt, athletesAffected, meanAcwr, peakAcwr
ORDER BY meanAcwr DESC;

// Q9 (CQ9 — Аналіз впливу №1, глибина 5): Каскадний вплив ударного мікроциклу MC-2026-W42 до протоколів RTP
MATCH path = (mc:TrainingMicrocycle {entityCode: 'MC-2026-W42'})<-[:PART_OF_MICROCYCLE]-(s:TrainingSession)
  <-[:RECORDED_FROM_SESSION]-(m:LoadRecoveryMetric)<-[:HAS_METRIC_RECORD]-(a:Athlete)
  -[:HAS_INJURY_DIAGNOSIS]->(inj:SportsInjury)-[:TREATED_BY_PROTOCOL]->(rtp:ReturnToPlayProtocol)
RETURN DISTINCT mc.entityCode AS rootMicrocycle, a.entityCode AS impactedAthlete,
       length(path) AS dependencyDepth, m.acwrValue AS acwrTrigger,
       inj.osicsCode AS injuryOsics, rtp.entityCode AS assignedProtocol, rtp.maxAllowedHrBpm AS maxHrCap
ORDER BY acwrTrigger DESC;

// Q10 (CQ10 — Аналіз впливу №2, глибина 4): Зворотний ланцюг впливу рішень спортивного лікаря на плани тренерів
MATCH path = (doc:SportsDoctor {entityCode: 'MED-03'})<-[:SUPERVISED_BY_DOCTOR]-(rtp:ReturnToPlayProtocol)
  <-[:TREATED_BY_PROTOCOL]-(inj:SportsInjury)<-[:HAS_INJURY_DIAGNOSIS]-(a:Athlete)-[:COACHED_BY]->(c:Coach)
RETURN doc.name AS supervisingDoctor, rtp.entityCode AS protocol, a.entityCode AS athlete,
       c.name AS affectedCoach, length(path) AS impactDepth,
       [n IN nodes(path) | n.entityCode] AS dependencyTrace;
