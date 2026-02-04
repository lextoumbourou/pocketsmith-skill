"""Tests for the client module."""

import pytest

from pocketsmith.client import PocketSmithClient, APIError


@pytest.fixture
def mock_credentials(monkeypatch):
    """Set mock credentials in environment."""
    monkeypatch.setenv("POCKETSMITH_DEVELOPER_KEY", "test_developer_key")


class TestPocketSmithClient:
    """Tests for PocketSmithClient class."""

    def test_get_request_success(self, mock_credentials, httpx_mock):
        """Test successful GET request."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/me",
            json={"id": 123, "login": "testuser"},
        )

        client = PocketSmithClient()
        result = client.get("/me")

        assert result == {"id": 123, "login": "testuser"}
        client.close()

    def test_get_request_with_params(self, mock_credentials, httpx_mock):
        """Test GET request with query parameters."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/users/123/transactions?start_date=2024-01-01&type=debit",
            json=[{"id": 1}, {"id": 2}],
        )

        client = PocketSmithClient()
        result = client.get("/users/123/transactions", params={"start_date": "2024-01-01", "type": "debit"})

        assert result == [{"id": 1}, {"id": 2}]
        client.close()

    def test_post_request_success(self, mock_credentials, httpx_mock):
        """Test successful POST request."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pocketsmith.com/v2/transaction_accounts/456/transactions",
            json={"id": 789, "payee": "Test Store", "amount": -50.0},
        )

        client = PocketSmithClient()
        result = client.post(
            "/transaction_accounts/456/transactions",
            json_data={"payee": "Test Store", "amount": -50.0, "date": "2024-01-15"},
        )

        assert result["id"] == 789
        assert result["payee"] == "Test Store"
        client.close()

    def test_put_request_success(self, mock_credentials, httpx_mock):
        """Test successful PUT request."""
        httpx_mock.add_response(
            method="PUT",
            url="https://api.pocketsmith.com/v2/transactions/123",
            json={"id": 123, "payee": "Updated Payee"},
        )

        client = PocketSmithClient()
        result = client.put("/transactions/123", json_data={"payee": "Updated Payee"})

        assert result["payee"] == "Updated Payee"
        client.close()

    def test_delete_request_success(self, mock_credentials, httpx_mock):
        """Test successful DELETE request (204 No Content)."""
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.pocketsmith.com/v2/transactions/123",
            status_code=204,
        )

        client = PocketSmithClient()
        result = client.delete("/transactions/123")

        assert result is None
        client.close()

    def test_api_error_with_message(self, mock_credentials, httpx_mock):
        """Test API error with error message in response."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/transactions/999",
            status_code=404,
            json={"error": "Transaction not found"},
        )

        client = PocketSmithClient()
        with pytest.raises(APIError) as exc_info:
            client.get("/transactions/999")

        assert exc_info.value.status_code == 404
        assert "Transaction not found" in exc_info.value.message
        client.close()

    def test_api_error_401_unauthorized(self, mock_credentials, httpx_mock):
        """Test 401 Unauthorized error."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/me",
            status_code=401,
            json={"error": "Invalid API key"},
        )

        client = PocketSmithClient()
        with pytest.raises(APIError) as exc_info:
            client.get("/me")

        assert exc_info.value.status_code == 401
        client.close()

    def test_api_error_plain_text(self, mock_credentials, httpx_mock):
        """Test API error with plain text response."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/me",
            status_code=500,
            text="Internal Server Error",
        )

        client = PocketSmithClient()
        with pytest.raises(APIError) as exc_info:
            client.get("/me")

        assert exc_info.value.status_code == 500
        assert "Internal Server Error" in exc_info.value.message
        client.close()

    def test_context_manager(self, mock_credentials, httpx_mock):
        """Test client works as context manager."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/me",
            json={"id": 123},
        )

        with PocketSmithClient() as client:
            result = client.get("/me")
            assert result == {"id": 123}

    def test_headers_include_developer_key(self, mock_credentials, httpx_mock):
        """Test that requests include the X-Developer-Key header."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pocketsmith.com/v2/me",
            json={"id": 123},
        )

        with PocketSmithClient() as client:
            client.get("/me")

        request = httpx_mock.get_request()
        assert request.headers["X-Developer-Key"] == "test_developer_key"
        assert request.headers["Content-Type"] == "application/json"


class TestAPIError:
    """Tests for APIError class."""

    def test_api_error_attributes(self):
        """Test APIError has correct attributes."""
        error = APIError(404, "Not found")
        assert error.status_code == 404
        assert error.message == "Not found"

    def test_api_error_str(self):
        """Test APIError string representation."""
        error = APIError(404, "Resource not found")
        assert "404" in str(error)
        assert "Resource not found" in str(error)
