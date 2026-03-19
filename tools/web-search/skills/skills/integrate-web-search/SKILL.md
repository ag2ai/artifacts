---
name: integrate-web-search
description: Register and use web search tools with AG2 agents to search the web and extract page content
version: 1.0.0
authors:
  - ag2ai
tags:
  - web
  - search
  - tools
  - ag2
---

# Integrate Web Search Tools with AG2 Agents

## Overview

The `web-search` tool provides two functions for AG2 agents:

- **`web_search(query, max_results)`** — Search the web via DuckDuckGo (no API key needed) and return formatted results with titles, URLs, and snippets.
- **`fetch_page(url)`** — Fetch a web page and extract clean, readable text content using BeautifulSoup.

## Installation

Install the required dependencies:

```bash
pip install httpx>=0.27 beautifulsoup4>=4.12
```

## Usage

### Register tools with an AG2 agent

```python
import autogen

from tools.web_search import fetch_page, web_search

# Configure the LLM
config_list = [{"model": "gpt-4o", "api_key": "YOUR_KEY"}]

assistant = autogen.AssistantAgent(
    name="research_assistant",
    llm_config={"config_list": config_list},
)

user_proxy = autogen.UserProxyAgent(
    name="user",
    human_input_mode="NEVER",
    code_execution_config=False,
)

# Register both tools with the agent
assistant.register_for_llm(description="Search the web using DuckDuckGo")(web_search)
assistant.register_for_llm(description="Fetch and extract text from a URL")(fetch_page)
user_proxy.register_for_execution()(web_search)
user_proxy.register_for_execution()(fetch_page)
```

### Complete working example

```python
import autogen

from tools.web_search import fetch_page, web_search

config_list = [{"model": "gpt-4o", "api_key": "YOUR_KEY"}]

assistant = autogen.AssistantAgent(
    name="web_researcher",
    system_message=(
        "You are a helpful research assistant. Use the web_search tool to "
        "find information, then use fetch_page to read the most relevant "
        "results. Summarize your findings clearly."
    ),
    llm_config={"config_list": config_list},
)

user_proxy = autogen.UserProxyAgent(
    name="user",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config=False,
)

# Register tools
assistant.register_for_llm(description="Search the web using DuckDuckGo")(web_search)
assistant.register_for_llm(description="Fetch and extract text from a URL")(fetch_page)
user_proxy.register_for_execution()(web_search)
user_proxy.register_for_execution()(fetch_page)

# Start the conversation
user_proxy.initiate_chat(
    assistant,
    message="Search the web for 'AG2 multi-agent framework' and summarize what you find.",
)
```

### Using with ConversableAgent and tool decorator

```python
import autogen
from autogen import register_function

from tools.web_search import fetch_page, web_search

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
    web_search,
    caller=assistant,
    executor=user_proxy,
    name="web_search",
    description="Search the web using DuckDuckGo and return results",
)

register_function(
    fetch_page,
    caller=assistant,
    executor=user_proxy,
    name="fetch_page",
    description="Fetch a web page and extract its text content",
)
```

## Tool Details

### `web_search`

| Parameter     | Type  | Default | Description                        |
|---------------|-------|---------|------------------------------------|
| `query`       | `str` | —       | The search query string            |
| `max_results` | `int` | `5`     | Maximum results to return (1–20)   |

Returns a formatted string with numbered results including title, URL, and snippet.

### `fetch_page`

| Parameter | Type  | Default | Description               |
|-----------|-------|---------|---------------------------|
| `url`     | `str` | —       | The URL of the page to fetch |

Returns extracted text content (up to ~8000 characters). Strips scripts, styles, navigation, headers, and footers for clean output.

## Notes

- No API keys are required for web search (uses DuckDuckGo HTML search).
- `fetch_page` respects a 15-second timeout and follows redirects.
- Content is truncated at ~8000 characters to stay within LLM context limits.
