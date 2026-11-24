"""Рекомендаційний модуль: Popularity, Graph-Paths, Embeddings kNN, Hybrid Weighted/RRF та фільтри якості/RBAC."""
import json, math, os
from collections import defaultdict
import numpy as np

ROLE_PERMS = {
    "guest": {"public"},
    "coach": {"public", "internal"},
    "analyst": {"public", "internal", "restricted"},
    "doctor": {"public", "internal", "restricted"},
}

def load_catalog(path="data/catalog.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def apply_filters(candidates, role="coach", verified_only=True, max_age_days=180):
    allowed = ROLE_PERMS.get(role, {"public"})
    kept, removed = [], {"unverified": 0, "stale": 0, "rbac": 0}
    for it in candidates:
        if verified_only and not it.get("verified", False):
            removed["unverified"] += 1
            continue
        if max_age_days is not None and it.get("updated_days_ago", 999) > max_age_days:
            removed["stale"] += 1
            continue
        if it.get("sensitivity", "internal") not in allowed:
            removed["rbac"] += 1
            continue
        kept.append(it)
    return kept, removed

def recommend(user_id, role, history_ids, catalog, item_pop, method="hybrid_weighted", alpha=0.45, rrf_k=60, top_k=5):
    cands, removed = apply_filters(catalog, role=role)
    item_map = {it["item_id"]: it for it in catalog}
    ent_items = defaultdict(set)
    for it in catalog:
        for e in it["entities"]:
            ent_items[e].add(it["item_id"])

    pop_s = {it["item_id"]: item_pop.get(it["item_id"], 0) for it in cands}
    graph_s, paths = {}, {}
    if history_ids:
        u_ents, src_map = defaultdict(int), {}
        for h in history_ids:
            if h in item_map:
                for e in item_map[h]["entities"]:
                    u_ents[e] += 1
                    src_map[e] = h
        for it in cands:
            sc, best_p, bw = 0.0, None, -1.0
            for e in it["entities"]:
                if e in u_ents:
                    w = u_ents[e] / math.log2(max(1, len(ent_items[e])) + 1.5)
                    sc += w
                    if w > bw:
                        bw, best_p = w, (user_id, src_map[e], e, it["item_id"])
            graph_s[it["item_id"]] = sc
            paths[it["item_id"]] = best_p or (user_id, f"ROLE:{role}", f"TOPIC:{it['topic']}", it["item_id"])
    else:
        for it in cands:
            graph_s[it["item_id"]] = 1.0 if it["sensitivity"] == "public" else 0.7
            paths[it["item_id"]] = (user_id, f"ROLE:{role}", f"TOPIC:{it['topic']}", it["item_id"])

    emb_s = {}
    valid_hist = [item_map[h]["embedding"] for h in history_ids if h in item_map]
    if valid_hist:
        u_vec = np.mean(valid_hist, axis=0)
        u_vec = u_vec / max(1e-9, np.linalg.norm(u_vec))
        for it in cands:
            emb_s[it["item_id"]] = float(np.dot(u_vec, np.array(it["embedding"])))
    else:
        for it in cands:
            emb_s[it["item_id"]] = graph_s[it["item_id"]]

    def norm(d):
        vals = list(d.values())
        mn, mx = min(vals), max(vals)
        return {k: (0.0 if mx - mn < 1e-9 else (v - mn) / (mx - mn)) for k, v in d.items()}

    if method == "popularity":
        scores = pop_s
    elif method == "graph":
        scores = graph_s
    elif method == "embeddings":
        scores = emb_s
    elif method == "hybrid_weighted":
        ng, ne = norm(graph_s), norm(emb_s)
        scores = {k: alpha * ng[k] + (1.0 - alpha) * ne[k] for k in graph_s}
    else:
        rg = {k: i + 1 for i, (k, _) in enumerate(sorted(graph_s.items(), key=lambda x: -x[1]))}
        re_ = {k: i + 1 for i, (k, _) in enumerate(sorted(emb_s.items(), key=lambda x: -x[1]))}
        rp = {k: i + 1 for i, (k, _) in enumerate(sorted(pop_s.items(), key=lambda x: -x[1]))}
        scores = {k: 1/(rrf_k+rg[k]) + 1/(rrf_k+re_[k]) + 0.15/(rrf_k+rp[k]) for k in graph_s}

    ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))[:top_k]
    return [{"item_id": iid, "title": item_map[iid]["title"], "score": round(sc, 4), "path": paths[iid]} for iid, sc in ranked], removed
