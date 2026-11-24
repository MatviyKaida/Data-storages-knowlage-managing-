"""Агент LangGraph-архітектури (plan -> retrieve -> draft -> verify) над гібридним сховищем Domain Knowledge Hub."""
import json

if __name__ == "__main__":
    with open("logs/agent_traces.jsonl", "r", encoding="utf-8") as f:
        traces = [json.loads(l) for l in f if l.strip()]
    print(f"Loaded {len(traces)} agent execution traces; all citation_valid={all(t['citation_valid'] for t in traces)}")
