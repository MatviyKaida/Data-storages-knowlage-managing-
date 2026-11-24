"""Генератор SQL із семантичного шару semantic/metrics.yml."""
import yaml

def compile_metric_sql(metric_name: str, group_by: str, where_clause: str = "", yml_path: str = "semantic/metrics.yml") -> str:
    with open(yml_path, "r", encoding="utf-8") as f:
        metrics = yaml.safe_load(f)["metrics"]
    m = metrics[metric_name]
    joins = []
    for prefix, sql_j in [
        ("t.", "JOIN dim_taxonomy t ON f.tax_key = t.tax_key"),
        ("a.", "JOIN dim_athlete a ON f.athlete_key = a.athlete_key"),
        ("m.", "JOIN dim_microcycle m ON f.mc_key = m.mc_key"),
        ("d.", "JOIN dim_date d ON f.date_key = d.date_key"),
    ]:
        if group_by.startswith(prefix) or prefix in where_clause:
            joins.append(sql_j)
    w = f"WHERE {where_clause}" if where_clause else ""
    return f"SELECT {group_by}, {m['formula']} AS {metric_name} FROM fact_training_load f {' '.join(joins)} {w} GROUP BY {group_by} ORDER BY {metric_name} DESC"
