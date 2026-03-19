---
name: run-eval
description: How to run the Agent Eval Benchmark dataset with ag2 test eval
license: Apache-2.0
---

# Running Agent Eval Benchmark

The `agent-eval-bench` dataset contains evaluation cases for testing AG2 agent capabilities. It is designed for use with the `ag2 test eval` command.

## Quick start

Run the sample split (included inline, no download required):

```bash
ag2 test eval --dataset agent-eval-bench
```

This runs the `sample` split by default, which contains 10 cases across four categories: tool-use, reasoning, coordination, and safety.

## Running the full benchmark

The full benchmark (12MB) is hosted remotely and will be downloaded on first use:

```bash
ag2 test eval --dataset agent-eval-bench --split full-bench
```

The file is cached at `~/.ag2/cache/datasets/agent-eval-bench/` after the first download.

## Filtering by category

Run only a specific category of tests:

```bash
ag2 test eval --dataset agent-eval-bench --filter category=tool-use
ag2 test eval --dataset agent-eval-bench --filter category=safety
ag2 test eval --dataset agent-eval-bench --filter difficulty=hard
```

## Assertion types

Each test case defines assertions that the eval runner checks automatically:

| Type | Description |
|------|-------------|
| `contains` | Response must contain the specified text |
| `not_contains` | Response must not contain the specified text |
| `tool_called` | The agent must have called the specified tool |
| `matches` | Response must match a regex pattern |

## Writing custom cases

Add new cases to `data/sample.yaml` following this format:

```yaml
- name: "my-custom-test"
  input: "The prompt sent to the agent"
  category: "tool-use"
  difficulty: "medium"
  assertions:
    - type: contains
      value: "expected output"
    - type: tool_called
      value: "Read"
```

## Interpreting results

The eval runner outputs a summary table after each run:

- **PASS** -- All assertions for the case were satisfied.
- **FAIL** -- One or more assertions were not satisfied. The failing assertion and actual output are shown.
- **ERROR** -- The agent encountered an error during execution (timeout, tool failure, etc.).

A healthy agent should pass all `easy` cases and most `medium` cases. The `hard` cases test advanced capabilities and a lower pass rate is expected.
