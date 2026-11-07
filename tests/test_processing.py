"""Ordinary FIFO and urgent-priority processing tests."""

import unittest

from walletflow import WalletFlow
from walletflow.models import STATUS_PROCESSED
from walletflow.sample_data import EXPECTED_PROCESSING_ORDER, SAMPLE_TRANSACTIONS

from .helpers import check


def txn(txn_id, urgent=False, priority=1, minute=0):
    return {
        "txn_id": txn_id,
        "amount_cents": 1000,
        "txn_type": "purchase",
        "urgent": urgent,
        "priority": priority,
        "category": "food",
        "arrival_time": f"2026-11-02T08:{minute:02d}:00",
    }


def drain(wf):
    order = []
    while (t := wf.process_next()) is not None:
        order.append(t.txn_id)
    return order


class TestOrdinaryFifo(unittest.TestCase):
    def test_ordinary_processed_in_arrival_order(self):
        wf = WalletFlow()
        for i, tid in enumerate(["A1", "A2", "A3"]):
            wf.add(txn(tid, minute=i))
        check(self, "ordinary payments are first in, first out", "add A1, A2, A3 (all ordinary)",
              ["A1", "A2", "A3"], drain(wf))

    def test_processing_updates_status_and_keeps_record(self):
        wf = WalletFlow()
        wf.add(txn("A1"))
        processed = wf.process_next()
        found = wf.find("A1")
        check(self, "status becomes processed; record still findable; nothing pending",
              "add A1, process once",
              (STATUS_PROCESSED, True, 0, 1),
              (found.status, processed is found, wf.pending_count(), len(wf.store)))

    def test_process_when_nothing_pending(self):
        wf = WalletFlow()
        check(self, "processing an empty queue returns None", "process_next() on empty system",
              None, wf.process_next())

    def test_transaction_not_processed_twice(self):
        wf = WalletFlow()
        wf.add(txn("A1"))
        wf.process_next()
        check(self, "a processed transaction is not processed again", "process A1, then process again",
              None, wf.process_next())


class TestUrgent(unittest.TestCase):
    def test_urgent_before_ordinary(self):
        wf = WalletFlow()
        wf.add(txn("O1", minute=0))
        wf.add(txn("U1", urgent=True, priority=1, minute=1))
        check(self, "urgent is processed before an earlier ordinary payment",
              "add O1 (ordinary), then U1 (urgent p1)", ["U1", "O1"], drain(wf))

    def test_higher_priority_first(self):
        wf = WalletFlow()
        wf.add(txn("P1", urgent=True, priority=1, minute=0))
        wf.add(txn("P2", urgent=True, priority=2, minute=1))
        wf.add(txn("P3", urgent=True, priority=3, minute=2))
        check(self, "urgent priorities 3, 2, 1 in that order", "add P1, P2, P3 (urgent)",
              ["P3", "P2", "P1"], drain(wf))

    def test_equal_priority_uses_arrival_order(self):
        wf = WalletFlow()
        wf.add(txn("E1", urgent=True, priority=2, minute=0))
        wf.add(txn("E2", urgent=True, priority=2, minute=1))
        wf.add(txn("E3", urgent=True, priority=2, minute=2))
        check(self, "equal urgent priorities follow arrival order", "add E1, E2, E3 (urgent p2)",
              ["E1", "E2", "E3"], drain(wf))


class TestSampleData(unittest.TestCase):
    def test_full_sample_processing_order(self):
        wf = WalletFlow()
        for raw in SAMPLE_TRANSACTIONS:
            wf.add(raw)
        order = drain(wf)
        all_processed = all(t.status == STATUS_PROCESSED for t in wf.store.all())
        check(self, "sample set processes in the expected order, all records kept",
              "10 sample transactions", (EXPECTED_PROCESSING_ORDER, True, 10),
              (order, all_processed, len(wf.store)))


if __name__ == "__main__":
    unittest.main()
