"""Tests for the CLI module."""

import json
import sys
from unittest.mock import patch

import pytest

from pocketsmith.cli import (
    WritesDisabledError,
    requires_write_permission,
    create_parser,
    main,
)


@pytest.fixture
def mock_credentials(monkeypatch):
    """Set mock credentials in environment."""
    monkeypatch.setenv("POCKETSMITH_DEVELOPER_KEY", "test_developer_key")


@pytest.fixture
def allow_writes(monkeypatch):
    """Enable write operations."""
    monkeypatch.setenv("POCKETSMITH_ALLOW_WRITES", "true")


class TestWriteProtection:
    """Tests for write protection decorator."""

    def test_decorator_raises_when_not_set(self, monkeypatch):
        """Test decorator raises error when POCKETSMITH_ALLOW_WRITES not set."""
        monkeypatch.delenv("POCKETSMITH_ALLOW_WRITES", raising=False)

        @requires_write_permission
        def dummy_write():
            return "success"

        with pytest.raises(WritesDisabledError) as exc_info:
            dummy_write()
        assert "POCKETSMITH_ALLOW_WRITES=true" in str(exc_info.value)

    def test_decorator_raises_when_false(self, monkeypatch):
        """Test decorator raises error when POCKETSMITH_ALLOW_WRITES is false."""
        monkeypatch.setenv("POCKETSMITH_ALLOW_WRITES", "false")

        @requires_write_permission
        def dummy_write():
            return "success"

        with pytest.raises(WritesDisabledError):
            dummy_write()

    def test_decorator_allows_when_true(self, monkeypatch):
        """Test decorator allows execution when POCKETSMITH_ALLOW_WRITES is true."""
        monkeypatch.setenv("POCKETSMITH_ALLOW_WRITES", "true")

        @requires_write_permission
        def dummy_write():
            return "success"

        assert dummy_write() == "success"

    def test_decorator_allows_when_TRUE(self, monkeypatch):
        """Test decorator is case-insensitive."""
        monkeypatch.setenv("POCKETSMITH_ALLOW_WRITES", "TRUE")

        @requires_write_permission
        def dummy_write():
            return "success"

        assert dummy_write() == "success"


class TestParser:
    """Tests for argument parser."""

    def test_parser_me_command(self):
        """Test parsing 'me' command."""
        parser = create_parser()
        args = parser.parse_args(["me"])
        assert args.command == "me"

    def test_parser_auth_status(self):
        """Test parsing 'auth status' command."""
        parser = create_parser()
        args = parser.parse_args(["auth", "status"])
        assert args.command == "auth"
        assert args.auth_command == "status"

    def test_parser_transactions_get(self):
        """Test parsing 'transactions get' command."""
        parser = create_parser()
        args = parser.parse_args(["transactions", "get", "123"])
        assert args.command == "transactions"
        assert args.transactions_command == "get"
        assert args.id == 123

    def test_parser_transactions_list_by_user(self):
        """Test parsing 'transactions list-by-user' command with filters."""
        parser = create_parser()
        args = parser.parse_args([
            "transactions", "list-by-user", "456",
            "--start-date", "2024-01-01",
            "--end-date", "2024-12-31",
            "--type", "debit",
            "--uncategorised",
        ])
        assert args.command == "transactions"
        assert args.transactions_command == "list-by-user"
        assert args.user_id == 456
        assert args.start_date == "2024-01-01"
        assert args.end_date == "2024-12-31"
        assert args.type == "debit"
        assert args.uncategorised is True

    def test_parser_transactions_update(self):
        """Test parsing 'transactions update' command."""
        parser = create_parser()
        args = parser.parse_args([
            "transactions", "update", "789",
            "--payee", "New Payee",
            "--category-id", "123",
            "--labels", "tag1,tag2",
        ])
        assert args.command == "transactions"
        assert args.transactions_command == "update"
        assert args.id == 789
        assert args.payee == "New Payee"
        assert args.category_id == 123
        assert args.labels == "tag1,tag2"

    def test_parser_transactions_create(self):
        """Test parsing 'transactions create' command."""
        parser = create_parser()
        args = parser.parse_args([
            "transactions", "create", "456",
            "--payee", "Test Store",
            "--amount", "-50.00",
            "--date", "2024-01-15",
        ])
        assert args.command == "transactions"
        assert args.transactions_command == "create"
        assert args.transaction_account_id == 456
        assert args.payee == "Test Store"
        assert args.amount == -50.00
        assert args.date == "2024-01-15"

    def test_parser_categories_list(self):
        """Test parsing 'categories list' command."""
        parser = create_parser()
        args = parser.parse_args(["categories", "list", "123"])
        assert args.command == "categories"
        assert args.categories_command == "list"
        assert args.user_id == 123

    def test_parser_categories_create(self):
        """Test parsing 'categories create' command."""
        parser = create_parser()
        args = parser.parse_args([
            "categories", "create", "123",
            "--title", "New Category",
            "--colour", "#ff0000",
            "--parent-id", "456",
        ])
        assert args.command == "categories"
        assert args.categories_command == "create"
        assert args.user_id == 123
        assert args.title == "New Category"
        assert args.colour == "#ff0000"
        assert args.parent_id == 456

    def test_parser_labels_list(self):
        """Test parsing 'labels list' command."""
        parser = create_parser()
        args = parser.parse_args(["labels", "list", "123"])
        assert args.command == "labels"
        assert args.labels_command == "list"
        assert args.user_id == 123

    def test_parser_budget_list(self):
        """Test parsing 'budget list' command."""
        parser = create_parser()
        args = parser.parse_args(["budget", "list", "123"])
        assert args.command == "budget"
        assert args.budget_command == "list"
        assert args.user_id == 123

    def test_parser_budget_summary(self):
        """Test parsing 'budget summary' command."""
        parser = create_parser()
        args = parser.parse_args([
            "budget", "summary", "123",
            "--period", "months",
            "--interval", "1",
            "--start-date", "2024-01-01",
            "--end-date", "2024-12-31",
        ])
        assert args.command == "budget"
        assert args.budget_command == "summary"
        assert args.user_id == 123
        assert args.period == "months"
        assert args.interval == 1
        assert args.start_date == "2024-01-01"
        assert args.end_date == "2024-12-31"

    def test_parser_budget_trend(self):
        """Test parsing 'budget trend' command."""
        parser = create_parser()
        args = parser.parse_args([
            "budget", "trend", "123",
            "--period", "weeks",
            "--interval", "2",
            "--start-date", "2024-01-01",
            "--end-date", "2024-06-30",
            "--categories", "1,2,3",
            "--scenarios", "4,5",
        ])
        assert args.command == "budget"
        assert args.budget_command == "trend"
        assert args.user_id == 123
        assert args.period == "weeks"
        assert args.interval == 2
        assert args.categories == "1,2,3"
        assert args.scenarios == "4,5"


class TestMainCommands:
    """Tests for main CLI commands."""

    def test_me_command(self, mock_credentials, httpx_mock, capsys):
        """Test 'me' command."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/me",
            json={"id": 123, "login": "testuser", "name": "Test User"},
        )

        with patch.object(sys, "argv", ["pocketsmith", "me"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["id"] == 123
        assert output["login"] == "testuser"

    def test_auth_status_authenticated(self, mock_credentials, httpx_mock, capsys):
        """Test 'auth status' when authenticated."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/me",
            json={"id": 123, "login": "testuser", "name": "Test User"},
        )

        with patch.object(sys, "argv", ["pocketsmith", "auth", "status"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["authenticated"] is True
        assert output["user_id"] == 123

    def test_auth_status_not_authenticated(self, monkeypatch, capsys):
        """Test 'auth status' when not authenticated."""
        monkeypatch.delenv("POCKETSMITH_DEVELOPER_KEY", raising=False)

        with patch.object(sys, "argv", ["pocketsmith", "auth", "status"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["authenticated"] is False

    def test_transactions_get(self, mock_credentials, httpx_mock, capsys):
        """Test 'transactions get' command."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/transactions/123",
            json={"id": 123, "payee": "Test Store", "amount": -50.0},
        )

        with patch.object(sys, "argv", ["pocketsmith", "transactions", "get", "123"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["id"] == 123
        assert output["payee"] == "Test Store"

    def test_transactions_list_by_user(self, mock_credentials, httpx_mock, capsys):
        """Test 'transactions list-by-user' command."""
        # Use match_headers=False and match_content=False to allow any query params
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/456/transactions?uncategorised=0&needs_review=0",
            json=[{"id": 1}, {"id": 2}, {"id": 3}],
        )

        with patch.object(sys, "argv", ["pocketsmith", "transactions", "list-by-user", "456"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert len(output) == 3

    def test_categories_list(self, mock_credentials, httpx_mock, capsys):
        """Test 'categories list' command."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/123/categories",
            json=[{"id": 1, "title": "Food"}, {"id": 2, "title": "Transport"}],
        )

        with patch.object(sys, "argv", ["pocketsmith", "categories", "list", "123"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert len(output) == 2
        assert output[0]["title"] == "Food"

    def test_labels_list(self, mock_credentials, httpx_mock, capsys):
        """Test 'labels list' command."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/123/labels",
            json=["tag1", "tag2", "tag3"],
        )

        with patch.object(sys, "argv", ["pocketsmith", "labels", "list", "123"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output == ["tag1", "tag2", "tag3"]

    def test_budget_list(self, mock_credentials, httpx_mock, capsys):
        """Test 'budget list' command."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/123/budget",
            json=[{"category": {"id": 1, "title": "Food"}, "expense": {}}],
        )

        with patch.object(sys, "argv", ["pocketsmith", "budget", "list", "123"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert len(output) == 1

    def test_budget_summary(self, mock_credentials, httpx_mock, capsys):
        """Test 'budget summary' command."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/123/budget_summary?period=months&interval=1&start_date=2024-01-01&end_date=2024-12-31",
            json={"income": {"total_actual_amount": 50000}, "expense": {"total_actual_amount": 30000}},
        )

        with patch.object(sys, "argv", [
            "pocketsmith", "budget", "summary", "123",
            "--period", "months", "--interval", "1",
            "--start-date", "2024-01-01", "--end-date", "2024-12-31"
        ]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "income" in output


class TestWriteCommands:
    """Tests for write commands with protection."""

    def test_transactions_update_blocked(self, mock_credentials, capsys, monkeypatch):
        """Test 'transactions update' blocked without write permission."""
        monkeypatch.delenv("POCKETSMITH_ALLOW_WRITES", raising=False)

        with patch.object(sys, "argv", ["pocketsmith", "transactions", "update", "123", "--payee", "New"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error = json.loads(captured.err)
        assert "POCKETSMITH_ALLOW_WRITES" in error["error"]

    def test_transactions_update_allowed(self, mock_credentials, allow_writes, httpx_mock, capsys):
        """Test 'transactions update' allowed with write permission."""
        httpx_mock.add_response(
            method="PUT",
            url="https://api.pocketsmith.com/v2/transactions/123",
            json={"id": 123, "payee": "New Payee"},
        )

        with patch.object(sys, "argv", ["pocketsmith", "transactions", "update", "123", "--payee", "New Payee"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["payee"] == "New Payee"

    def test_transactions_delete_blocked(self, mock_credentials, capsys, monkeypatch):
        """Test 'transactions delete' blocked without write permission."""
        monkeypatch.delenv("POCKETSMITH_ALLOW_WRITES", raising=False)

        with patch.object(sys, "argv", ["pocketsmith", "transactions", "delete", "123"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error = json.loads(captured.err)
        assert "POCKETSMITH_ALLOW_WRITES" in error["error"]

    def test_transactions_create_blocked(self, mock_credentials, capsys, monkeypatch):
        """Test 'transactions create' blocked without write permission."""
        monkeypatch.delenv("POCKETSMITH_ALLOW_WRITES", raising=False)

        with patch.object(sys, "argv", [
            "pocketsmith", "transactions", "create", "456",
            "--payee", "Test", "--amount", "-10", "--date", "2024-01-01"
        ]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error = json.loads(captured.err)
        assert "POCKETSMITH_ALLOW_WRITES" in error["error"]

    def test_categories_create_blocked(self, mock_credentials, capsys, monkeypatch):
        """Test 'categories create' blocked without write permission."""
        monkeypatch.delenv("POCKETSMITH_ALLOW_WRITES", raising=False)

        with patch.object(sys, "argv", [
            "pocketsmith", "categories", "create", "123", "--title", "New"
        ]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error = json.loads(captured.err)
        assert "POCKETSMITH_ALLOW_WRITES" in error["error"]

    def test_categories_update_blocked(self, mock_credentials, capsys, monkeypatch):
        """Test 'categories update' blocked without write permission."""
        monkeypatch.delenv("POCKETSMITH_ALLOW_WRITES", raising=False)

        with patch.object(sys, "argv", [
            "pocketsmith", "categories", "update", "123", "--title", "Updated"
        ]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error = json.loads(captured.err)
        assert "POCKETSMITH_ALLOW_WRITES" in error["error"]

    def test_categories_delete_blocked(self, mock_credentials, capsys, monkeypatch):
        """Test 'categories delete' blocked without write permission."""
        monkeypatch.delenv("POCKETSMITH_ALLOW_WRITES", raising=False)

        with patch.object(sys, "argv", ["pocketsmith", "categories", "delete", "123"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error = json.loads(captured.err)
        assert "POCKETSMITH_ALLOW_WRITES" in error["error"]

    def test_budget_refresh_blocked(self, mock_credentials, capsys, monkeypatch):
        """Test 'budget refresh' blocked without write permission."""
        monkeypatch.delenv("POCKETSMITH_ALLOW_WRITES", raising=False)

        with patch.object(sys, "argv", ["pocketsmith", "budget", "refresh", "123"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error = json.loads(captured.err)
        assert "POCKETSMITH_ALLOW_WRITES" in error["error"]

    def test_budget_refresh_allowed(self, mock_credentials, allow_writes, httpx_mock, capsys):
        """Test 'budget refresh' allowed with write permission."""
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.pocketsmith.com/v2/users/123/forecast_cache",
            status_code=204,
        )

        with patch.object(sys, "argv", ["pocketsmith", "budget", "refresh", "123"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["status"] == "success"


class TestErrorHandling:
    """Tests for error handling."""

    def test_api_error_handling(self, mock_credentials, httpx_mock, capsys):
        """Test API error is handled and returned as JSON."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/transactions/999",
            status_code=404,
            json={"error": "Transaction not found"},
        )

        with patch.object(sys, "argv", ["pocketsmith", "transactions", "get", "999"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error = json.loads(captured.err)
        assert error["status_code"] == 404
        assert "not found" in error["error"].lower()

    def test_missing_credentials_handling(self, monkeypatch, capsys):
        """Test missing credentials error is handled."""
        monkeypatch.delenv("POCKETSMITH_DEVELOPER_KEY", raising=False)

        with patch.object(sys, "argv", ["pocketsmith", "me"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error = json.loads(captured.err)
        assert "POCKETSMITH_DEVELOPER_KEY" in error["error"]


class TestAdditionalCommands:
    """Additional tests for CLI commands to improve coverage."""

    def test_no_command_shows_help(self, capsys):
        """Test running without command shows help."""
        with patch.object(sys, "argv", ["pocketsmith"]):
            result = main()
        assert result == 0

    def test_transactions_list_by_account(self, mock_credentials, httpx_mock, capsys):
        """Test 'transactions list-by-account' command."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/accounts/789/transactions?uncategorised=0&needs_review=0",
            json=[{"id": 1}, {"id": 2}],
        )

        with patch.object(sys, "argv", ["pocketsmith", "transactions", "list-by-account", "789"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert len(output) == 2

    def test_transactions_list_by_category(self, mock_credentials, httpx_mock, capsys):
        """Test 'transactions list-by-category' command."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/categories/1,2,3/transactions?uncategorised=0&needs_review=0",
            json=[{"id": 1}],
        )

        with patch.object(sys, "argv", ["pocketsmith", "transactions", "list-by-category", "1,2,3"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert len(output) == 1

    def test_transactions_list_by_transaction_account(self, mock_credentials, httpx_mock, capsys):
        """Test 'transactions list-by-transaction-account' command."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/transaction_accounts/999/transactions?uncategorised=0&needs_review=0",
            json=[{"id": 1}, {"id": 2}, {"id": 3}],
        )

        with patch.object(sys, "argv", ["pocketsmith", "transactions", "list-by-transaction-account", "999"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert len(output) == 3

    def test_transactions_create_allowed(self, mock_credentials, allow_writes, httpx_mock, capsys):
        """Test 'transactions create' allowed with write permission."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pocketsmith.com/v2/transaction_accounts/456/transactions",
            json={"id": 123, "payee": "Test Store", "amount": -50.0},
        )

        with patch.object(sys, "argv", [
            "pocketsmith", "transactions", "create", "456",
            "--payee", "Test Store", "--amount", "-50", "--date", "2024-01-15"
        ]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["id"] == 123

    def test_transactions_delete_allowed(self, mock_credentials, allow_writes, httpx_mock, capsys):
        """Test 'transactions delete' allowed with write permission."""
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.pocketsmith.com/v2/transactions/123",
            status_code=204,
        )

        with patch.object(sys, "argv", ["pocketsmith", "transactions", "delete", "123"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["status"] == "success"

    def test_categories_get(self, mock_credentials, httpx_mock, capsys):
        """Test 'categories get' command."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/categories/123",
            json={"id": 123, "title": "Food"},
        )

        with patch.object(sys, "argv", ["pocketsmith", "categories", "get", "123"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["title"] == "Food"

    def test_categories_create_allowed(self, mock_credentials, allow_writes, httpx_mock, capsys):
        """Test 'categories create' allowed with write permission."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pocketsmith.com/v2/users/123/categories",
            json={"id": 456, "title": "New Category"},
        )

        with patch.object(sys, "argv", [
            "pocketsmith", "categories", "create", "123", "--title", "New Category"
        ]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["title"] == "New Category"

    def test_categories_update_allowed(self, mock_credentials, allow_writes, httpx_mock, capsys):
        """Test 'categories update' allowed with write permission."""
        httpx_mock.add_response(
            method="PUT",
            url="https://api.pocketsmith.com/v2/categories/123",
            json={"id": 123, "title": "Updated Title"},
        )

        with patch.object(sys, "argv", [
            "pocketsmith", "categories", "update", "123", "--title", "Updated Title"
        ]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["title"] == "Updated Title"

    def test_categories_update_with_no_parent(self, mock_credentials, allow_writes, httpx_mock, capsys):
        """Test 'categories update' with --no-parent flag."""
        httpx_mock.add_response(
            method="PUT",
            url="https://api.pocketsmith.com/v2/categories/123",
            json={"id": 123, "parent_id": None},
        )

        with patch.object(sys, "argv", [
            "pocketsmith", "categories", "update", "123", "--no-parent"
        ]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["parent_id"] is None

    def test_categories_delete_allowed(self, mock_credentials, allow_writes, httpx_mock, capsys):
        """Test 'categories delete' allowed with write permission."""
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.pocketsmith.com/v2/categories/123",
            status_code=204,
        )

        with patch.object(sys, "argv", ["pocketsmith", "categories", "delete", "123"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["status"] == "success"

    def test_budget_trend(self, mock_credentials, httpx_mock, capsys):
        """Test 'budget trend' command."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/123/trend_analysis?period=weeks&interval=2&start_date=2024-01-01&end_date=2024-06-30&categories=1%2C2&scenarios=3%2C4",
            json=[{"period": {}}],
        )

        with patch.object(sys, "argv", [
            "pocketsmith", "budget", "trend", "123",
            "--period", "weeks", "--interval", "2",
            "--start-date", "2024-01-01", "--end-date", "2024-06-30",
            "--categories", "1,2", "--scenarios", "3,4"
        ]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert len(output) == 1

    def test_auth_status_invalid_key(self, mock_credentials, httpx_mock, capsys):
        """Test 'auth status' with invalid key returns error."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/me",
            status_code=401,
            json={"error": "Unauthorized"},
        )

        with patch.object(sys, "argv", ["pocketsmith", "auth", "status"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["authenticated"] is False


class TestParserEdgeCases:
    """Tests for parser edge cases."""

    def test_parser_transactions_list_with_all_filters(self):
        """Test parsing 'transactions list-by-user' with all filters."""
        parser = create_parser()
        args = parser.parse_args([
            "transactions", "list-by-user", "456",
            "--start-date", "2024-01-01",
            "--end-date", "2024-12-31",
            "--updated-since", "2024-01-01T00:00:00",
            "--type", "credit",
            "--uncategorised",
            "--needs-review",
            "--search", "coffee",
            "--page", "2",
        ])
        assert args.start_date == "2024-01-01"
        assert args.end_date == "2024-12-31"
        assert args.updated_since == "2024-01-01T00:00:00"
        assert args.type == "credit"
        assert args.uncategorised is True
        assert args.needs_review is True
        assert args.search == "coffee"
        assert args.page == 2

    def test_parser_categories_create_all_options(self):
        """Test parsing 'categories create' with all options."""
        parser = create_parser()
        args = parser.parse_args([
            "categories", "create", "123",
            "--title", "Test",
            "--colour", "#ff0000",
            "--parent-id", "456",
            "--is-transfer", "true",
            "--is-bill", "false",
            "--roll-up", "true",
            "--refund-behaviour", "debit_only",
        ])
        assert args.title == "Test"
        assert args.colour == "#ff0000"
        assert args.parent_id == 456
        assert args.is_transfer is True
        assert args.is_bill is False
        assert args.roll_up is True
        assert args.refund_behaviour == "debit_only"

    def test_parser_categories_update_all_options(self):
        """Test parsing 'categories update' with all options."""
        parser = create_parser()
        args = parser.parse_args([
            "categories", "update", "123",
            "--title", "Updated",
            "--colour", "#00ff00",
            "--parent-id", "789",
            "--is-transfer", "false",
            "--is-bill", "true",
            "--roll-up", "false",
            "--refund-behaviour", "credit_only",
        ])
        assert args.title == "Updated"
        assert args.parent_id == 789

    def test_parser_transactions_create_all_options(self):
        """Test parsing 'transactions create' with all options."""
        parser = create_parser()
        args = parser.parse_args([
            "transactions", "create", "456",
            "--payee", "Test Store",
            "--amount", "-50.00",
            "--date", "2024-01-15",
            "--is-transfer", "true",
            "--labels", "tag1,tag2",
            "--category-id", "789",
            "--note", "Test note",
            "--memo", "Test memo",
            "--cheque-number", "12345",
            "--needs-review", "true",
        ])
        assert args.payee == "Test Store"
        assert args.amount == -50.00
        assert args.is_transfer is True
        assert args.labels == "tag1,tag2"
        assert args.category_id == 789
        assert args.note == "Test note"
        assert args.memo == "Test memo"
        assert args.cheque_number == "12345"
        assert args.needs_review is True

    def test_parser_budget_list_with_roll_up(self):
        """Test parsing 'budget list' with roll-up option."""
        parser = create_parser()
        args = parser.parse_args([
            "budget", "list", "123",
            "--roll-up", "true",
        ])
        assert args.roll_up is True

    def test_parser_attachments_get(self):
        """Test parsing 'attachments get' command."""
        parser = create_parser()
        args = parser.parse_args(["attachments", "get", "123"])
        assert args.command == "attachments"
        assert args.attachments_command == "get"
        assert args.id == 123

    def test_parser_attachments_update(self):
        """Test parsing 'attachments update' command."""
        parser = create_parser()
        args = parser.parse_args(["attachments", "update", "123", "--title", "New Title"])
        assert args.command == "attachments"
        assert args.attachments_command == "update"
        assert args.id == 123
        assert args.title == "New Title"

    def test_parser_attachments_delete(self):
        """Test parsing 'attachments delete' command."""
        parser = create_parser()
        args = parser.parse_args(["attachments", "delete", "123"])
        assert args.command == "attachments"
        assert args.attachments_command == "delete"
        assert args.id == 123

    def test_parser_attachments_list_by_user(self):
        """Test parsing 'attachments list-by-user' command."""
        parser = create_parser()
        args = parser.parse_args(["attachments", "list-by-user", "456"])
        assert args.command == "attachments"
        assert args.attachments_command == "list-by-user"
        assert args.user_id == 456

    def test_parser_attachments_list_by_transaction(self):
        """Test parsing 'attachments list-by-transaction' command."""
        parser = create_parser()
        args = parser.parse_args(["attachments", "list-by-transaction", "789"])
        assert args.command == "attachments"
        assert args.attachments_command == "list-by-transaction"
        assert args.transaction_id == 789

    def test_parser_attachments_assign(self):
        """Test parsing 'attachments assign' command."""
        parser = create_parser()
        args = parser.parse_args(["attachments", "assign", "789", "123"])
        assert args.command == "attachments"
        assert args.attachments_command == "assign"
        assert args.transaction_id == 789
        assert args.attachment_id == 123

    def test_parser_attachments_unassign(self):
        """Test parsing 'attachments unassign' command."""
        parser = create_parser()
        args = parser.parse_args(["attachments", "unassign", "789", "123"])
        assert args.command == "attachments"
        assert args.attachments_command == "unassign"
        assert args.transaction_id == 789
        assert args.attachment_id == 123


class TestAttachmentCommands:
    """Tests for attachment CLI commands."""

    def test_attachments_get(self, mock_credentials, httpx_mock, capsys):
        """Test 'attachments get' command."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/attachments/123",
            json={"id": 123, "title": "Receipt", "type": "image"},
        )

        with patch.object(sys, "argv", ["pocketsmith", "attachments", "get", "123"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["id"] == 123
        assert output["title"] == "Receipt"

    def test_attachments_update_blocked(self, mock_credentials, capsys, monkeypatch):
        """Test 'attachments update' blocked without write permission."""
        monkeypatch.delenv("POCKETSMITH_ALLOW_WRITES", raising=False)

        with patch.object(sys, "argv", ["pocketsmith", "attachments", "update", "123", "--title", "New"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error = json.loads(captured.err)
        assert "POCKETSMITH_ALLOW_WRITES" in error["error"]

    def test_attachments_update_allowed(self, mock_credentials, allow_writes, httpx_mock, capsys):
        """Test 'attachments update' allowed with write permission."""
        httpx_mock.add_response(
            method="PUT",
            url="https://api.pocketsmith.com/v2/attachments/123",
            json={"id": 123, "title": "Updated Title"},
        )

        with patch.object(sys, "argv", ["pocketsmith", "attachments", "update", "123", "--title", "Updated Title"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["title"] == "Updated Title"

    def test_attachments_delete_blocked(self, mock_credentials, capsys, monkeypatch):
        """Test 'attachments delete' blocked without write permission."""
        monkeypatch.delenv("POCKETSMITH_ALLOW_WRITES", raising=False)

        with patch.object(sys, "argv", ["pocketsmith", "attachments", "delete", "123"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error = json.loads(captured.err)
        assert "POCKETSMITH_ALLOW_WRITES" in error["error"]

    def test_attachments_delete_allowed(self, mock_credentials, allow_writes, httpx_mock, capsys):
        """Test 'attachments delete' allowed with write permission."""
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.pocketsmith.com/v2/attachments/123",
            status_code=204,
        )

        with patch.object(sys, "argv", ["pocketsmith", "attachments", "delete", "123"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["status"] == "success"

    def test_attachments_list_by_user(self, mock_credentials, httpx_mock, capsys):
        """Test 'attachments list-by-user' command."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/456/attachments",
            json=[{"id": 1}, {"id": 2}],
        )

        with patch.object(sys, "argv", ["pocketsmith", "attachments", "list-by-user", "456"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert len(output) == 2

    def test_attachments_list_by_transaction(self, mock_credentials, httpx_mock, capsys):
        """Test 'attachments list-by-transaction' command."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/transactions/789/attachments",
            json=[{"id": 1, "title": "Receipt"}],
        )

        with patch.object(sys, "argv", ["pocketsmith", "attachments", "list-by-transaction", "789"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert len(output) == 1

    def test_attachments_assign_blocked(self, mock_credentials, capsys, monkeypatch):
        """Test 'attachments assign' blocked without write permission."""
        monkeypatch.delenv("POCKETSMITH_ALLOW_WRITES", raising=False)

        with patch.object(sys, "argv", ["pocketsmith", "attachments", "assign", "789", "123"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error = json.loads(captured.err)
        assert "POCKETSMITH_ALLOW_WRITES" in error["error"]

    def test_attachments_assign_allowed(self, mock_credentials, allow_writes, httpx_mock, capsys):
        """Test 'attachments assign' allowed with write permission."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pocketsmith.com/v2/transactions/789/attachments",
            json={"id": 123, "title": "Receipt"},
        )

        with patch.object(sys, "argv", ["pocketsmith", "attachments", "assign", "789", "123"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["id"] == 123

    def test_attachments_unassign_blocked(self, mock_credentials, capsys, monkeypatch):
        """Test 'attachments unassign' blocked without write permission."""
        monkeypatch.delenv("POCKETSMITH_ALLOW_WRITES", raising=False)

        with patch.object(sys, "argv", ["pocketsmith", "attachments", "unassign", "789", "123"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error = json.loads(captured.err)
        assert "POCKETSMITH_ALLOW_WRITES" in error["error"]

    def test_attachments_unassign_allowed(self, mock_credentials, allow_writes, httpx_mock, capsys):
        """Test 'attachments unassign' allowed with write permission."""
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.pocketsmith.com/v2/transactions/789/attachments/123",
            status_code=204,
        )

        with patch.object(sys, "argv", ["pocketsmith", "attachments", "unassign", "789", "123"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["status"] == "success"

    def test_attachments_no_subcommand_shows_help(self, mock_credentials, capsys):
        """Test running 'attachments' without subcommand shows help."""
        with patch.object(sys, "argv", ["pocketsmith", "attachments"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "attachments" in captured.out
