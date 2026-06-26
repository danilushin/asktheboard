"""Foresight data model -- the un-retrofittable core of ask-the-board.

A BoardMinute records a decision together with a *pre-registered, time-anchored,
falsifiable prediction* and a per-seat dissent vector. On (or after) the
resolution date, reality grades it: each seat gets a Brier score, and a seat that
dissented from the board and turned out more right than the consensus earns a
"contrarian win".

The value is structural, not cosmetic: the prediction's anchor timestamp is
stamped at creation and frozen, and a minute physically cannot be graded before
its resolution date. Cloning this file is easy; what is hard to fake is the
record it accrues -- you can't back-date a timestamp, so a track record only
exists if you called decisions in advance and let reality grade them.

No clock magic, no I/O, no LLM here -- pure data + integrity rules so the model
is trivially testable. Timestamps are injectable; production defaults to now().
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


def _now() -> datetime:
    return datetime.now()


class IntegrityError(ValueError):
    """Raised when an operation would violate the foresight contract.

    The two load-bearing rules:
      1. A prediction cannot be pre-registered to resolve in the past
         (no backfilling an "old" call onto a known outcome).
      2. A minute cannot be graded before its resolution date arrives
         (the outcome must not be knowable yet -- that is what makes it foresight).
    """


def brier(probability: float, outcome: bool) -> float:
    """Binary Brier score: (p - o)^2, where o is 1.0 if the event occurred.

    Range [0, 1]; lower is better. 0.0 = perfect, 0.25 = a coin-flip 0.5 call,
    1.0 = maximally, confidently wrong.
    """
    if not 0.0 <= probability <= 1.0:
        raise ValueError(f"probability must be in [0, 1], got {probability}")
    o = 1.0 if outcome else 0.0
    return (probability - o) ** 2


@dataclass(frozen=True)
class SeatCall:
    """One board seat's position on the pre-registered prediction.

    `stance` is relative to the board decision: a seat that "dissent"s disagrees
    with the consensus call. `probability` is the seat's own P(prediction is TRUE)
    -- the falsifiable bet that reality will later grade.
    """

    seat: str
    stance: str  # "affirm" | "dissent"
    probability: float
    rationale: str = ""

    def __post_init__(self) -> None:
        if self.stance not in ("affirm", "dissent"):
            raise ValueError(f"stance must be 'affirm' or 'dissent', got {self.stance!r}")
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError(f"probability must be in [0, 1], got {self.probability}")

    def brier(self, outcome: bool) -> float:
        return brier(self.probability, outcome)

    def to_dict(self) -> dict:
        return {
            "seat": self.seat,
            "stance": self.stance,
            "probability": self.probability,
            "rationale": self.rationale,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SeatCall":
        return cls(
            seat=d["seat"],
            stance=d["stance"],
            probability=float(d["probability"]),
            rationale=d.get("rationale", ""),
        )


@dataclass(frozen=True)
class Prediction:
    """A falsifiable, dated claim with the board's consensus confidence.

    Frozen on purpose: once a minute is created the prediction text, horizon and
    board probability are immutable -- you cannot quietly edit the bet after the
    fact to look prescient.
    """

    statement: str
    resolution_date: date
    board_probability: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.board_probability <= 1.0:
            raise ValueError(f"board_probability must be in [0, 1], got {self.board_probability}")
        if not self.statement.strip():
            raise ValueError("prediction statement must be non-empty")

    def brier(self, outcome: bool) -> float:
        return brier(self.board_probability, outcome)

    def to_dict(self) -> dict:
        return {
            "statement": self.statement,
            "resolution_date": self.resolution_date.isoformat(),
            "board_probability": self.board_probability,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Prediction":
        return cls(
            statement=d["statement"],
            resolution_date=date.fromisoformat(d["resolution_date"]),
            board_probability=float(d["board_probability"]),
        )


@dataclass(frozen=True)
class Resolution:
    """Reality's verdict, recorded on or after the resolution date."""

    realized_outcome: bool
    resolved_at: datetime
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "realized_outcome": self.realized_outcome,
            "resolved_at": self.resolved_at.isoformat(),
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Resolution":
        return cls(
            realized_outcome=bool(d["realized_outcome"]),
            resolved_at=datetime.fromisoformat(d["resolved_at"]),
            note=d.get("note", ""),
        )


@dataclass
class BoardMinute:
    """A decision + its pre-registered prediction + the per-seat dissent vector.

    `created_at` is THE anchor -- the timestamp the moat is built on. It is set at
    construction and never mutated. `resolution` is the only mutable field, and it
    can only be written through `resolve()`, which enforces the time gate.
    """

    id: str
    question: str
    prior: str  # what the user believed going in
    decision: str  # the board's recommendation
    prediction: Prediction
    seats: list[SeatCall] = field(default_factory=list)
    created_at: datetime = field(default_factory=_now)
    resolution: Optional[Resolution] = None

    def __post_init__(self) -> None:
        # Rule 1: cannot pre-register a call that already resolves in the past.
        if self.prediction.resolution_date <= self.created_at.date():
            raise IntegrityError(
                f"resolution_date {self.prediction.resolution_date} must be after "
                f"created_at date {self.created_at.date()} -- a prediction must be "
                f"anchored before its outcome is knowable (no backfilling)"
            )

    @property
    def resolved(self) -> bool:
        return self.resolution is not None

    @property
    def vindicated(self) -> Optional[bool]:
        """True if the board call landed on the right side of 0.5; None if open."""
        if self.resolution is None:
            return None
        board_said_true = self.prediction.board_probability >= 0.5
        return board_said_true == self.resolution.realized_outcome

    def resolve(self, realized_outcome: bool, *, resolved_at: Optional[datetime] = None,
                note: str = "") -> Resolution:
        """Grade the minute against reality. Enforces the foresight time gate."""
        if self.resolution is not None:
            raise IntegrityError(f"minute {self.id} is already resolved")
        when = resolved_at or _now()
        # Rule 2: cannot grade before the horizon -- the outcome must not be
        # knowable yet at pre-registration time.
        if when.date() < self.prediction.resolution_date:
            raise IntegrityError(
                f"cannot resolve {self.id} on {when.date()}: its resolution_date "
                f"{self.prediction.resolution_date} has not arrived -- grading early "
                f"would mean the outcome was already knowable"
            )
        if when < self.created_at:
            raise IntegrityError("resolved_at cannot precede created_at")
        self.resolution = Resolution(realized_outcome=realized_outcome,
                                     resolved_at=when, note=note)
        return self.resolution

    def seat_briers(self) -> dict[str, float]:
        """Per-seat Brier score; empty until resolved."""
        if self.resolution is None:
            return {}
        o = self.resolution.realized_outcome
        return {s.seat: s.brier(o) for s in self.seats}

    def board_brier(self) -> Optional[float]:
        if self.resolution is None:
            return None
        return self.prediction.brier(self.resolution.realized_outcome)

    def contrarian_winners(self) -> list[str]:
        """Seats that dissented AND beat the board consensus against reality.

        The gold the scoreboard is built from: a seat that broke from the board
        and turned out more right than the consensus.
        """
        if self.resolution is None:
            return []
        board = self.board_brier()
        o = self.resolution.realized_outcome
        return [s.seat for s in self.seats
                if s.stance == "dissent" and s.brier(o) < board]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "question": self.question,
            "prior": self.prior,
            "decision": self.decision,
            "prediction": self.prediction.to_dict(),
            "seats": [s.to_dict() for s in self.seats],
            "created_at": self.created_at.isoformat(),
            "resolution": self.resolution.to_dict() if self.resolution else None,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "BoardMinute":
        m = cls(
            id=d["id"],
            question=d["question"],
            prior=d["prior"],
            decision=d["decision"],
            prediction=Prediction.from_dict(d["prediction"]),
            seats=[SeatCall.from_dict(s) for s in d.get("seats", [])],
            created_at=datetime.fromisoformat(d["created_at"]),
        )
        if d.get("resolution"):
            m.resolution = Resolution.from_dict(d["resolution"])
        return m
