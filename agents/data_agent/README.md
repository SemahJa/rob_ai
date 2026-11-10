# Data Engineering Agent — minimal local starter

This starter is owned by the Data developer. It uses **only the Python standard library** for its metadata catalog and tests. MCP is not required. An optional Ollama adapter provides natural-language intent selection, while all actual counts come from SQLite.

## Quick start (Ubuntu or Windows with Python 3.10+)

```bash
cd agents/data_agent
python3 -m unittest discover -s tests -v
python3 -m data_agent.cli index --csv sample_data/recordings.csv --db .local/catalog.sqlite
python3 -m data_agent.cli count --db .local/catalog.sqlite --direction anticlockwise
python3 -m data_agent.cli list --db .local/catalog.sqlite --validity validated
python3 -m data_agent.cli latest --db .local/catalog.sqlite
```

## Optional Ollama model

```bash
ollama pull qwen3.5:0.8b
python3 -m data_agent.cli ask --db .local/catalog.sqlite --model qwen3.5:0.8b --question "Have we collected anticlockwise rotation?"
```

The LLM is **not trusted as a data source**. It only selects one of `count`, `latest`, or `list`, with validated filters; no free-form SQL is executed. Errors are shown rather than guessed.

## Source metadata CSV

Required columns:

- `recording_id`: original source recording ID; must be unique
- `recorded_at_utc`: ISO 8601 timestamp with offset or Z
- `task`: task name (e.g., `cube rotation`)
- `direction`: `clockwise`, `anticlockwise`, or `unknown`
- `outcome`: `success`, `failure`, `partial`, or `unknown`
- `validity`: `validated`, `review`, or `invalid`
- `source_path`: path to original recording (not a LeRobot segment)

**This CSV is sample synthetic data.** Do not confuse these counts with real collection results. Real imports should have source provenance, consistent direction-frame conventions, and an explicit last-indexed timestamp.

## Next development tasks

1. Add a safe MCAP inventory scanner (metadata only) and distinguish recordings vs exports.
2. Add checks for camera streams, action masks, timestamps, and duplication.
3. Add indexing of LeRobot exports with source lineage.
4. Add evaluation questions and ground-truth answer fixtures.
5. Standardize integration with the `interfaces/` schemas for future coordinator use.
