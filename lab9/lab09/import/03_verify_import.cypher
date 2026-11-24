// Крок 4. Перевірка кількості вузлів і зв'язків, ідемпотентності та порушення обмеження
MATCH (n) RETURN count(n) AS totalNodes;
MATCH ()-[r]->() RETURN count(r) AS totalRelationships;

MATCH (n)
RETURN labels(n) AS labelSet, count(n) AS nodeCount
ORDER BY nodeCount DESC;

MATCH ()-[r]->()
RETURN type(r) AS relType, count(r) AS relCount
ORDER BY relCount DESC;

// Перевірка наявності властивостей походження на всіх ребрах (має повернути 0)
MATCH ()-[r]->()
WHERE r.source IS NULL OR r.confidence IS NULL OR r.validFrom IS NULL
RETURN count(r) AS missingProvenanceCount;

// Приклад порушення обмеження унікальності constr_athlete_code
// Очікувана помилка:
// Neo.ClientError.Schema.ConstraintValidationFailed:
// Node(13) already exists with label `Athlete` and property `entityCode` = 'ATH-2026-014'
CREATE (:Athlete {entityCode: 'ATH-2026-014', name: 'Тестовий дублікат'});
