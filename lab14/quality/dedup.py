"""Конвеєр дедуплікації (Entity Resolution): нормалізація -> blocking -> 3 метрики схожості -> merge/unmerge."""
import copy, math, re
from collections import Counter
from difflib import SequenceMatcher

def normalize_str(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-zа-яіїєґ0-9\s-]", "", s.lower().strip()))

def blocking_key(rec: dict) -> str:
    n = normalize_str(rec["name"])
    return f"{rec['type']}::{n[:4]}"

def char_trigram_cosine(a: str, b: str) -> float:
    na, nb = f" {normalize_str(a)} ", f" {normalize_str(b)} "
    ca = Counter(na[i:i+3] for i in range(max(0, len(na)-2)))
    cb = Counter(nb[i:i+3] for i in range(max(0, len(nb)-2)))
    dot = sum(ca[k] * cb[k] for k in ca.keys() & cb.keys())
    mag = math.sqrt(sum(v*v for v in ca.values())) * math.sqrt(sum(v*v for v in cb.values()))
    return dot / mag if mag > 0 else 0.0

def score_pair(rec1: dict, rec2: dict) -> float:
    s_edit = SequenceMatcher(None, normalize_str(rec1["name"]), normalize_str(rec2["name"])).ratio()
    s_emb = char_trigram_cosine(rec1["name"], rec2["name"])
    s_attr = 1.0 if rec1["type"] == rec2["type"] else 0.0
    return round(0.45 * s_edit + 0.40 * s_emb + 0.15 * s_attr, 4)

def merge_with_provenance(store: dict, journal: dict, keep_id: str, dup_id: str, ts: str = "2026-11-24"):
    snap = copy.deepcopy(store[dup_id])
    store[keep_id]["merged_from"] = store[keep_id].get("merged_from", []) + [dup_id]
    journal[dup_id] = {"kept": keep_id, "snapshot": snap, "merged_at": ts}
    del store[dup_id]

def unmerge(store: dict, journal: dict, dup_id: str):
    rec = journal.pop(dup_id)
    store[dup_id] = rec["snapshot"]
    store[rec["kept"]]["merged_from"].remove(dup_id)
