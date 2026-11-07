"""Progress Check demo: add/store, validation errors, find by ID, and processing.

Run from the repo root:  python3 demo.py
"""

from walletflow import DuplicateTransactionError, ValidationError, WalletFlow
from walletflow.sample_data import SAMPLE_TRANSACTIONS


def show(txn):
    kind = f"URGENT p{txn.priority}" if txn.urgent else "ordinary"
    return (f"{txn.txn_id}  {txn.amount_display():>11}  {txn.txn_type:<12} {txn.category:<14} "
            f"{kind:<10} {txn.status}")


def try_add(wf, raw):
    try:
        txn = wf.add(raw)
        print(f"  OK     added {txn.txn_id}")
    except (ValidationError, DuplicateTransactionError) as err:
        print(f"  ERROR  {raw.get('txn_id')!r}: {err}")


def main():
    wf = WalletFlow()

    print("1) Add sample transactions")
    for raw in SAMPLE_TRANSACTIONS:
        try_add(wf, raw)

    print("\n2) Invalid inputs are rejected without changing stored data")
    try_add(wf, dict(SAMPLE_TRANSACTIONS[0]))                              # duplicate ID
    try_add(wf, {**SAMPLE_TRANSACTIONS[0], "txn_id": "T100", "amount_cents": -5})
    try_add(wf, {**SAMPLE_TRANSACTIONS[0], "txn_id": "T101", "amount_cents": 45.75})
    try_add(wf, {**SAMPLE_TRANSACTIONS[0], "txn_id": "T102", "priority": 7})
    print(f"  stored: {len(wf.store)}  pending: {wf.pending_count()}")

    print("\n3) Find by ID")
    for tid in ("T004", "T999"):
        txn = wf.find(tid)
        print(f"  {tid}: {show(txn) if txn else 'not found'}")

    print("\n4) Process everything (urgent by priority, then ordinary FIFO)")
    while (txn := wf.process_next()) is not None:
        print(f"  processed {show(txn)}")
    print(f"  next: {wf.process_next() or 'no pending transactions'}")

    print("\n5) Records remain after processing")
    print(f"  T001: {show(wf.find('T001'))}")


if __name__ == "__main__":
    main()
