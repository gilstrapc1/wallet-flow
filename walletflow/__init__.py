"""WalletFlow: digital-wallet transaction processing (COT 5480 semester project)."""

from typing import Optional

from .models import (
    AlreadyProcessedError,
    DuplicateTransactionError,
    Transaction,
    ValidationError,
)
from .processing import ProcessingQueues
from .store import TransactionStore

__all__ = [
    "WalletFlow",
    "Transaction",
    "TransactionStore",
    "ProcessingQueues",
    "ValidationError",
    "DuplicateTransactionError",
    "AlreadyProcessedError",
]


class WalletFlow:
    """Single entry point: one permanent store plus the pending-work queues."""

    def __init__(self, **queue_kwargs) -> None:
        self.store = TransactionStore()
        self.queues = ProcessingQueues(**queue_kwargs)

    def add(self, raw: dict) -> Transaction:
        """Validate, store, and queue a transaction for processing."""
        txn = self.store.add(raw)
        self.queues.enqueue(txn)
        return txn

    def find(self, txn_id: str) -> Optional[Transaction]:
        return self.store.find(txn_id)

    def process_next(self) -> Optional[Transaction]:
        return self.queues.process_next()

    def pending_count(self) -> int:
        return self.queues.pending_count()
