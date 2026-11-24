// Крок 3. Ідемпотентний імпорт 120 вузлів та 245 зв'язків через LOAD CSV + MERGE
LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
CALL apoc.merge.node(
  split(row.labels, ';'),
  {entityCode: row.entityCode},
  {
    name: row.name,
    age: CASE WHEN row.age <> '' THEN toInteger(toFloat(row.age)) ELSE null END,
    roleOrType: row.roleOrType,
    restingHrBpm: CASE WHEN row.restingHrBpm <> '' THEN toInteger(toFloat(row.restingHrBpm)) ELSE null END,
    rmssdBaseMs: CASE WHEN row.rmssdBaseMs <> '' THEN toFloat(row.rmssdBaseMs) ELSE null END,
    rmssdMorningMs: CASE WHEN row.rmssdMorningMs <> '' THEN toFloat(row.rmssdMorningMs) ELSE null END,
    acwrValue: CASE WHEN row.acwrValue <> '' THEN toFloat(row.acwrValue) ELSE null END,
    readinessScorePct: CASE WHEN row.readinessScorePct <> '' THEN toInteger(toFloat(row.readinessScorePct)) ELSE null END,
    plannedTrimp: CASE WHEN row.plannedTrimp <> '' THEN toInteger(toFloat(row.plannedTrimp)) ELSE null END,
    osicsCode: CASE WHEN row.osicsCode <> '' THEN row.osicsCode ELSE null END,
    maxAllowedHrBpm: CASE WHEN row.maxAllowedHrBpm <> '' THEN toInteger(toFloat(row.maxAllowedHrBpm)) ELSE null END,
    totalDistanceM: CASE WHEN row.totalDistanceM <> '' THEN toInteger(toFloat(row.totalDistanceM)) ELSE null END,
    hsrDistanceM: CASE WHEN row.hsrDistanceM <> '' THEN toInteger(toFloat(row.hsrDistanceM)) ELSE null END,
    rpeScore: CASE WHEN row.rpeScore <> '' THEN toFloat(row.rpeScore) ELSE null END,
    sessionDate: CASE WHEN row.sessionDate <> '' THEN date(row.sessionDate) ELSE null END,
    creatineKinaseUL: CASE WHEN row.creatineKinaseUL <> '' THEN toInteger(toFloat(row.creatineKinaseUL)) ELSE null END,
    lsiSymmetryPct: CASE WHEN row.lsiSymmetryPct <> '' THEN toInteger(toFloat(row.lsiSymmetryPct)) ELSE null END,
    extraInfo: row.extraInfo
  },
  {}
) YIELD node
RETURN count(node) AS totalMergedNodes;

LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
MATCH (src {entityCode: row.sourceCode})
MATCH (dst {entityCode: row.targetCode})
CALL apoc.merge.relationship(
  src,
  row.relType,
  {},
  {
    source: row.source,
    confidence: toFloat(row.confidence),
    validFrom: date(row.validFrom)
  },
  dst,
  {}
) YIELD rel
RETURN count(rel) AS totalMergedRelationships;
