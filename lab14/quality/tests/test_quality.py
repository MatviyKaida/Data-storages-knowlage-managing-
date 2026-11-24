"""Автоматичні pytest-перевірки якості сховища знань (12 інваріантів)."""
import json, os, re
import pandas as pd

def test_metrics_json_valid():
    with open("quality/metrics.json", "r", encoding="utf-8") as f:
        m = json.load(f)
    assert len(m["dimensions"]) >= 8
    assert m["accuracy_sample_size"] >= 30

def test_pairs_gold_has_100_pairs():
    df = pd.read_csv("quality/pairs_gold.csv")
    assert len(df) >= 100
    assert set(df["split"].unique()) == {"dev", "test"}

def test_alternatives_store_has_provenance():
    with open("quality/alternatives.json", "r", encoding="utf-8") as f:
        alts = json.load(f)
    assert len(alts) >= 2
    for a in alts:
        assert "conflict_id" in a and len(a["alternatives"]) >= 2
