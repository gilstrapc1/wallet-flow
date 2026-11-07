"""Small fixed sample set for demos and tests.

Covers ordinary and urgent payments, every priority level, and one pair of
urgent payments with equal priority (T004 and T007) to show tie handling.
"""

SAMPLE_TRANSACTIONS = [
    {"txn_id": "T001", "amount_cents": 4575, "txn_type": "purchase", "urgent": False, "priority": 1, "category": "food", "arrival_time": "2026-11-02T08:15:00"},
    {"txn_id": "T002", "amount_cents": 120000, "txn_type": "bill_payment", "urgent": False, "priority": 1, "category": "bills", "arrival_time": "2026-11-02T08:20:00"},
    {"txn_id": "T003", "amount_cents": 2500, "txn_type": "transfer", "urgent": True, "priority": 1, "category": "other", "arrival_time": "2026-11-02T08:22:00"},
    {"txn_id": "T004", "amount_cents": 8999, "txn_type": "bill_payment", "urgent": True, "priority": 2, "category": "bills", "arrival_time": "2026-11-02T08:30:00"},
    {"txn_id": "T005", "amount_cents": 1850, "txn_type": "purchase", "urgent": False, "priority": 1, "category": "transportation", "arrival_time": "2026-11-02T08:41:00"},
    {"txn_id": "T006", "amount_cents": 50000, "txn_type": "transfer", "urgent": True, "priority": 3, "category": "other", "arrival_time": "2026-11-02T08:45:00"},
    {"txn_id": "T007", "amount_cents": 3200, "txn_type": "bill_payment", "urgent": True, "priority": 2, "category": "bills", "arrival_time": "2026-11-02T08:50:00"},
    {"txn_id": "T008", "amount_cents": 6425, "txn_type": "purchase", "urgent": False, "priority": 2, "category": "shopping", "arrival_time": "2026-11-02T09:05:00"},
    {"txn_id": "T009", "amount_cents": 999, "txn_type": "purchase", "urgent": False, "priority": 1, "category": "food", "arrival_time": "2026-11-02T09:10:00"},
    {"txn_id": "T010", "amount_cents": 15000, "txn_type": "transfer", "urgent": False, "priority": 3, "category": "other", "arrival_time": "2026-11-02T09:12:00"},
]

# Expected processing order for the set above:
#   urgent by priority (3, then 2s in arrival order, then 1): T006, T004, T007, T003
#   then ordinary FIFO: T001, T002, T005, T008, T009, T010
EXPECTED_PROCESSING_ORDER = [
    "T006", "T004", "T007", "T003",
    "T001", "T002", "T005", "T008", "T009", "T010",
]
