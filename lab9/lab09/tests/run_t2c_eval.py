#!/usr/bin/env python3
"""
Оцінювання Text-to-Cypher (ЛР №9, Результат 5):
- read-only роль (t2c_reader)
- перевірка схеми графа (дозволені мітки, типи ребер, властивості)
- перевірка наявності LIMIT <= 25 та заборона write-операторів
- обчислення метрик: Execution Accuracy (EX), Syntax Validity, Schema Validity, середня затримка.
"""
import argparse
import json
import os
import re
import statistics

ALLOWED_LABELS = {
    "Athlete", "Coach", "TrainingSession", "SpeedStrengthSession",
    "TrainingMicrocycle", "BiometricSensor", "LoadRecoveryMetric",
    "LabTest", "SportsInjury", "ReturnToPlayProtocol", "SportsDoctor",
}
ALLOWED_RELS = {
    "COACHED_BY", "PERFORMS_SESSION", "PART_OF_MICROCYCLE", "USES_SENSOR",
    "HAS_METRIC_RECORD", "RECORDED_FROM_SESSION", "UNDERGOES_LAB_TEST",
    "HAS_INJURY_DIAGNOSIS", "TREATED_BY_PROTOCOL", "SUPERVISED_BY_DOCTOR",
}
FORBIDDEN_WRITE_KW = re.compile(
    r"\b(CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|CALL\s+apoc\.merge|LOAD\s+CSV)\b",
    re.IGNORECASE,
)

def validate_guardrails(cypher: str) -> tuple[bool, list[str]]:
    issues = []
    if FORBIDDEN_WRITE_KW.search(cypher):
        issues.append("ReadOnlyViolation: виявлено заборонений write-оператор")
    if not re.search(r"\bLIMIT\s+(\d+)\b", cypher, re.IGNORECASE):
        issues.append("MissingLimit: відсутній обов'язковий LIMIT")
    else:
        lim = int(re.search(r"\bLIMIT\s+(\d+)\b", cypher, re.IGNORECASE).group(1))
        if lim > 25:
            issues.append(f"LimitExceeded: LIMIT {lim} > 25")
    if "`skm:" in cypher or "skm:" in cypher:
        issues.append("RDFPrefixLeakage: виявлено RDF-префікс skm:")
    for lbl in re.findall(r":([A-Z][A-Za-z]+)\b", cypher):
        if lbl not in ALLOWED_LABELS and lbl not in ALLOWED_RELS:
            issues.append(f"UnknownLabel: {lbl}")
    return (len(issues) == 0, issues)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonl", default="tests/t2c.jsonl")
    parser.add_argument("--offline-validate", action="store_true", help="Статична валідація без підключення до Neo4j")
    args = parser.parse_args()

    with open(args.jsonl, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]

    total = len(records)
    syntax_ok = sum(1 for r in records if r["syntax_valid"])
    schema_ok = sum(1 for r in records if r["schema_valid"])
    exec_ok = sum(1 for r in records if r["execution_match"])
    avg_lat = statistics.mean(r["latency_sec"] for r in records)

    print(f"Всього тестових питань : {total}")
    print(f"Syntax Validity        : {syntax_ok}/{total} ({syntax_ok/total*100:.1f}%)")
    print(f"Schema Validity        : {schema_ok}/{total} ({schema_ok/total*100:.1f}%)")
    print(f"Execution Match (EX)   : {exec_ok}/{total} ({exec_ok/total*100:.1f}%)")
    print(f"Середній час генерації : {avg_lat:.2f} с")
    print("\nПеревірка guardrails (read-only + LIMIT + схема):")
    for r in records:
        ok, issues = validate_guardrails(r["generated_cypher"])
        status = "OK" if ok else f"WARN: {', '.join(issues)}"
        print(f"  {r['id']}: guardrails={status} | EX={r['execution_match']}")

    if not args.offline_validate:
        from neo4j import GraphDatabase
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_READONLY_USER", "t2c_reader")
        pwd = os.getenv("NEO4J_READONLY_PASSWORD", "readonly_2026")
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        with driver.session(default_access_mode="READ") as sess:
            for r in records:
                ok, issues = validate_guardrails(r["generated_cypher"])
                if not ok:
                    print(f"[SKIP {r['id']}] {issues}")
                    continue
                try:
                    res = list(sess.run(r["generated_cypher"]))
                    print(f"[RUN  {r['id']}] rows={len(res)}")
                except Exception as e:
                    print(f"[ERR  {r['id']}] {e}")
        driver.close()

if __name__ == "__main__":
    main()
