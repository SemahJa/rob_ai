# rob_ai — lightweight two-agent starter

One GitLab repository, two independently developed specialist agents. There is **no coordinator, MCP server, or shared agent framework yet**.

```text
rob_ai/
├── agents/
│   ├── bc_agent/          # Owner: BC developer; copy current bc_agent_starter here
│   └── data_agent/        # Owner: Data developer; working minimal starter
├── interfaces/           # Only shared contracts; kept framework-agnostic
├── docs/TEAM_WORKFLOW.md
├── .gitlab-ci.yml
├── .gitignore
└── README.md
```

## 1. BC developer — keep your existing BC starter

From the directory containing both `rob_ai` and `bc_agent_starter`, use:

```bash
cp -a bc_agent_starter/. rob_ai/agents/bc_agent/
cd rob_ai/agents/bc_agent
python3 -m unittest discover -s tests -v
```

The BC starter remains an independent Python application. Its own `README.md` may replace the placeholder README included here; that's expected.

## 2. Data developer — inspect sample dataset without an LLM

```bash
cd rob_ai/agents/data_agent
python3 -m unittest discover -s tests -v
python3 -m data_agent.cli index --csv sample_data/recordings.csv --db .local/catalog.sqlite
python3 -m data_agent.cli count --db .local/catalog.sqlite --direction anticlockwise
python3 -m data_agent.cli latest --db .local/catalog.sqlite
```

The included recordings are **synthetic examples**, not real experiment data. For real data, supply a trusted CSV exported from your metadata pipeline and use a new local catalog. The agent never scans or labels raw MCAP files in this first prototype.

## 3. Optional local LLM query

Start Ollama separately and pull an approved model (requires initial download). Then:

```bash
python3 -m data_agent.cli ask --db .local/catalog.sqlite --model qwen3.5:0.8b \
  --question 'Did we collect anticlockwise rotation demonstrations?'
```

LLM use is optional and only chooses an allowlisted query operation; SQLite computes the counts. If Ollama is unavailable, use `count`, `latest`, and `list` commands directly.

## 4. GitLab collaboration

1. Keep `main` as the shared reviewed branch.
2. Use `bc/<feature>` and `data/<feature>` branches and merge requests.
3. Each developer changes their own `agents/<name>/` directory. Review edits to `interfaces/` together.
4. Do not push raw datasets, robot credentials, models, or generated runs to Git. Keep them outside the repository.

See `docs/TEAM_WORKFLOW.md` and `interfaces/` for the shared message contracts.

## 5. Future migration

Add `coordinator/` and a common runtime package **later** without relocating the two specialist directories. Extract shared code only after multiple agents need the same implementation. No MCP required in Phase 1–2.
