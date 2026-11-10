# Team workflow and ownership

- **BC owner** controls `agents/bc_agent/`.
- **Data owner** controls `agents/data_agent/`.
- The two developers jointly approve changes in `interfaces/`.
- Make source changes on separate feature branches (`bc/...`, `data/...`) and merge through MRs into `main`.
- For cross-agent reviews, open a GitLab issue or MR and request review; don't silently change the other's component.
- Agent-generated patches run in isolated copies/worktrees, with the human reviewing before merging.
- Do not let either agent run arbitrary code from untrusted datasets or unchecked remote sources.
- Do not store datasets, checkpoints, secrets, tokens, large simulation outputs, or robot credentials in the repo.
- Use GitLab CODEOWNERS later if your tier and approval policy warrant it (usernames not included in this template).

## Stable integration contract (v1)

`interfaces/task.schema.json` describes a coordinator-to-agent request. `interfaces/result.schema.json` describes the agent's response. Neither agent needs the coordinator or MCP installed to develop against these schemas.

Examples are in `interfaces/examples/`. The schema contracts are starting points; version changes should be reviewed together.

## When a coordinator is introduced

Keep the folder locations and add `coordinator/`; each agent should expose a small adapter around its existing CLI/Python API. A shared package is optional and should be extracted only after actual duplication emerges.
