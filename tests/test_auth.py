"""Tests for the auth module."""

import pytest

from pocketsmith import auth


class TestGetDeveloperKey:
    """Tests for get_developer_key function."""

    def test_get_developer_key_success(self, monkeypatch):
        """Test successful retrieval of developer key."""
        monkeypatch.setenv("POCKETSMITH_DEVELOPER_KEY", "test_key_123")
        key = auth.get_developer_key()
        assert key == "test_key_123"

    def test_get_developer_key_missing(self, monkeypatch):
        """Test error when developer key is not set."""
        monkeypatch.delenv("POCKETSMITH_DEVELOPER_KEY", raising=False)
        with pytest.raises(ValueError, match="POCKETSMITH_DEVELOPER_KEY"):
            auth.get_developer_key()

    def test_get_developer_key_empty(self, monkeypatch):
        """Test error when developer key is empty."""
        monkeypatch.setenv("POCKETSMITH_DEVELOPER_KEY", "")
        with pytest.raises(ValueError, match="POCKETSMITH_DEVELOPER_KEY"):
            auth.get_developer_key()


class TestIsAuthenticated:
    """Tests for is_authenticated function."""

    def test_is_authenticated_true(self, monkeypatch):
        """Test returns True when key is set."""
        monkeypatch.setenv("POCKETSMITH_DEVELOPER_KEY", "test_key")
        assert auth.is_authenticated() is True

    def test_is_authenticated_false_missing(self, monkeypatch):
        """Test returns False when key is not set."""
        monkeypatch.delenv("POCKETSMITH_DEVELOPER_KEY", raising=False)
        assert auth.is_authenticated() is False

    def test_is_authenticated_false_empty(self, monkeypatch):
        """Test returns False when key is empty."""
        monkeypatch.setenv("POCKETSMITH_DEVELOPER_KEY", "")
        assert auth.is_authenticated() is False
