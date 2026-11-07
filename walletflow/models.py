"""Transaction record, allowed values, and field validation for WalletFlow."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

TXN_TYPES = ("purchase", "transfer", "bill_payment")
CATEGORIES = ("food", "transportation", "bills", "shopping", "other")

STATUS_PENDING = "pending"
STATUS_PROCESSED = "processed"

MIN_PRIORITY = 1
MAX_PRIORITY = 3  # 3 = highest priority

REQUIRED_FIELDS = (
    "txn_id",
    "amount_cents",
    "txn_type",
    "urgent",
    "priority",
    "category",
    "arrival_time",
)


class ValidationError(ValueError):
    """Raised when a transaction has missing or invalid fields."""


class DuplicateTransactionError(ValueError):
    """Raised when a transaction ID is already stored."""


class AlreadyProcessedError(ValueError):
    """Raised when processing is attempted on a processed transaction."""


@dataclass
class Transaction:
    txn_id: str
    amount_cents: int
    txn_type: str
    urgent: bool
    priority: int
    category: str
    arrival_time: datetime
    status: str = STATUS_PENDING
    seq: int = -1  # arrival counter, assigned by the store on add
    processed_at: Optional[datetime] = None

    def amount_display(self) -> str:
        return f"${self.amount_cents // 100:,}.{self.amount_cents % 100:02d}"


def _parse_time(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass
    raise ValidationError(
        f"arrival_time must be an ISO 8601 date/time (e.g. 2026-11-06T09:30), got {value!r}"
    )


def make_transaction(raw: dict) -> Transaction:
    """Validate a raw dict and build a pending Transaction.

    Raises ValidationError with a clear message on the first problem found.
    Status and seq are set by the system and ignored if supplied.
    """
    if not isinstance(raw, dict):
        raise ValidationError("transaction must be a dict of fields")

    missing = [f for f in REQUIRED_FIELDS if raw.get(f) is None]
    if missing:
        raise ValidationError(f"missing required field(s): {', '.join(missing)}")

    txn_id = raw["txn_id"]
    if not isinstance(txn_id, str) or not txn_id.strip():
        raise ValidationError("txn_id must be a non-empty string")
    txn_id = txn_id.strip()

    amount = raw["amount_cents"]
    # bool is a subclass of int, so reject it explicitly; floats are never allowed for money.
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValidationError(f"amount_cents must be an integer number of cents, got {amount!r}")
    if amount <= 0:
        raise ValidationError(f"amount_cents must be positive, got {amount}")

    txn_type = raw["txn_type"]
    if txn_type not in TXN_TYPES:
        raise ValidationError(f"txn_type must be one of {TXN_TYPES}, got {txn_type!r}")

    urgent = raw["urgent"]
    if not isinstance(urgent, bool):
        raise ValidationError(f"urgent must be True or False, got {urgent!r}")

    priority = raw["priority"]
    if (
        isinstance(priority, bool)
        or not isinstance(priority, int)
        or not MIN_PRIORITY <= priority <= MAX_PRIORITY
    ):
        raise ValidationError(
            f"priority must be an integer {MIN_PRIORITY}-{MAX_PRIORITY}, got {priority!r}"
        )

    category = raw["category"]
    if category not in CATEGORIES:
        raise ValidationError(f"category must be one of {CATEGORIES}, got {category!r}")

    return Transaction(
        txn_id=txn_id,
        amount_cents=amount,
        txn_type=txn_type,
        urgent=urgent,
        priority=priority,
        category=category,
        arrival_time=_parse_time(raw["arrival_time"]),
    )
