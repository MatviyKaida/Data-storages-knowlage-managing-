"""Entity linking та витяг лінеаризованого підграфа (1–2 кроки з лімітом ребер) із графа ЛР №9."""
import os
from collections import defaultdict
import pandas as pd

SYNONYMS = {
    "коваленко": "ATH-2026-014", "бондаренко": "ATH-2026-015", "мельник": "COACH-01",
    "кравчук": "COACH-02", "іваненко": "COACH-03", "литвин": "COACH-04",
    "савчук": "MED-03", "коваль": "MED-01", "гриценко": "MED-02",
    "ударний мікроцикл w42": "MC-2026-W42", "мікроцикл w42": "MC-2026-W42",
    "гнатюк": "ATH-2026-003", "савченко": "ATH-2026-006", "лисенко": "ATH-2026-009",
}

class GraphContextRetriever:
    def __init__(self, nodes_csv: str, rels_csv: str):
        ndf = pd.read_csv(nodes_csv)
        rdf = pd.read_csv(rels_csv)
        self.node_map = {r["entityCode"]: r.to_dict() for _, r in ndf.iterrows()}
        self.adj = defaultdict(list)
        for _, r in rdf.iterrows():
            u, v, t = r["sourceCode"], r["targetCode"], r["relType"]
            self.adj[u].append((v, t, "out", r["confidence"]))
            self.adj[v].append((u, t, "in", r["confidence"]))

    def link_entities(self, query: str) -> list[str]:
        ql = query.lower()
        found = [c for c in self.node_map if c.lower() in ql]
        for syn, code in SYNONYMS.items():
            if syn in ql and code not in found:
                found.append(code)
        return found[:4]

    def extract_subgraph(self, seeds: list[str], hops: int = 2, max_edges: int = 10) -> tuple[list[str], list[str]]:
        edges_str, node_ids, seen_e, frontier = [], set(seeds), set(), list(seeds)
        for _ in range(hops):
            nxt = []
            for u in frontier:
                for v, rt, direction, conf in self.adj.get(u, []):
                    if len(edges_str) >= max_edges:
                        break
                    key = (u, v, rt) if direction == "out" else (v, u, rt)
                    if key in seen_e:
                        continue
                    seen_e.add(key)
                    node_ids.add(v)
                    edges_str.append(f"[{key[0]}|{self.node_map[key[0]]['name']}] -[:{rt} {{conf:{conf}}}]-> [{key[1]}|{self.node_map[key[1]]['name']}]")
                    nxt.append(v)
                if len(edges_str) >= max_edges:
                    break
            frontier = nxt
        return edges_str, sorted(node_ids)
