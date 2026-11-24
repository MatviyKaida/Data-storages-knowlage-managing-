"""Гібридний пошук BM25 + Dense, злиття RRF (k=60), metadata pre-filter та cross-reranker (top-30 -> top-5)."""
import math, re
from collections import Counter, defaultdict
from src.index import tokenize, char_ngrams

class BM25Retriever:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.ids, self.tf, self.dl, self.avgdl, self.idf = [], [], [], 0.0, {}

    def build(self, ids: list[str], texts: list[str]):
        self.ids = list(ids)
        df = Counter()
        for t in texts:
            toks = tokenize(t)
            self.dl.append(len(toks))
            cnt = Counter(toks)
            self.tf.append(cnt)
            for w in cnt:
                df[w] += 1
        N = len(texts)
        self.avgdl = sum(self.dl) / max(N, 1)
        self.idf = {w: math.log((N - c + 0.5) / (c + 0.5) + 1.0) for w, c in df.items()}

    def search(self, query: str, top_k: int = 30, allowed_ids: set | None = None):
        qtoks = tokenize(query)
        scores = []
        for i, cid in enumerate(self.ids):
            if allowed_ids is not None and cid not in allowed_ids:
                continue
            s, dl, cnt = 0.0, self.dl[i], self.tf[i]
            for w in qtoks:
                if w not in cnt: continue
                f = cnt[w]
                s += self.idf.get(w, 0.0) * (f * (self.k1 + 1.0)) / (f + self.k1 * (1.0 - self.b + self.b * dl / self.avgdl))
            scores.append((s, cid))
        scores.sort(reverse=True)
        return scores[:top_k]

def rrf_fuse(bm25_res: list, dense_res: list, k: int = 60, top_k: int = 30) -> list:
    scores = defaultdict(float)
    for rank, (_, cid) in enumerate(bm25_res, start=1):
        scores[cid] += 1.0 / (k + rank)
    for rank, (_, cid) in enumerate(dense_res, start=1):
        scores[cid] += 1.0 / (k + rank)
    return sorted([(s, cid) for cid, s in scores.items()], reverse=True)[:top_k]

def prefilter_ids(chunks: list[dict], doc_type: str | None = None, sensitivity: str | None = None, date_from: str | None = None) -> set:
    allowed = set()
    for c in chunks:
        if doc_type and c["type"] != doc_type: continue
        if sensitivity and c["sensitivity"] != sensitivity: continue
        if date_from and c["date"] < date_from: continue
        allowed.add(c["chunk_id"])
    return allowed
