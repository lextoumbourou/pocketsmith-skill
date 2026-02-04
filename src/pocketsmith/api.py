"""High-level API wrapper for PocketSmith."""

from typing import Any, Optional

from .client import PocketSmithClient


class PocketSmithAPI:
    """High-level API for interacting with PocketSmith."""

    def __init__(self):
        self._client = PocketSmithClient()

    def close(self) -> None:
        """Close the API client."""
        self._client.close()

    def __enter__(self) -> "PocketSmithAPI":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    # -------------------------------------------------------------------------
    # User endpoints
    # -------------------------------------------------------------------------

    def get_me(self) -> dict[str, Any]:
        """Get the current authenticated user.

        Returns:
            User object with id, login, name, email, etc.
        """
        return self._client.get("/me")

    # -------------------------------------------------------------------------
    # Transaction endpoints
    # -------------------------------------------------------------------------

    def get_transaction(self, transaction_id: int) -> dict[str, Any]:
        """Get a single transaction by ID.

        Args:
            transaction_id: The transaction ID.

        Returns:
            Transaction object.
        """
        return self._client.get(f"/transactions/{transaction_id}")

    def update_transaction(
        self,
        transaction_id: int,
        *,
        memo: Optional[str] = None,
        cheque_number: Optional[str] = None,
        payee: Optional[str] = None,
        amount: Optional[float] = None,
        date: Optional[str] = None,
        is_transfer: Optional[bool] = None,
        category_id: Optional[int] = None,
        note: Optional[str] = None,
        needs_review: Optional[bool] = None,
        labels: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Update a transaction.

        Args:
            transaction_id: The transaction ID.
            memo: Bank memo/description.
            cheque_number: Cheque number.
            payee: Payee name.
            amount: Signed amount (negative for debits).
            date: Transaction date (YYYY-MM-DD).
            is_transfer: Whether this is a transfer.
            category_id: Category ID to assign.
            note: User note.
            needs_review: Whether transaction needs review.
            labels: List of labels to assign.

        Returns:
            Updated transaction object.
        """
        data: dict[str, Any] = {}
        if memo is not None:
            data["memo"] = memo
        if cheque_number is not None:
            data["cheque_number"] = cheque_number
        if payee is not None:
            data["payee"] = payee
        if amount is not None:
            data["amount"] = amount
        if date is not None:
            data["date"] = date
        if is_transfer is not None:
            data["is_transfer"] = is_transfer
        if category_id is not None:
            data["category_id"] = category_id
        if note is not None:
            data["note"] = note
        if needs_review is not None:
            data["needs_review"] = needs_review
        if labels is not None:
            data["labels"] = labels

        return self._client.put(f"/transactions/{transaction_id}", json_data=data)

    def delete_transaction(self, transaction_id: int) -> None:
        """Delete a transaction.

        Args:
            transaction_id: The transaction ID.
        """
        self._client.delete(f"/transactions/{transaction_id}")

    def list_user_transactions(
        self,
        user_id: int,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        updated_since: Optional[str] = None,
        uncategorised: Optional[bool] = None,
        type: Optional[str] = None,
        needs_review: Optional[bool] = None,
        search: Optional[str] = None,
        page: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """List transactions for a user.

        Args:
            user_id: The user ID.
            start_date: Start date filter (YYYY-MM-DD).
            end_date: End date filter (YYYY-MM-DD).
            updated_since: Only transactions updated since this datetime.
            uncategorised: Filter to uncategorised transactions only.
            type: Filter by type ('debit' or 'credit').
            needs_review: Filter to transactions needing review.
            search: Search term for payee/memo.
            page: Page number for pagination.

        Returns:
            List of transaction objects.
        """
        params: dict[str, Any] = {}
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if updated_since is not None:
            params["updated_since"] = updated_since
        if uncategorised is not None:
            params["uncategorised"] = 1 if uncategorised else 0
        if type is not None:
            params["type"] = type
        if needs_review is not None:
            params["needs_review"] = 1 if needs_review else 0
        if search is not None:
            params["search"] = search
        if page is not None:
            params["page"] = page

        return self._client.get(f"/users/{user_id}/transactions", params=params or None)

    def list_account_transactions(
        self,
        account_id: int,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        updated_since: Optional[str] = None,
        uncategorised: Optional[bool] = None,
        type: Optional[str] = None,
        needs_review: Optional[bool] = None,
        search: Optional[str] = None,
        page: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """List transactions for an account.

        Args:
            account_id: The account ID.
            start_date: Start date filter (YYYY-MM-DD).
            end_date: End date filter (YYYY-MM-DD).
            updated_since: Only transactions updated since this datetime.
            uncategorised: Filter to uncategorised transactions only.
            type: Filter by type ('debit' or 'credit').
            needs_review: Filter to transactions needing review.
            search: Search term for payee/memo.
            page: Page number for pagination.

        Returns:
            List of transaction objects.
        """
        params: dict[str, Any] = {}
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if updated_since is not None:
            params["updated_since"] = updated_since
        if uncategorised is not None:
            params["uncategorised"] = 1 if uncategorised else 0
        if type is not None:
            params["type"] = type
        if needs_review is not None:
            params["needs_review"] = 1 if needs_review else 0
        if search is not None:
            params["search"] = search
        if page is not None:
            params["page"] = page

        return self._client.get(f"/accounts/{account_id}/transactions", params=params or None)

    def list_category_transactions(
        self,
        category_ids: str,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        updated_since: Optional[str] = None,
        uncategorised: Optional[bool] = None,
        type: Optional[str] = None,
        needs_review: Optional[bool] = None,
        search: Optional[str] = None,
        page: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """List transactions for categories.

        Args:
            category_ids: Comma-separated category IDs.
            start_date: Start date filter (YYYY-MM-DD).
            end_date: End date filter (YYYY-MM-DD).
            updated_since: Only transactions updated since this datetime.
            uncategorised: Filter to uncategorised transactions only.
            type: Filter by type ('debit' or 'credit').
            needs_review: Filter to transactions needing review.
            search: Search term for payee/memo.
            page: Page number for pagination.

        Returns:
            List of transaction objects.
        """
        params: dict[str, Any] = {}
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if updated_since is not None:
            params["updated_since"] = updated_since
        if uncategorised is not None:
            params["uncategorised"] = 1 if uncategorised else 0
        if type is not None:
            params["type"] = type
        if needs_review is not None:
            params["needs_review"] = 1 if needs_review else 0
        if search is not None:
            params["search"] = search
        if page is not None:
            params["page"] = page

        return self._client.get(f"/categories/{category_ids}/transactions", params=params or None)

    def list_transaction_account_transactions(
        self,
        transaction_account_id: int,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        updated_since: Optional[str] = None,
        uncategorised: Optional[bool] = None,
        type: Optional[str] = None,
        needs_review: Optional[bool] = None,
        search: Optional[str] = None,
        page: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """List transactions for a transaction account.

        Args:
            transaction_account_id: The transaction account ID.
            start_date: Start date filter (YYYY-MM-DD).
            end_date: End date filter (YYYY-MM-DD).
            updated_since: Only transactions updated since this datetime.
            uncategorised: Filter to uncategorised transactions only.
            type: Filter by type ('debit' or 'credit').
            needs_review: Filter to transactions needing review.
            search: Search term for payee/memo.
            page: Page number for pagination.

        Returns:
            List of transaction objects.
        """
        params: dict[str, Any] = {}
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if updated_since is not None:
            params["updated_since"] = updated_since
        if uncategorised is not None:
            params["uncategorised"] = 1 if uncategorised else 0
        if type is not None:
            params["type"] = type
        if needs_review is not None:
            params["needs_review"] = 1 if needs_review else 0
        if search is not None:
            params["search"] = search
        if page is not None:
            params["page"] = page

        return self._client.get(
            f"/transaction_accounts/{transaction_account_id}/transactions", params=params or None
        )

    def create_transaction(
        self,
        transaction_account_id: int,
        *,
        payee: str,
        amount: float,
        date: str,
        is_transfer: Optional[bool] = None,
        labels: Optional[list[str]] = None,
        category_id: Optional[int] = None,
        note: Optional[str] = None,
        memo: Optional[str] = None,
        cheque_number: Optional[str] = None,
        needs_review: Optional[bool] = None,
    ) -> dict[str, Any]:
        """Create a transaction in a transaction account.

        Args:
            transaction_account_id: The transaction account ID.
            payee: Payee name (required).
            amount: Signed amount - negative for debits (required).
            date: Transaction date YYYY-MM-DD (required).
            is_transfer: Whether this is a transfer.
            labels: List of labels.
            category_id: Category ID.
            note: User note.
            memo: Bank memo.
            cheque_number: Cheque number.
            needs_review: Whether transaction needs review.

        Returns:
            Created transaction object.
        """
        data: dict[str, Any] = {
            "payee": payee,
            "amount": amount,
            "date": date,
        }
        if is_transfer is not None:
            data["is_transfer"] = is_transfer
        if labels is not None:
            data["labels"] = labels
        if category_id is not None:
            data["category_id"] = category_id
        if note is not None:
            data["note"] = note
        if memo is not None:
            data["memo"] = memo
        if cheque_number is not None:
            data["cheque_number"] = cheque_number
        if needs_review is not None:
            data["needs_review"] = needs_review

        return self._client.post(
            f"/transaction_accounts/{transaction_account_id}/transactions", json_data=data
        )

    # -------------------------------------------------------------------------
    # Category endpoints
    # -------------------------------------------------------------------------

    def get_category(self, category_id: int) -> dict[str, Any]:
        """Get a single category by ID.

        Args:
            category_id: The category ID.

        Returns:
            Category object with id, title, colour, children, parent_id, etc.
        """
        return self._client.get(f"/categories/{category_id}")

    def update_category(
        self,
        category_id: int,
        *,
        title: Optional[str] = None,
        colour: Optional[str] = None,
        parent_id: Optional[int] = None,
        is_transfer: Optional[bool] = None,
        is_bill: Optional[bool] = None,
        roll_up: Optional[bool] = None,
        refund_behaviour: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update a category.

        Args:
            category_id: The category ID.
            title: Category title.
            colour: CSS hex colour (e.g., '#ff0000').
            parent_id: Parent category ID (null for top-level).
            is_transfer: Whether this is a transfer category.
            is_bill: Whether this is a bill category.
            roll_up: Whether to roll up to parent category.
            refund_behaviour: Refund behaviour ('debit_only', 'credit_only', or null).

        Returns:
            Updated category object.
        """
        data: dict[str, Any] = {}
        if title is not None:
            data["title"] = title
        if colour is not None:
            data["colour"] = colour
        if parent_id is not None:
            data["parent_id"] = parent_id
        if is_transfer is not None:
            data["is_transfer"] = is_transfer
        if is_bill is not None:
            data["is_bill"] = is_bill
        if roll_up is not None:
            data["roll_up"] = roll_up
        if refund_behaviour is not None:
            data["refund_behaviour"] = refund_behaviour

        return self._client.put(f"/categories/{category_id}", json_data=data)

    def delete_category(self, category_id: int) -> None:
        """Delete a category.

        Note: This deletes all budgets within the category and uncategorizes
        all transactions assigned to it.

        Args:
            category_id: The category ID.
        """
        self._client.delete(f"/categories/{category_id}")

    def list_categories(self, user_id: int) -> list[dict[str, Any]]:
        """List all categories for a user.

        Args:
            user_id: The user ID.

        Returns:
            List of category objects.
        """
        return self._client.get(f"/users/{user_id}/categories")

    def create_category(
        self,
        user_id: int,
        *,
        title: str,
        colour: Optional[str] = None,
        parent_id: Optional[int] = None,
        is_transfer: Optional[bool] = None,
        is_bill: Optional[bool] = None,
        roll_up: Optional[bool] = None,
        refund_behaviour: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a category for a user.

        Args:
            user_id: The user ID.
            title: Category title (required).
            colour: CSS hex colour (e.g., '#ff0000').
            parent_id: Parent category ID (null for top-level).
            is_transfer: Whether this is a transfer category.
            is_bill: Whether this is a bill category.
            roll_up: Whether to roll up to parent category.
            refund_behaviour: Refund behaviour ('debit_only', 'credit_only', or null).

        Returns:
            Created category object.
        """
        data: dict[str, Any] = {"title": title}
        if colour is not None:
            data["colour"] = colour
        if parent_id is not None:
            data["parent_id"] = parent_id
        if is_transfer is not None:
            data["is_transfer"] = is_transfer
        if is_bill is not None:
            data["is_bill"] = is_bill
        if roll_up is not None:
            data["roll_up"] = roll_up
        if refund_behaviour is not None:
            data["refund_behaviour"] = refund_behaviour

        return self._client.post(f"/users/{user_id}/categories", json_data=data)
