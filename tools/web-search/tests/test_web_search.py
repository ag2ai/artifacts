"""Unit tests for web_search tools (HTTP calls are mocked)."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from src.web_search import fetch_page, web_search

# -- Fixtures ----------------------------------------------------------------

FAKE_DDG_HTML = """
<html><body>
<div class="result">
  <a class="result__a" href="https://duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fpage1">
    Example Page One
  </a>
  <a class="result__snippet">This is the first result snippet.</a>
</div>
<div class="result">
  <a class="result__a" href="https://duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fpage2">
    Example Page Two
  </a>
  <a class="result__snippet">Second result snippet here.</a>
</div>
</body></html>
"""

FAKE_PAGE_HTML = """
<html>
<head><style>body { color: red; }</style></head>
<body>
  <nav>Navigation links</nav>
  <main>
    <h1>Hello World</h1>
    <p>This is the main content of the page.</p>
    <p>It has multiple paragraphs.</p>
  </main>
  <footer>Footer stuff</footer>
  <script>alert('x');</script>
</body>
</html>
"""


def _mock_response(text: str, status_code: int = 200, content_type: str = "text/html"):
    """Create a mock httpx.Response."""
    resp = MagicMock()
    resp.text = text
    resp.status_code = status_code
    resp.headers = {"content-type": content_type}
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        import httpx
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=resp
        )
    return resp


# -- Tests -------------------------------------------------------------------

class TestWebSearch(unittest.TestCase):
    """Tests for the web_search function."""

    @patch("src.web_search.httpx.Client")
    def test_returns_formatted_results(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = _mock_response(FAKE_DDG_HTML)

        result = web_search("test query", max_results=5)

        assert "Search results for: test query" in result
        assert "Example Page One" in result
        assert "https://example.com/page1" in result

    @patch("src.web_search.httpx.Client")
    def test_respects_max_results(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = _mock_response(FAKE_DDG_HTML)

        result = web_search("test", max_results=1)

        # Should have at most 1 numbered result
        assert "2." not in result

    @patch("src.web_search.httpx.Client")
    def test_handles_no_results(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = _mock_response("<html><body></body></html>")

        result = web_search("xyznonexistent")

        assert "No results found" in result

    @patch("src.web_search.httpx.Client")
    def test_handles_http_error(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = _mock_response("", status_code=503)

        result = web_search("test")

        assert "failed" in result.lower()


class TestFetchPage(unittest.TestCase):
    """Tests for the fetch_page function."""

    @patch("src.web_search.httpx.Client")
    def test_extracts_main_content(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = _mock_response(FAKE_PAGE_HTML)

        result = fetch_page("https://example.com")

        assert "Hello World" in result
        assert "main content of the page" in result

    @patch("src.web_search.httpx.Client")
    def test_strips_scripts_and_nav(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = _mock_response(FAKE_PAGE_HTML)

        result = fetch_page("https://example.com")

        assert "alert" not in result
        assert "Navigation links" not in result
        assert "Footer stuff" not in result

    @patch("src.web_search.httpx.Client")
    def test_handles_http_error(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = _mock_response("", status_code=404)

        result = fetch_page("https://example.com/nope")

        assert "Failed" in result or "failed" in result

    @patch("src.web_search.httpx.Client")
    def test_unsupported_content_type(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = _mock_response(
            "binary", content_type="application/pdf"
        )

        result = fetch_page("https://example.com/file.pdf")

        assert "Unsupported content type" in result


if __name__ == "__main__":
    unittest.main()
