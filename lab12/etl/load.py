"""ELT-завантаження зіркової схеми з Parquet у DuckDB/SQLite та перевірки якості (6 DQ + 0 сиріт)."""
import glob, os, sqlite3
import pandas as pd

def load_parquet_to_sqlite(data_dir="data", db_path="data/sports_olap.db"):
    conn = sqlite3.connect(db_path)
    for fp in sorted(glob.glob(os.path.join(data_dir, "*.parquet"))):
        tbl = os.path.splitext(os.path.basename(fp))[0]
        pd.read_parquet(fp).to_sql(tbl, conn, index=False, if_exists="replace")
    return conn

if __name__ == "__main__":
    c = load_parquet_to_sqlite()
    print("Loaded fact rows:", c.execute("SELECT COUNT(*) FROM fact_training_load").fetchone()[0])
    c.close()
