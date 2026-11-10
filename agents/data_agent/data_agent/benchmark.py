"""Simple deterministic metadata query benchmark (not a model benchmark)."""
import argparse
import json
from pathlib import Path
from .tools import count_recordings


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True)
    p.add_argument("--tasks", default="benchmarks/example_tasks.jsonl")
    args = p.parse_args()
    tasks = [json.loads(line) for line in Path(args.tasks).read_text().splitlines() if line.strip()]
    passed = 0
    for task in tasks:
        actual = count_recordings(args.db, **task["filters"])
        ok = actual == task["expected_count"]
        passed += ok
        print(f"{task['id']}: {'PASS' if ok else 'FAIL'} (actual={actual}, expected={task['expected_count']})")
    print(f"Results: {passed}/{len(tasks)} passed")
    if passed != len(tasks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
