"""Decision-type catalog -- default resolution horizons that keep the loop honest.

A board-minute is only foresight if its prediction has a date by which reality can
grade it. Picking that date by hand every time is friction; worse, it lets an
operator quietly stretch the horizon until any call looks right. The catalog fixes
a sensible default horizon per decision class so the common case is one lookup and
the dishonest case (a 5-year horizon on a library swap) stands out.

Ordered short-latency first on purpose: the fastest-resolving decisions are how a
fresh board accumulates a track record before anyone will trust a slow one. Seed
the scoreboard with `library` calls; let the `architecture` bets ripen.

No clock magic here -- `resolution_date()` takes the anchor explicitly so it stays
pure and testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


class UnknownDecisionType(KeyError):
    """Raised when a decision-type key is not in the catalog."""


@dataclass(frozen=True)
class DecisionType:
    """A class of decision with the default horizon over which it resolves."""

    key: str
    label: str
    horizon_days: int
    description: str

    def resolution_date(self, anchor: date) -> date:
        """The default date reality can grade a call of this type, given its anchor."""
        return anchor + timedelta(days=self.horizon_days)


# Short-latency first -> a new board earns signal fast on these, then ripens the
# slower bets. Exactly the three the plan names; extend deliberately, not by reflex.
_TYPES = (
    DecisionType(
        "library",
        "Library / dependency choice",
        90,
        "Adopt, swap, or drop a library or dependency. Resolves within a quarter: "
        "you know inside 90 days whether it held up in production.",
    ),
    DecisionType(
        "migration",
        "Migration / infrastructure change",
        180,
        "Move a datastore, platform, or pipeline. Half-year horizon: migrations "
        "reveal their true cost over a couple of release cycles.",
    ),
    DecisionType(
        "architecture",
        "Architecture / design bet",
        365,
        "A structural design choice you will live with. Yearly horizon: the bill "
        "for an architecture decision lands over the following year.",
    ),
)

CATALOG: dict[str, DecisionType] = {t.key: t for t in _TYPES}


def get(key: str) -> DecisionType:
    """Look up a decision type by key, raising UnknownDecisionType if absent."""
    try:
        return CATALOG[key]
    except KeyError:
        raise UnknownDecisionType(
            f"unknown decision type {key!r}; known: {', '.join(CATALOG)}"
        ) from None


def keys() -> list[str]:
    """Catalog keys, short-latency first (insertion order)."""
    return list(CATALOG)


def resolution_date_for(key: str, anchor: date) -> date:
    """Default resolution date for a decision of type `key` anchored at `anchor`."""
    return get(key).resolution_date(anchor)
