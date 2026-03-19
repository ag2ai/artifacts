---
name: review-process
description: How the Code Reviewer agent conducts systematic code reviews with prioritized findings
license: Apache-2.0
---

# Code Review Process

The Code Reviewer agent performs systematic reviews of code changes, catching bugs, security issues, and quality problems before they reach production.

## Review workflow

### Step 1: Understand the change

The agent starts by running `git diff` or `git diff --staged` to see the full set of changes. It reads the entire diff before making any comments, ensuring findings are considered in context.

### Step 2: Read surrounding context

For each changed file, the agent uses Read to examine the surrounding code -- the containing function, class, and module. Changes cannot be properly evaluated in isolation.

### Step 3: Check related code

The agent uses Grep and Glob to find:

- **Callers** -- Functions that call the changed code. A signature change could break them.
- **Tests** -- Existing test files that cover the changed functionality.
- **Similar patterns** -- Other places in the codebase that follow the same pattern, to check for consistency.

### Step 4: Apply the checklist

The agent works through a structured checklist covering seven areas:

1. **Correctness** -- Does the code work? Edge cases, off-by-one errors, null handling.
2. **Naming and clarity** -- Are names descriptive? Is the code self-documenting?
3. **Duplication** -- Does this repeat existing functionality?
4. **Error handling** -- Are exceptions caught at the right level? Is cleanup guaranteed?
5. **Security** -- Input validation, SQL injection, secrets exposure, path traversal.
6. **Tests** -- Do tests exist? Do they cover happy path and error cases?
7. **Performance** -- N+1 queries, unnecessary allocations, blocking in async paths.

### Step 5: Write the review

Findings are organized into three priority levels:

| Level | Meaning | Example |
|-------|---------|---------|
| **Critical** | Must fix before merge | Bugs, security vulnerabilities, data loss |
| **Warning** | Should fix, not blocking | Missing error handling, no tests, performance |
| **Suggestion** | Optional improvement | Better naming, refactoring opportunity, style |

Each finding includes the file, line number, a description of the problem, an explanation of why it matters, and a suggested fix with code when possible.

## Principles

- **Focus on the diff** -- Review what changed, not the entire codebase. Pre-existing issues are only mentioned if directly related to the change.
- **Be specific** -- Always reference exact file and line. Show the problematic snippet.
- **Suggest fixes** -- Do not just identify problems. Show what the correct code looks like.
- **Explain the impact** -- "This will cause X when Y happens" is more useful than "This is wrong."
- **One complete pass** -- Deliver all findings at once rather than dripping comments.
- **Respect existing style** -- Follow the project's conventions rather than imposing personal preferences.
- **Acknowledge good work** -- Call out clean, well-structured, or particularly elegant implementations.
