"""Data Agent demonstration CLI: python -m data_agent.cli --help"""
import argparse
import json
from .tools import build_catalog, count_recordings, list_recordings, latest_recording
from .agent import ask


def main():
    p = argparse.ArgumentParser(description="Data Engineering Agent (local metadata tools)")
    sub = p.add_subparsers(dest="command", required=True)
    idx = sub.add_parser("index", help="Index source recordings metadata CSV")
    idx.add_argument("--csv", required=True)
    idx.add_argument("--db", required=True)
    for name in ("count", "list", "latest", "ask"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--db", required=True)
        if name in ("count", "list"):
            for field in ("task", "direction", "outcome", "validity"):
                cmd.add_argument("--" + field)
        if name == "ask":
            cmd.add_argument("--model", default="qwen3.5:0.8b")
            cmd.add_argument("--question", required=True)
    args = p.parse_args()
    if args.command == "index":
        result = {"indexed_source_recordings": build_catalog(args.csv, args.db)}
    elif args.command == "count":
        filters = {k: getattr(args, k) for k in ("task", "direction", "outcome", "validity") if getattr(args, k)}
        result = {"count_source_recordings": count_recordings(args.db, **filters), "filters": filters}
    elif args.command == "list":
        filters = {k: getattr(args, k) for k in ("task", "direction", "outcome", "validity") if getattr(args, k)}
        result = {"source_recordings": list_recordings(args.db, **filters), "filters": filters}
    elif args.command == "latest":
        result = {"latest_source_recording": latest_recording(args.db)}
    else:
        result = ask(args.db, args.question, model=args.model)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
