# AG2 Resource Hub

The official resource repository for the [AG2 CLI](https://github.com/ag2ai/ag2).

Install any artifact with:

```bash
ag2 install skills                          # AG2 skills (default)
ag2 install skills fastapi                  # FastAPI skills
ag2 install template mcp-server-python      # MCP server template
ag2 install tool web-search                 # AG2 tool function
ag2 install tool github-mcp                 # MCP server
ag2 install dataset agent-eval-bench        # Eval dataset
ag2 install agent research-analyst          # Claude Code agent
ag2 install bundle research-assistant       # Curated collection
```

## Artifact Types

| Type | Description |
|------|-------------|
| **Skills** | Knowledge for AI coding agents — any framework |
| **Templates** | Project scaffolds with bundled skills |
| **Tools** | AG2 tool functions and MCP servers |
| **Datasets** | Evaluation and training data |
| **Agents** | Pre-built Claude Code subagents |
| **Bundles** | Curated collections of artifacts |

## Contributing

Submit artifacts via pull request. Each artifact must include:

1. `artifact.json` — manifest following the [schema](schema/v1.json)
2. Skills that explain how to use the artifact
3. Tests (where applicable)

## License

Apache 2.0
