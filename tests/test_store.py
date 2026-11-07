"""Add/store, validation, and find-by-ID tests."""

import unittest

from walletflow import DuplicateTransactionError, ValidationError, WalletFlow
from walletflow.models import STATUS_PENDING

from .helpers import check


def valid(**overrides):
    raw = {
        "txn_id": "T001",
        "amount_cents": 4575,
        "txn_type": "purchase",
        "urgent": False,
        "priority": 1,
        "category": "food",
        "arrival_time": "2026-11-02T08:15:00",
    }
    raw.update(overrides)
    return raw


class TestAdd(unittest.TestCase):
    def setUp(self):
        self.wf = WalletFlow()

    def test_add_valid_transaction(self):
        txn = self.wf.add(valid())
        check(self, "valid transaction is stored as pending", "T001, $45.75 purchase",
              ("T001", 1, STATUS_PENDING), (txn.txn_id, len(self.wf.store), txn.status))

    def test_duplicate_id_rejected_and_original_unchanged(self):
        self.wf.add(valid())
        with self.assertRaises(DuplicateTransactionError):
            self.wf.add(valid(amount_cents=99999))
        kept = self.wf.find("T001")
        check(self, "duplicate ID rejected; original amount kept, store size 1",
              "add T001 twice (second with 99999 cents)",
              (1, 4575), (len(self.wf.store), kept.amount_cents))

    def test_invalid_fields_rejected_without_changing_store(self):
        bad_inputs = {
            "missing txn_id": valid(txn_id=None),
            "blank txn_id": valid(txn_id="   "),
            "zero amount": valid(amount_cents=0),
            "negative amount": valid(amount_cents=-500),
            "float amount": valid(amount_cents=45.75),
            "unknown txn_type": valid(txn_type="refund"),
            "unknown category": valid(category="travel"),
            "priority too low": valid(priority=0),
            "priority too high": valid(priority=4),
            "urgent not a bool": valid(urgent="yes"),
            "bad arrival_time": valid(arrival_time="yesterday"),
        }
        for label, raw in bad_inputs.items():
            with self.subTest(label):
                with self.assertRaises(ValidationError) as ctx:
                    self.wf.add(raw)
                check(self, f"invalid input rejected: {label} ({ctx.exception})",
                      label, (0, 0), (len(self.wf.store), self.wf.pending_count()))


class TestFind(unittest.TestCase):
    def setUp(self):
        self.wf = WalletFlow()
        self.wf.add(valid())
        self.wf.add(valid(txn_id="T002", amount_cents=120000, txn_type="bill_payment", category="bills"))

    def test_find_existing_id(self):
        txn = self.wf.find("T002")
        check(self, "find returns the full record", "find('T002')",
              ("T002", 120000, "bill_payment", "bills"),
              (txn.txn_id, txn.amount_cents, txn.txn_type, txn.category))

    def test_find_missing_id(self):
        check(self, "find on an unknown ID returns None", "find('T999')", None, self.wf.find("T999"))


if __name__ == "__main__":
    unittest.main()
