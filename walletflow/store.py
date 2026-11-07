"""Permanent transaction storage keyed by ID."""

from typing import Dict, List, Optional

from .models import DuplicateTransactionError, Transaction, make_transaction


class TransactionStore:
    """Holds every transaction ever added, pending or processed.

    Backed by a dict keyed by txn_id: average O(1) insert, duplicate check,
    and lookup. Records are never removed, so processed transactions stay
    available for searching and reporting.
    """

    def __init__(self) -> None:
        self._by_id: Dict[str, Transaction] = {}
        self._next_seq = 0

    def add(self, raw: dict) -> Transaction:
        """Validate and store a transaction. Stored data is unchanged on error."""
        txn = make_transaction(raw)  # raises ValidationError
        if txn.txn_id in self._by_id:
            raise DuplicateTransactionError(f"transaction ID {txn.txn_id!r} already exists")
        txn.seq = self._next_seq
        self._next_seq += 1
        self._by_id[txn.txn_id] = txn
        return txn

    def find(self, txn_id: str) -> Optional[Transaction]:
        """Return the transaction with this ID, or None if it does not exist."""
        return self._by_id.get(txn_id)

    def all(self) -> List[Transaction]:
        return list(self._by_id.values())

    def __len__(self) -> int:
        return len(self._by_id)

    def __contains__(self, txn_id: str) -> bool:
        return txn_id in self._by_id
