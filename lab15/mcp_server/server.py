"""Мінімальний MCP-сервер (JSON-RPC 2.0) із 3 read-only інструментами: search_docs, query_graph, query_olap."""
import json, sys

TOOLS = [
    {"name": "search_docs", "description": "Read-only гібридний пошук по корпусу регламентів (з pre-filter sensitivity).",
     "inputSchema": {"type": "object", "required": ["query", "role"], "properties": {"query": {"type": "string"}, "role": {"enum": ["guest", "coach", "doctor"]}, "top_k": {"type": "integer", "maximum": 10}}}},
    {"name": "query_graph", "description": "Read-only витяг 1-2 крокового підграфа сутності з Neo4j (ліміт 6 ребер).",
     "inputSchema": {"type": "object", "required": ["entity_code", "role"], "properties": {"entity_code": {"type": "string"}, "role": {"enum": ["guest", "coach", "doctor"]}}}},
    {"name": "query_olap", "description": "Read-only запит затверджених метрик із семантичного шару OLAP (LIMIT 5).",
     "inputSchema": {"type": "object", "required": ["metric", "role"], "properties": {"metric": {"enum": ["overload_shock", "distance_by_tax"]}, "role": {"enum": ["guest", "coach", "doctor"]}}}},
]

def handle_rpc(req: dict) -> dict:
    method = req.get("method")
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req.get("id"), "result": {"tools": TOOLS}}
    return {"jsonrpc": "2.0", "id": req.get("id"), "error": {"code": -32601, "message": "Method not found"}}

if __name__ == "__main__":
    print(json.dumps(handle_rpc({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}), ensure_ascii=False, indent=2))
