"""Optional local Ollama adapter: model selects a safe tool; Python executes it."""
import json
from urllib.request import Request, urlopen
from .tools import count_recordings, list_recordings, latest_recording

SYSTEM = """You are a data-query router. Return one JSON object only.
Allowed forms:
{"tool":"count","filters":{"direction":"anticlockwise"}}
{"tool":"list","filters":{"task":"cube rotation"}}
{"tool":"latest","filters":{}}
Only include the filters task, direction, outcome, validity when unambiguously specified.
Do not guess dates or values. Do not generate SQL. Do not invent counts.
Use tool=latest for requests about the most recent recording; tool=count for how many/have we, otherwise list.
"""


def ask(db_file: str, question: str, model: str = "qwen3.5:0.8b", endpoint: str = "http://127.0.0.1:11434/api/chat") -> dict:
    data = {"model": model, "stream": False, "format": "json", "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]}
    req = Request(endpoint, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=90) as resp:
            output = json.loads(resp.read())
    except Exception as exc:
        raise RuntimeError("Local model unavailable. Start Ollama, pull the model, or use the deterministic count/list/latest commands.") from exc
    try:
        intent = json.loads(output["message"]["content"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("The model did not return a valid tool choice") from exc
    if not isinstance(intent, dict) or intent.get("tool") not in {"count", "latest", "list"}:
        raise ValueError("Invalid tool choice; nothing executed")
    filters = intent.get("filters", {})
    if not isinstance(filters, dict):
        raise ValueError("Invalid filters; nothing executed")
    tool = intent["tool"]
    if tool == "latest":
        if filters:
            raise ValueError("latest does not support filters")
        result = latest_recording(db_file)
    elif tool == "count":
        result = count_recordings(db_file, **filters)
    else:
        result = list_recordings(db_file, **filters)
    return {"question": question, "tool": tool, "filters": filters, "result": result, "note": "Results come from local catalog; source recordings, not exported segments."}
