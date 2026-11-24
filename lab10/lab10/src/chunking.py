"""Стратегії chunking для ЛР №10: fixed_overlap, header_structure, semantic_hierarchical."""
import re

def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if len(s.strip()) > 15]

def chunk_fixed_overlap(docs: list[dict], size: int = 240, overlap: int = 60) -> list[dict]:
    out, idx = [], 0
    for d in docs:
        txt = re.sub(r"#+ ", "", d["clean_text"]).replace("\n", " ")
        start = 0
        while start < len(txt):
            piece = txt[start:start + size].strip()
            if len(piece) > 30:
                idx += 1
                out.append({"chunk_id": f"FX-{idx:04d}", "doc_id": d["doc_id"], "text": piece})
            start += (size - overlap)
    return out

def chunk_by_headers(docs: list[dict]) -> list[dict]:
    out, idx = [], 0
    for d in docs:
        for sec in re.split(r"\n(?=## )", d["clean_text"]):
            lines = sec.strip().splitlines()
            if not lines or lines[0].startswith("# "):
                continue
            sec_title = lines[0].replace("## ", "").strip()
            body = " ".join(lines[1:]).strip()
            idx += 1
            out.append({"chunk_id": f"HD-{idx:04d}", "doc_id": d["doc_id"], "text": f"{d['title']} — {sec_title}: {body}"})
    return out

def chunk_semantic_hierarchical(docs: list[dict]) -> list[dict]:
    out, idx = [], 0
    for d in docs:
        for sec in re.split(r"\n(?=## )", d["clean_text"]):
            lines = sec.strip().splitlines()
            if not lines or lines[0].startswith("# "):
                continue
            sec_title = lines[0].replace("## ", "").strip()
            body = " ".join(lines[1:]).strip()
            sents = split_sentences(body)
            for s in sents:
                idx += 1
                out.append({"chunk_id": f"CH-{idx:04d}", "doc_id": d["doc_id"], "section": sec_title, "text": f"{d['title']} — {sec_title}: {s}"})
            if len(sents) >= 2:
                idx += 1
                out.append({"chunk_id": f"CH-{idx:04d}", "doc_id": d["doc_id"], "section": f"{sec_title} (зведення)", "text": f"{d['title']} — {sec_title}: {body}"})
    return out
