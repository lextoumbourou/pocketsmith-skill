"""Tests for the API module."""

import pytest

from pocketsmith.api import PocketSmithAPI


@pytest.fixture
def mock_credentials(monkeypatch):
    """Set mock credentials in environment."""
    monkeypatch.setenv("POCKETSMITH_DEVELOPER_KEY", "test_developer_key")


class TestPocketSmithAPI:
    """Tests for PocketSmithAPI class."""

    def test_context_manager(self, mock_credentials, httpx_mock):
        """Test API can be used as context manager."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/me",
            json={"id": 123},
        )
        with PocketSmithAPI() as api:
            result = api.get_me()
            assert result["id"] == 123

    def test_close(self, mock_credentials):
        """Test API can be closed."""
        api = PocketSmithAPI()
        api.close()  # Should not raise


class TestUserEndpoints:
    """Tests for user-related API endpoints."""

    def test_get_me(self, mock_credentials, httpx_mock):
        """Test get_me returns user info."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/me",
            json={"id": 123, "login": "testuser", "name": "Test User"},
        )
        with PocketSmithAPI() as api:
            result = api.get_me()
            assert result["id"] == 123
            assert result["login"] == "testuser"


class TestTransactionEndpoints:
    """Tests for transaction-related API endpoints."""

    def test_get_transaction(self, mock_credentials, httpx_mock):
        """Test get_transaction returns transaction."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/transactions/123",
            json={"id": 123, "payee": "Test Store", "amount": -50.0},
        )
        with PocketSmithAPI() as api:
            result = api.get_transaction(123)
            assert result["id"] == 123
            assert result["payee"] == "Test Store"

    def test_update_transaction_minimal(self, mock_credentials, httpx_mock):
        """Test update_transaction with minimal params."""
        httpx_mock.add_response(
            method="PUT",
            url="https://api.pocketsmith.com/v2/transactions/123",
            json={"id": 123, "payee": "New Payee"},
        )
        with PocketSmithAPI() as api:
            result = api.update_transaction(123, payee="New Payee")
            assert result["payee"] == "New Payee"

    def test_update_transaction_all_params(self, mock_credentials, httpx_mock):
        """Test update_transaction with all params."""
        httpx_mock.add_response(
            method="PUT",
            url="https://api.pocketsmith.com/v2/transactions/123",
            json={"id": 123, "payee": "New Payee", "amount": -100.0},
        )
        with PocketSmithAPI() as api:
            result = api.update_transaction(
                123,
                memo="Test memo",
                cheque_number="12345",
                payee="New Payee",
                amount=-100.0,
                date="2024-01-15",
                is_transfer=True,
                category_id=456,
                note="Test note",
                needs_review=False,
                labels=["tag1", "tag2"],
            )
            assert result["id"] == 123

    def test_delete_transaction(self, mock_credentials, httpx_mock):
        """Test delete_transaction."""
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.pocketsmith.com/v2/transactions/123",
            status_code=204,
        )
        with PocketSmithAPI() as api:
            api.delete_transaction(123)  # Should not raise

    def test_list_user_transactions(self, mock_credentials, httpx_mock):
        """Test list_user_transactions."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/456/transactions",
            json=[{"id": 1}, {"id": 2}],
        )
        with PocketSmithAPI() as api:
            result = api.list_user_transactions(456)
            assert len(result) == 2

    def test_list_user_transactions_with_filters(self, mock_credentials, httpx_mock):
        """Test list_user_transactions with all filters."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/456/transactions?start_date=2024-01-01&end_date=2024-12-31&updated_since=2024-01-01T00%3A00%3A00&uncategorised=1&type=debit&needs_review=1&search=coffee&page=2",
            json=[{"id": 1}],
        )
        with PocketSmithAPI() as api:
            result = api.list_user_transactions(
                456,
                start_date="2024-01-01",
                end_date="2024-12-31",
                updated_since="2024-01-01T00:00:00",
                uncategorised=True,
                type="debit",
                needs_review=True,
                search="coffee",
                page=2,
            )
            assert len(result) == 1

    def test_list_account_transactions(self, mock_credentials, httpx_mock):
        """Test list_account_transactions."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/accounts/789/transactions",
            json=[{"id": 1}, {"id": 2}],
        )
        with PocketSmithAPI() as api:
            result = api.list_account_transactions(789)
            assert len(result) == 2

    def test_list_account_transactions_with_filters(self, mock_credentials, httpx_mock):
        """Test list_account_transactions with filters."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/accounts/789/transactions?start_date=2024-01-01&end_date=2024-12-31&updated_since=2024-01-01T00%3A00%3A00&uncategorised=0&type=credit&needs_review=0&search=test&page=1",
            json=[{"id": 1}],
        )
        with PocketSmithAPI() as api:
            result = api.list_account_transactions(
                789,
                start_date="2024-01-01",
                end_date="2024-12-31",
                updated_since="2024-01-01T00:00:00",
                uncategorised=False,
                type="credit",
                needs_review=False,
                search="test",
                page=1,
            )
            assert len(result) == 1

    def test_list_category_transactions(self, mock_credentials, httpx_mock):
        """Test list_category_transactions."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/categories/1,2,3/transactions",
            json=[{"id": 1}, {"id": 2}],
        )
        with PocketSmithAPI() as api:
            result = api.list_category_transactions("1,2,3")
            assert len(result) == 2

    def test_list_category_transactions_with_filters(self, mock_credentials, httpx_mock):
        """Test list_category_transactions with filters."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/categories/1,2/transactions?start_date=2024-01-01&end_date=2024-06-30&updated_since=2024-01-01T00%3A00%3A00&uncategorised=1&type=debit&needs_review=1&search=food&page=3",
            json=[{"id": 1}],
        )
        with PocketSmithAPI() as api:
            result = api.list_category_transactions(
                "1,2",
                start_date="2024-01-01",
                end_date="2024-06-30",
                updated_since="2024-01-01T00:00:00",
                uncategorised=True,
                type="debit",
                needs_review=True,
                search="food",
                page=3,
            )
            assert len(result) == 1

    def test_list_transaction_account_transactions(self, mock_credentials, httpx_mock):
        """Test list_transaction_account_transactions."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/transaction_accounts/999/transactions",
            json=[{"id": 1}, {"id": 2}, {"id": 3}],
        )
        with PocketSmithAPI() as api:
            result = api.list_transaction_account_transactions(999)
            assert len(result) == 3

    def test_list_transaction_account_transactions_with_filters(self, mock_credentials, httpx_mock):
        """Test list_transaction_account_transactions with filters."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/transaction_accounts/999/transactions?start_date=2024-02-01&end_date=2024-02-28&updated_since=2024-02-01T00%3A00%3A00&uncategorised=0&type=credit&needs_review=0&search=test&page=1",
            json=[{"id": 1}],
        )
        with PocketSmithAPI() as api:
            result = api.list_transaction_account_transactions(
                999,
                start_date="2024-02-01",
                end_date="2024-02-28",
                updated_since="2024-02-01T00:00:00",
                uncategorised=False,
                type="credit",
                needs_review=False,
                search="test",
                page=1,
            )
            assert len(result) == 1

    def test_create_transaction_minimal(self, mock_credentials, httpx_mock):
        """Test create_transaction with minimal params."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pocketsmith.com/v2/transaction_accounts/456/transactions",
            json={"id": 123, "payee": "Test Store", "amount": -50.0, "date": "2024-01-15"},
        )
        with PocketSmithAPI() as api:
            result = api.create_transaction(
                456,
                payee="Test Store",
                amount=-50.0,
                date="2024-01-15",
            )
            assert result["id"] == 123

    def test_create_transaction_all_params(self, mock_credentials, httpx_mock):
        """Test create_transaction with all params."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pocketsmith.com/v2/transaction_accounts/456/transactions",
            json={"id": 123, "payee": "Test Store"},
        )
        with PocketSmithAPI() as api:
            result = api.create_transaction(
                456,
                payee="Test Store",
                amount=-50.0,
                date="2024-01-15",
                is_transfer=True,
                labels=["tag1", "tag2"],
                category_id=789,
                note="Test note",
                memo="Test memo",
                cheque_number="12345",
                needs_review=True,
            )
            assert result["id"] == 123


class TestCategoryEndpoints:
    """Tests for category-related API endpoints."""

    def test_get_category(self, mock_credentials, httpx_mock):
        """Test get_category returns category."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/categories/123",
            json={"id": 123, "title": "Food"},
        )
        with PocketSmithAPI() as api:
            result = api.get_category(123)
            assert result["id"] == 123
            assert result["title"] == "Food"

    def test_update_category_minimal(self, mock_credentials, httpx_mock):
        """Test update_category with minimal params."""
        httpx_mock.add_response(
            method="PUT",
            url="https://api.pocketsmith.com/v2/categories/123",
            json={"id": 123, "title": "Updated Food"},
        )
        with PocketSmithAPI() as api:
            result = api.update_category(123, title="Updated Food")
            assert result["title"] == "Updated Food"

    def test_update_category_all_params(self, mock_credentials, httpx_mock):
        """Test update_category with all params."""
        httpx_mock.add_response(
            method="PUT",
            url="https://api.pocketsmith.com/v2/categories/123",
            json={"id": 123, "title": "Updated"},
        )
        with PocketSmithAPI() as api:
            result = api.update_category(
                123,
                title="Updated",
                colour="#ff0000",
                parent_id=456,
                is_transfer=True,
                is_bill=False,
                roll_up=True,
                refund_behaviour="debit_only",
            )
            assert result["id"] == 123

    def test_update_category_remove_parent(self, mock_credentials, httpx_mock):
        """Test update_category to make top-level (parent_id=None)."""
        httpx_mock.add_response(
            method="PUT",
            url="https://api.pocketsmith.com/v2/categories/123",
            json={"id": 123, "parent_id": None},
        )
        with PocketSmithAPI() as api:
            result = api.update_category(123, parent_id=None)
            assert result["parent_id"] is None

    def test_delete_category(self, mock_credentials, httpx_mock):
        """Test delete_category."""
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.pocketsmith.com/v2/categories/123",
            status_code=204,
        )
        with PocketSmithAPI() as api:
            api.delete_category(123)  # Should not raise

    def test_list_categories(self, mock_credentials, httpx_mock):
        """Test list_categories."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/456/categories",
            json=[{"id": 1, "title": "Food"}, {"id": 2, "title": "Transport"}],
        )
        with PocketSmithAPI() as api:
            result = api.list_categories(456)
            assert len(result) == 2

    def test_create_category_minimal(self, mock_credentials, httpx_mock):
        """Test create_category with minimal params."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pocketsmith.com/v2/users/456/categories",
            json={"id": 123, "title": "New Category"},
        )
        with PocketSmithAPI() as api:
            result = api.create_category(456, title="New Category")
            assert result["title"] == "New Category"

    def test_create_category_all_params(self, mock_credentials, httpx_mock):
        """Test create_category with all params."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pocketsmith.com/v2/users/456/categories",
            json={"id": 123, "title": "New Category"},
        )
        with PocketSmithAPI() as api:
            result = api.create_category(
                456,
                title="New Category",
                colour="#00ff00",
                parent_id=789,
                is_transfer=False,
                is_bill=True,
                roll_up=False,
                refund_behaviour="credit_only",
            )
            assert result["id"] == 123


class TestLabelEndpoints:
    """Tests for label-related API endpoints."""

    def test_list_labels(self, mock_credentials, httpx_mock):
        """Test list_labels."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/123/labels",
            json=["tag1", "tag2", "tag3"],
        )
        with PocketSmithAPI() as api:
            result = api.list_labels(123)
            assert result == ["tag1", "tag2", "tag3"]


class TestBudgetEndpoints:
    """Tests for budget-related API endpoints."""

    def test_list_budget(self, mock_credentials, httpx_mock):
        """Test list_budget."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/123/budget",
            json=[{"category": {"id": 1}}],
        )
        with PocketSmithAPI() as api:
            result = api.list_budget(123)
            assert len(result) == 1

    def test_list_budget_with_roll_up(self, mock_credentials, httpx_mock):
        """Test list_budget with roll_up param."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/123/budget?roll_up=1",
            json=[{"category": {"id": 1}}],
        )
        with PocketSmithAPI() as api:
            result = api.list_budget(123, roll_up=True)
            assert len(result) == 1

    def test_list_budget_with_roll_up_false(self, mock_credentials, httpx_mock):
        """Test list_budget with roll_up=False."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/123/budget?roll_up=0",
            json=[{"category": {"id": 1}}],
        )
        with PocketSmithAPI() as api:
            result = api.list_budget(123, roll_up=False)
            assert len(result) == 1

    def test_get_budget_summary(self, mock_credentials, httpx_mock):
        """Test get_budget_summary."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/123/budget_summary?period=months&interval=1&start_date=2024-01-01&end_date=2024-12-31",
            json={"income": {}, "expense": {}},
        )
        with PocketSmithAPI() as api:
            result = api.get_budget_summary(
                123,
                period="months",
                interval=1,
                start_date="2024-01-01",
                end_date="2024-12-31",
            )
            assert "income" in result

    def test_get_trend_analysis(self, mock_credentials, httpx_mock):
        """Test get_trend_analysis."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/123/trend_analysis?period=weeks&interval=2&start_date=2024-01-01&end_date=2024-06-30&categories=1%2C2%2C3&scenarios=4%2C5",
            json=[{"period": {}}],
        )
        with PocketSmithAPI() as api:
            result = api.get_trend_analysis(
                123,
                period="weeks",
                interval=2,
                start_date="2024-01-01",
                end_date="2024-06-30",
                categories="1,2,3",
                scenarios="4,5",
            )
            assert len(result) == 1

    def test_delete_forecast_cache(self, mock_credentials, httpx_mock):
        """Test delete_forecast_cache."""
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.pocketsmith.com/v2/users/123/forecast_cache",
            status_code=204,
        )
        with PocketSmithAPI() as api:
            api.delete_forecast_cache(123)  # Should not raise


class TestAttachmentEndpoints:
    """Tests for attachment-related API endpoints."""

    def test_get_attachment(self, mock_credentials, httpx_mock):
        """Test get_attachment returns attachment."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/attachments/123",
            json={
                "id": 123,
                "title": "Receipt",
                "file_name": "receipt.jpg",
                "type": "image",
                "content_type": "image/jpeg",
            },
        )
        with PocketSmithAPI() as api:
            result = api.get_attachment(123)
            assert result["id"] == 123
            assert result["title"] == "Receipt"

    def test_update_attachment(self, mock_credentials, httpx_mock):
        """Test update_attachment."""
        httpx_mock.add_response(
            method="PUT",
            url="https://api.pocketsmith.com/v2/attachments/123",
            json={"id": 123, "title": "Updated Title"},
        )
        with PocketSmithAPI() as api:
            result = api.update_attachment(123, title="Updated Title")
            assert result["title"] == "Updated Title"

    def test_update_attachment_no_title(self, mock_credentials, httpx_mock):
        """Test update_attachment with no params sends empty body."""
        httpx_mock.add_response(
            method="PUT",
            url="https://api.pocketsmith.com/v2/attachments/123",
            json={"id": 123, "title": "Original"},
        )
        with PocketSmithAPI() as api:
            result = api.update_attachment(123)
            assert result["id"] == 123

    def test_delete_attachment(self, mock_credentials, httpx_mock):
        """Test delete_attachment."""
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.pocketsmith.com/v2/attachments/123",
            status_code=204,
        )
        with PocketSmithAPI() as api:
            api.delete_attachment(123)  # Should not raise

    def test_list_user_attachments(self, mock_credentials, httpx_mock):
        """Test list_user_attachments."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/456/attachments",
            json=[{"id": 1, "title": "Receipt 1"}, {"id": 2, "title": "Receipt 2"}],
        )
        with PocketSmithAPI() as api:
            result = api.list_user_attachments(456)
            assert len(result) == 2

    def test_list_transaction_attachments(self, mock_credentials, httpx_mock):
        """Test list_transaction_attachments."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/transactions/789/attachments",
            json=[{"id": 1, "title": "Invoice"}],
        )
        with PocketSmithAPI() as api:
            result = api.list_transaction_attachments(789)
            assert len(result) == 1

    def test_assign_transaction_attachment(self, mock_credentials, httpx_mock):
        """Test assign_transaction_attachment."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pocketsmith.com/v2/transactions/789/attachments",
            json={"id": 123, "title": "Receipt"},
        )
        with PocketSmithAPI() as api:
            result = api.assign_transaction_attachment(789, 123)
            assert result["id"] == 123

    def test_unassign_transaction_attachment(self, mock_credentials, httpx_mock):
        """Test unassign_transaction_attachment."""
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.pocketsmith.com/v2/transactions/789/attachments/123",
            status_code=204,
        )
        with PocketSmithAPI() as api:
            api.unassign_transaction_attachment(789, 123)  # Should not raise
