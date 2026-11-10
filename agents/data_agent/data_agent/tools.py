"""Safe local metadata catalog. One row represents an ORIGINAL source recording."""
from __future__ import annotations

import csv
import sqlite3
from datetime import datetime
from pathlib import Path

REQUIRED = ("recording_id", "recorded_at_utc", "task", "direction", "outcome", "validity", "source_path")
ALLOWED = {
    "direction": {"clockwise", "anticlockwise", "unknown"},
    "outcome": {"success", "failure", "partial", "unknown"},
    "validity": {"validated", "review", "invalid"},
}
FILTERS = {"task", "direction", "outcome", "validity"}


def build_catalog(csv_file: str | Path, db_file: str | Path) -> int:
    """Rebuild a local SQLite index from a trusted CSV. Never modify source recordings."""
    csv_file, db_file = Path(csv_file), Path(db_file)
    with csv_file.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not set(REQUIRED).issubset(reader.fieldnames):
            raise ValueError(f"CSV must have columns: {', '.join(REQUIRED)}")
        rows = list(reader)
    ids = set()
    for row in rows:
        if not all(row.get(key, "").strip() for key in REQUIRED):
            raise ValueError("Missing required value in CSV row")
        if row["recording_id"] in ids:
            raise ValueError("Duplicate original recording_id: " + row["recording_id"])
        ids.add(row["recording_id"])
        for key, choices in ALLOWED.items():
            if row[key] not in choices:
                raise ValueError(f"Invalid {key}: {row[key]!r}")
        date = datetime.fromisoformat(row["recorded_at_utc"].replace("Z", "+00:00"))
        if date.tzinfo is None:
            raise ValueError("recorded_at_utc must include timezone")
    db_file.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_file) as conn:
        conn.execute("DROP TABLE IF EXISTS recordings")
        conn.execute("CREATE TABLE recordings (recording_id TEXT PRIMARY KEY, recorded_at_utc TEXT NOT NULL, task TEXT, direction TEXT, outcome TEXT, validity TEXT, source_path TEXT)")
        conn.executemany("INSERT INTO recordings VALUES (?,?,?,?,?,?,?)", [[row[k] for k in REQUIRED] for row in rows])
        conn.execute("CREATE INDEX IF NOT EXISTS idx_recordings_direction ON recordings(direction)")
    return len(rows)


def _connect_readonly(db_file: str | Path):
    p = Path(db_file).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Index not found: {p}. Run `index` first.")
    return sqlite3.connect(p.as_uri() + "?mode=ro", uri=True)


def _query_where(filters: dict):
    where, values = [], []
    for key, value in filters.items():
        if value is None:
            continue
        if key not in FILTERS:
            raise ValueError(f"Unsupported filter: {key}")
        if key in ALLOWED and value not in ALLOWED[key]:
            raise ValueError(f"Unsupported {key} value: {value}")
        where.append(f"{key} = ?")
        values.append(value)
    return (" WHERE " + " AND ".join(where) if where else ""), values


def count_recordings(db_file: str | Path, **filters) -> int:
    clause, vals = _query_where(filters)
    with _connect_readonly(db_file) as conn:
        return conn.execute("SELECT COUNT(*) FROM recordings" + clause, vals).fetchone()[0]


def list_recordings(db_file: str | Path, limit: int = 20, **filters) -> list[dict]:
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    clause, vals = _query_where(filters)
    sql = "SELECT recording_id, recorded_at_utc, task, direction, outcome, validity, source_path FROM recordings" + clause + " ORDER BY recorded_at_utc DESC, recording_id DESC LIMIT ?"
    with _connect_readonly(db_file) as conn:
        rows = conn.execute(sql, [*vals, limit]).fetchall()
    return [dict(zip(REQUIRED, row)) for row in rows]


def latest_recording(db_file: str | Path) -> dict | None:
    rows = list_recordings(db_file, limit=1)
    return rows[0] if rows else None
