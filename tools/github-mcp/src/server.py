"""GitHub MCP server providing repository, issue, and code search tools.

Runs as a stdio-based MCP server using FastMCP. Requires a GITHUB_TOKEN
environment variable for authenticated access to the GitHub API.
"""

from __future__ import annotations

import os
import sys

import httpx
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "github-mcp",
    description="GitHub operations — repos, issues, pull requests, and code search",
)

_GITHUB_API = "https://api.github.com"
_TIMEOUT = 15.0


def _get_headers() -> dict[str, str]:
    """Build request headers with optional authentication."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ag2-github-mcp/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def _github_get(path: str, params: dict[str, str] | None = None) -> dict | list:
    """Make an authenticated GET request to the GitHub API."""
    async with httpx.AsyncClient(
        base_url=_GITHUB_API,
        headers=_get_headers(),
        timeout=_TIMEOUT,
    ) as client:
        response = await client.get(path, params=params)
        response.raise_for_status()
        return response.json()


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_repos(owner: str) -> str:
    """List public GitHub repositories for a user or organization.

    Args:
        owner: GitHub username or organization name.

    Returns:
        Formatted list of repositories with name, description, stars, and
        language.
    """
    try:
        repos = await _github_get(
            f"/users/{owner}/repos",
            params={"sort": "updated", "per_page": "30", "type": "public"},
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return f"User or organization '{owner}' not found."
        return f"GitHub API error: HTTP {exc.response.status_code}"
    except httpx.RequestError as exc:
        return f"Request failed: {exc}"

    if not repos:
        return f"No public repositories found for '{owner}'."

    lines: list[str] = [f"Public repositories for {owner}:\n"]
    for repo in repos:
        name = repo.get("full_name", repo.get("name", "unknown"))
        desc = repo.get("description") or "No description"
        stars = repo.get("stargazers_count", 0)
        lang = repo.get("language") or "—"
        lines.append(f"  {name}")
        lines.append(f"    {desc}")
        lines.append(f"    Stars: {stars}  |  Language: {lang}")
        lines.append("")

    return "\n".join(lines).strip()


@mcp.tool()
async def get_issue(owner: str, repo: str, number: int) -> str:
    """Get details of a GitHub issue or pull request.

    Args:
        owner: Repository owner (user or org).
        repo: Repository name.
        number: Issue or pull request number.

    Returns:
        Formatted issue details including title, state, author, labels, and
        body.
    """
    try:
        issue = await _github_get(f"/repos/{owner}/{repo}/issues/{number}")
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return f"Issue #{number} not found in {owner}/{repo}."
        return f"GitHub API error: HTTP {exc.response.status_code}"
    except httpx.RequestError as exc:
        return f"Request failed: {exc}"

    title = issue.get("title", "Untitled")
    state = issue.get("state", "unknown")
    user = issue.get("user", {}).get("login", "unknown")
    created = issue.get("created_at", "")[:10]
    labels = ", ".join(l.get("name", "") for l in issue.get("labels", [])) or "none"
    body = issue.get("body") or "No description provided."

    # Truncate very long bodies
    if len(body) > 4000:
        body = body[:4000] + "\n\n[... body truncated]"

    is_pr = "pull_request" in issue
    kind = "Pull Request" if is_pr else "Issue"

    lines = [
        f"{kind} #{number}: {title}",
        f"State: {state}  |  Author: {user}  |  Created: {created}",
        f"Labels: {labels}",
        "",
        body,
    ]

    return "\n".join(lines)


@mcp.tool()
async def search_code(query: str, language: str | None = None) -> str:
    """Search code across GitHub repositories.

    Args:
        query: The search query (GitHub code search syntax).
        language: Optional language filter (e.g. 'python', 'rust').

    Returns:
        Formatted search results with file paths, repository names, and
        matching text snippets.
    """
    q = query
    if language:
        q += f" language:{language}"

    try:
        data = await _github_get("/search/code", params={"q": q, "per_page": "15"})
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 422:
            return "Invalid search query. Check GitHub code search syntax."
        if exc.response.status_code == 403:
            return "Rate limit exceeded. Set GITHUB_TOKEN for higher limits."
        return f"GitHub API error: HTTP {exc.response.status_code}"
    except httpx.RequestError as exc:
        return f"Request failed: {exc}"

    items = data.get("items", [])
    total = data.get("total_count", 0)

    if not items:
        return f"No code results found for: {query}"

    lines: list[str] = [f"Code search results ({total} total) for: {query}\n"]
    for item in items:
        repo_name = item.get("repository", {}).get("full_name", "unknown")
        path = item.get("path", "unknown")
        html_url = item.get("html_url", "")

        # text_matches may be present if Accept header includes
        # application/vnd.github.text-match+json, but it is optional.
        fragments = ""
        for match in item.get("text_matches", []):
            fragments += match.get("fragment", "")

        lines.append(f"  {repo_name}: {path}")
        if html_url:
            lines.append(f"    {html_url}")
        if fragments:
            snippet = fragments[:300].replace("\n", " ")
            lines.append(f"    ...{snippet}...")
        lines.append("")

    return "\n".join(lines).strip()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
