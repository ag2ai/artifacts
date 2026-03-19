---
name: research-methodology
description: How the Research Analyst agent conducts research, evaluates sources, and produces structured reports
license: Apache-2.0
---

# Research Methodology

The Research Analyst agent follows a systematic methodology to produce reliable, well-sourced research reports.

## Research phases

### 1. Scoping

Before any search begins, the agent defines:

- **Topic boundaries** -- What is in scope and what is not.
- **Depth requirement** -- Surface-level overview vs. deep technical analysis.
- **Output expectations** -- Report length, audience, and required sections.

If the user's request is ambiguous, the agent asks clarifying questions before proceeding.

### 2. Broad search

The agent uses WebSearch with multiple query variations to find a diverse set of sources:

- Rephrase the topic using synonyms and related terms.
- Search for both supporting and opposing viewpoints.
- Look for primary sources (research papers, official docs) and secondary sources (analysis, commentary).
- Target different content types: articles, documentation, forum discussions, code repositories.

### 3. Deep reading

For the most promising results, the agent uses WebFetch to read full pages and extract:

- Key statistics and data points.
- Direct quotes from domain experts.
- Methodology details (for research papers).
- Publication dates and author credentials.

### 4. Cross-referencing

Every factual claim is verified against at least two independent sources:

- If multiple sources agree, the claim is marked **High confidence**.
- If only one source supports it, the claim is marked **Medium confidence** with a note.
- If sources contradict each other, both positions are presented with context.

### 5. Synthesis

The agent identifies patterns across sources:

- Common themes and areas of consensus.
- Active debates and unresolved questions.
- Gaps in available information.
- Emerging trends that multiple sources hint at.

### 6. Report writing

The final report follows a fixed structure: Executive Summary, Key Findings, Detailed Analysis, Sources, and Confidence Assessment. Every factual claim includes an inline citation.

## Source evaluation criteria

The agent ranks sources using these factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Authority | High | Is the author or organization a recognized expert? |
| Recency | High | When was the content published or last updated? |
| Evidence | Medium | Does the source cite its own references? |
| Objectivity | Medium | Does the source acknowledge limitations and counterarguments? |
| Corroboration | High | Do other independent sources agree? |

## When to use local tools

If the research topic relates to code in the current project, the agent supplements web research with local analysis:

- **Grep** to find relevant patterns, imports, and usage.
- **Read** to examine specific files in detail.
- **Glob** to understand project structure.
- **Bash** to run commands like `git log` for project history.

This is especially useful for questions about the project's architecture, dependencies, or implementation details.
