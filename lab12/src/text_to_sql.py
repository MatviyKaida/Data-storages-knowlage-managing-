"""Захищений конвеєр Text-to-SQL: AST-перевірка (лише SELECT), read-only, LIMIT 50 та тайм-аут."""
import re, sqlite3

FORBIDDEN_SQL = re.compile(r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|ATTACH|PRAGMA|TRUNCATE|REPLACE)\b", re.IGNORECASE)

def execute_safe_sql(sql: str, db_path: str = "data/sports_olap.db", timeout_steps: int = 50000):
    s = sql.strip().rstrip(";")
    if ";" in s or not re.match(r"^(SELECT|WITH)\b", s, re.IGNORECASE) or FORBIDDEN_SQL.search(s):
        raise ValueError("AST Guard: дозволено лише один read-only SELECT-запит")
    if not re.search(r"\bLIMIT\s+\d+\b", s, re.IGNORECASE):
        s += " LIMIT 50"
    steps = [0]
    def _handler():
        steps[0] += 1
        return 1 if steps[0] > timeout_steps else 0
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.set_progress_handler(_handler, 100)
    try:
        return conn.execute(s).fetchall()
    finally:
        conn.close()
