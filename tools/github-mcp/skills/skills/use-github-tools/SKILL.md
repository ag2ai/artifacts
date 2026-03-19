---
name: use-github-tools
description: Connect AG2 agents to GitHub via MCP for repository, issue, and code search operations
version: 1.0.0
authors:
  - ag2ai
tags:
  - github
  - mcp
  - tools
  - ag2
---

# Use GitHub MCP Tools with AG2 Agents

## Overview

The `github-mcp` server exposes GitHub operations as MCP tools that AG2 agents can call:

- **`list_repos(owner)`** — List public repositories for a GitHub user or organization.
- **`get_issue(owner, repo, number)`** — Get full details of an issue or pull request.
- **`search_code(query, language)`** — Search code across all of GitHub.

The server communicates over stdio using the Model Context Protocol and requires a `GITHUB_TOKEN` environment variable for authenticated API access.

## Prerequisites

1. A GitHub personal access token with appropriate scopes (e.g., `repo`, `read:org`).
2. Python 3.10+ with `uv` available on PATH.
3. Install dependencies:

```bash
pip install "mcp[cli]>=1.0" "httpx>=0.27"
```

## MCP Server Configuration

The server is configured in `artifact.json` with this MCP config block:

```json
{
  "command": "uv",
  "args": ["run", "--directory", "${toolDir}", "src/server.py"],
  "env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"}
}
```

You can also run the server directly for testing:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
uv run src/server.py
```

## Usage with AG2

### Using AG2's MCP tool integration

```python
import asyncio
import os

import autogen
from autogen.tools.experimental import MCPToolAdapter

# Ensure the token is set
os.environ["GITHUB_TOKEN"] = "ghp_your_token_here"

config_list = [{"model": "gpt-4o", "api_key": "YOUR_KEY"}]


async def main():
    # Create the MCP adapter pointing to the server
    mcp_adapter = MCPToolAdapter(
        command="uv",
        args=["run", "--directory", "tools/github-mcp", "src/server.py"],
        env={"GITHUB_TOKEN": os.environ["GITHUB_TOKEN"]},
    )

    # Connect and discover tools
    async with mcp_adapter:
        tools = await mcp_adapter.discover_tools()

        assistant = autogen.AssistantAgent(
            name="github_assistant",
            system_message=(
                "You are a helpful assistant with access to GitHub tools. "
                "Use them to look up repositories, issues, and search code "
                "when asked."
            ),
            llm_config={"config_list": config_list},
        )

        user_proxy = autogen.UserProxyAgent(
            name="user",
            human_input_mode="NEVER",
            code_execution_config=False,
        )

        # Register all discovered MCP tools
        for tool in tools:
            tool.register(caller=assistant, executor=user_proxy)

        user_proxy.initiate_chat(
            assistant,
            message="List the repositories for the ag2ai organization on GitHub.",
        )


asyncio.run(main())
```

### Manual tool registration (without MCP adapter)

If you want to call the GitHub API directly without the MCP server, you can
import the underlying functions and register them as standard AG2 tools:

```python
import asyncio

import autogen
from autogen import register_function

# Import the server module to access the async tool functions
from tools.github_mcp.src.server import get_issue, list_repos, search_code

config_list = [{"model": "gpt-4o", "api_key": "YOUR_KEY"}]

assistant = autogen.ConversableAgent(
    name="assistant",
    llm_config={"config_list": config_list},
)

user_proxy = autogen.ConversableAgent(
    name="user",
    human_input_mode="NEVER",
    code_execution_config=False,
)

register_function(
    list_repos,
    caller=assistant,
    executor=user_proxy,
    name="list_repos",
    description="List GitHub repositories for a user or org",
)

register_function(
    get_issue,
    caller=assistant,
    executor=user_proxy,
    name="get_issue",
    description="Get details of a GitHub issue",
)

register_function(
    search_code,
    caller=assistant,
    executor=user_proxy,
    name="search_code",
    description="Search code across GitHub repositories",
)
```

## Tool Details

### `list_repos`

| Parameter | Type  | Description                          |
|-----------|-------|--------------------------------------|
| `owner`   | `str` | GitHub username or organization name |

Returns up to 30 public repositories sorted by most recently updated, including name, description, star count, and primary language.

### `get_issue`

| Parameter | Type  | Description                     |
|-----------|-------|---------------------------------|
| `owner`   | `str` | Repository owner (user or org)  |
| `repo`    | `str` | Repository name                 |
| `number`  | `int` | Issue or pull request number    |

Returns title, state, author, creation date, labels, and body text. Works for both issues and pull requests.

### `search_code`

| Parameter  | Type            | Description                               |
|------------|-----------------|-------------------------------------------|
| `query`    | `str`           | Search query (GitHub code search syntax)  |
| `language` | `str` or `None` | Optional language filter (e.g., "python") |

Returns up to 15 results with repository name, file path, and URL. Uses the GitHub code search API.

## Authentication

The server reads `GITHUB_TOKEN` from the environment. Without a token:
- Public repository and issue endpoints work but have lower rate limits (60 requests/hour).
- Code search requires authentication.
- Private repository access requires a token with the `repo` scope.

Create a fine-grained token at https://github.com/settings/tokens with the permissions you need.

## Notes

- All tools return formatted text strings suitable for LLM consumption.
- Issue/PR bodies are truncated at 4000 characters to fit within context limits.
- The server uses async httpx for non-blocking API calls.
