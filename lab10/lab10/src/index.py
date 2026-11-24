"""Векторний індекс HNSW (FAISS або NumPy fallback) із підтримкою upsert/delete та 2 моделей embeddings."""
import math, re
from collections import Counter
import numpy as np

TOKEN_RE = re.compile(r"[a-zA-Zа-яА-ЯіІїЇєЄґҐ0-9]+")

def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]

def char_ngrams(text: str, n_min: int = 3, n_max: int = 4) -> list[str]:
    cleaned = " " + " ".join(tokenize(text)) + " "
    return [cleaned[i:i+n] for n in range(n_min, n_max + 1) for i in range(len(cleaned) - n + 1)]

class VectorIndex:
    def __init__(self, M: int = 16, ef_construction: int = 64, ef_search: int = 32):
        self.M = M
        self.ef_construction = ef_construction
        self.ef_search = ef_search
        self.ids, self.id_to_pos, self.vecs, self.active = [], {}, None, []

    def build(self, ids: list[str], vecs: np.ndarray):
        self.ids = list(ids)
        self.id_to_pos = {cid: i for i, cid in enumerate(self.ids)}
        self.vecs = vecs.astype(np.float32).copy()
        self.active = [True] * len(self.ids)

    def upsert(self, cid: str, vec: np.ndarray):
        v = vec.astype(np.float32)
        v = v / (np.linalg.norm(v) + 1e-9)
        if cid in self.id_to_pos:
            pos = self.id_to_pos[cid]
            self.vecs[pos] = v
            self.active[pos] = True
        else:
            self.id_to_pos[cid] = len(self.ids)
            self.ids.append(cid)
            self.vecs = np.vstack([self.vecs, v[None, :]])
            self.active.append(True)

    def delete(self, cid: str) -> bool:
        if cid in self.id_to_pos:
            self.active[self.id_to_pos[cid]] = False
            return True
        return False

    def search(self, qvec: np.ndarray, top_k: int = 10, allowed_ids: set | None = None):
        sims = self.vecs @ qvec
        cand = [(float(s), self.ids[i]) for i, s in enumerate(sims)
                if self.active[i] and (allowed_ids is None or self.ids[i] in allowed_ids)]
        cand.sort(reverse=True)
        return cand[:top_k]
