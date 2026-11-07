# wallet-flow
Class project to simulate the transaction-processing function of a digital-wallet platform.

COT 5480 semester project — James Clifford, Cody Gilstrap, Aden Brady.

## Requirements

- Python 3.8 or newer
- Standard library only; no packages to install

## Run the demo

From the repo root:

```bash
python3 demo.py
```

It adds the sample transactions, shows rejected invalid inputs, looks up IDs (including one that does not exist), and processes everything: urgent payments by priority first, then ordinary payments first in, first out.

## Run the tests

```bash
python3 -m unittest -v
```

Each test prints its input, expected result, and actual result, then asserts they match.

## Layout

| Path | Contents |
| --- | --- |
| `walletflow/models.py` | `Transaction` record, allowed values, validation |
| `walletflow/store.py` | `TransactionStore`: dict keyed by transaction ID (add, find) |
| `walletflow/processing.py` | `ProcessingQueues`: deque for ordinary FIFO, heap for urgent |
| `walletflow/__init__.py` | `WalletFlow`: one store plus the queues |
| `walletflow/sample_data.py` | Fixed 10-transaction sample set and its expected processing order |
| `tests/` | `unittest` tests for storage, lookup, and processing |
| `demo.py` | Progress Check walkthrough |

## Transaction rules

| Field | Rule |
| --- | --- |
| `txn_id` | Non-empty string, unique |
| `amount_cents` | Positive integer (cents; floats rejected) |
| `txn_type` | `purchase`, `transfer`, or `bill_payment` |
| `urgent` | `True` or `False` |
| `priority` | Integer 1–3, 3 is highest |
| `category` | `food`, `transportation`, `bills`, `shopping`, or `other` |
| `arrival_time` | ISO 8601 date/time, e.g. `2026-11-02T08:15:00` |

Status starts as `pending` and becomes `processed`; processed records stay in the store for searching and reporting.
