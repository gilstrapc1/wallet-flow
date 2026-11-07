"""Pending-work queues: FIFO for ordinary payments, priority heap for urgent ones."""

import heapq
from collections import deque
from datetime import datetime
from typing import Callable, Deque, List, Optional, Tuple

from .models import STATUS_PENDING, STATUS_PROCESSED, AlreadyProcessedError, Transaction


class ProcessingQueues:
    """Holds pending work only; the store keeps the permanent records.

    - Ordinary: collections.deque, append / popleft are O(1) -> first in, first out.
    - Urgent: heapq min-heap of (-priority, seq, txn). Negating priority makes the
      highest priority pop first; seq (arrival order) breaks ties, so equal
      priorities are processed first in, first out. Push / pop are O(log n).
    Urgent work is always processed before ordinary work.
    """

    def __init__(self, clock: Callable[[], datetime] = datetime.now) -> None:
        self._ordinary: Deque[Transaction] = deque()
        self._urgent: List[Tuple[int, int, Transaction]] = []
        self._clock = clock

    def enqueue(self, txn: Transaction) -> None:
        if txn.status != STATUS_PENDING:
            raise AlreadyProcessedError(f"transaction {txn.txn_id!r} is not pending")
        if txn.urgent:
            heapq.heappush(self._urgent, (-txn.priority, txn.seq, txn))
        else:
            self._ordinary.append(txn)

    def _pop_next(self) -> Optional[Transaction]:
        if self._urgent:
            return heapq.heappop(self._urgent)[2]
        if self._ordinary:
            return self._ordinary.popleft()
        return None

    def process_next(self) -> Optional[Transaction]:
        """Process and return the next pending transaction, or None if nothing is pending.

        A transaction already marked processed is skipped, so nothing is
        processed twice even if it somehow ended up queued again.
        """
        while True:
            txn = self._pop_next()
            if txn is None:
                return None
            if txn.status == STATUS_PROCESSED:
                continue
            txn.status = STATUS_PROCESSED
            txn.processed_at = self._clock()
            return txn

    def pending_count(self) -> int:
        return len(self._urgent) + len(self._ordinary)

    def urgent_count(self) -> int:
        return len(self._urgent)

    def ordinary_count(self) -> int:
        return len(self._ordinary)
