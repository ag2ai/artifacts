"""Tests for MCP server tools."""

from src.server import calculate, get_time, greet


class TestGreet:
    def test_greet_returns_name(self) -> None:
        result = greet("Alice")
        assert "Alice" in result

    def test_greet_returns_string(self) -> None:
        result = greet("Bob")
        assert isinstance(result, str)


class TestCalculate:
    def test_addition(self) -> None:
        assert calculate("2 + 3") == "5"

    def test_multiplication(self) -> None:
        assert calculate("4 * 5") == "20"

    def test_complex_expression(self) -> None:
        assert calculate("2 + 3 * 4") == "14"

    def test_division(self) -> None:
        assert calculate("10 / 4") == "2.5"

    def test_parentheses(self) -> None:
        assert calculate("(2 + 3) * 4") == "20"

    def test_rejects_disallowed_characters(self) -> None:
        result = calculate("__import__('os')")
        assert "Error" in result

    def test_division_by_zero(self) -> None:
        result = calculate("1 / 0")
        assert "Error" in result


class TestGetTime:
    def test_returns_iso_format(self) -> None:
        result = get_time()
        # ISO-8601 dates contain "T" separating date and time
        assert "T" in result

    def test_returns_string(self) -> None:
        result = get_time()
        assert isinstance(result, str)

    def test_utc_timezone(self) -> None:
        result = get_time("UTC")
        assert "+00:00" in result
