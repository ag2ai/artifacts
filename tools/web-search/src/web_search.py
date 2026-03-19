"""Web search and page extraction tools for AG2 agents.

Uses DuckDuckGo HTML search (no API key required) and BeautifulSoup
for clean text extraction from web pages.
"""

from __future__ import annotations

import re
import urllib.parse
from typing import Annotated

import httpx
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

_TIMEOUT = 15.0


def _extract_ddg_results(html: str, max_results: int) -> list[dict[str, str]]:
    """Parse DuckDuckGo HTML search results into structured data."""
    soup = BeautifulSoup(html, "html.parser")
    results: list[dict[str, str]] = []

    # DuckDuckGo lite/html results are in <a class="result-link"> or
    # the standard results page uses <a class="result__a">
    for link_tag in soup.select("a.result__a, a.result-link"):
        if len(results) >= max_results:
            break

        href = link_tag.get("href", "")
        title = link_tag.get_text(strip=True)

        # DuckDuckGo wraps URLs in a redirect; extract the real URL
        if "uddg=" in href:
            parsed = urllib.parse.urlparse(href)
            qs = urllib.parse.parse_qs(parsed.query)
            href = qs.get("uddg", [href])[0]

        if not href or not title:
            continue

        # Try to grab the snippet from the sibling element
        snippet_tag = link_tag.find_parent(class_="result")
        snippet = ""
        if snippet_tag:
            snippet_el = snippet_tag.select_one(
                ".result__snippet, .result-snippet"
            )
            if snippet_el:
                snippet = snippet_el.get_text(strip=True)

        results.append({"title": title, "url": href, "snippet": snippet})

    # Fallback: parse generic <a> tags from the results page if the
    # CSS-class approach found nothing (DuckDuckGo changes markup).
    if not results:
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "uddg=" in href:
                parsed = urllib.parse.urlparse(href)
                qs = urllib.parse.parse_qs(parsed.query)
                real_url = qs.get("uddg", [""])[0]
                if real_url and real_url.startswith("http"):
                    title = a_tag.get_text(strip=True) or real_url
                    results.append(
                        {"title": title, "url": real_url, "snippet": ""}
                    )
                    if len(results) >= max_results:
                        break

    return results


def web_search(
    query: Annotated[str, "The search query string"],
    max_results: Annotated[int, "Maximum number of results to return"] = 5,
) -> str:
    """Search the web using DuckDuckGo and return formatted results.

    Performs an HTTP request to DuckDuckGo's HTML search page, parses the
    results, and returns them as formatted text. No API key is required.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default 5, max 20).

    Returns:
        A formatted string of search results with titles, URLs, and snippets.
    """
    max_results = min(max(1, max_results), 20)

    params = {"q": query, "t": "h_", "ia": "web"}
    url = "https://html.duckduckgo.com/html/"

    try:
        with httpx.Client(
            headers=_HEADERS,
            timeout=_TIMEOUT,
            follow_redirects=True,
        ) as client:
            response = client.post(url, data=params)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        return f"Search request failed with status {exc.response.status_code}."
    except httpx.RequestError as exc:
        return f"Search request failed: {exc}"

    results = _extract_ddg_results(response.text, max_results)

    if not results:
        return f"No results found for: {query}"

    lines: list[str] = [f"Search results for: {query}\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']}")
        lines.append(f"   URL: {r['url']}")
        if r["snippet"]:
            lines.append(f"   {r['snippet']}")
        lines.append("")

    return "\n".join(lines).strip()


def fetch_page(
    url: Annotated[str, "The URL of the web page to fetch"],
) -> str:
    """Fetch a web page and extract its main text content.

    Downloads the page at the given URL and uses BeautifulSoup to strip
    scripts, styles, and navigation elements, returning clean readable text.

    Args:
        url: The full URL of the page to fetch.

    Returns:
        The extracted text content of the page, truncated to ~8000 characters.
    """
    max_chars = 8000

    try:
        with httpx.Client(
            headers=_HEADERS,
            timeout=_TIMEOUT,
            follow_redirects=True,
        ) as client:
            response = client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        return f"Failed to fetch {url} — HTTP {exc.response.status_code}."
    except httpx.RequestError as exc:
        return f"Failed to fetch {url}: {exc}"

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type and "text/plain" not in content_type:
        return f"Unsupported content type: {content_type}"

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "header", "footer", "aside",
                     "noscript", "iframe", "svg", "form"]):
        tag.decompose()

    # Prefer <main> or <article> if available
    main = soup.find("main") or soup.find("article") or soup.find("body")
    if main is None:
        main = soup

    text = main.get_text(separator="\n", strip=True)

    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[... content truncated]"

    if not text.strip():
        return f"No readable text content found at {url}."

    return text
