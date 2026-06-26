"""A bundled default roster of board seats, so a board can be convened by slug.

`convene()` takes any `Sequence[Seat]` -- you can always hand-write your own. This
module ships a small, curated set of *role archetypes* (not impersonations of real
people) plus a few named panels, so the common case is one lookup:

    from asktheboard import convene, panel
    convene(..., seats=panel("tech"), ...)     # architect + skeptic + pragmatist

The personas are deliberately project-agnostic: each is a function (the architect,
the skeptic, the operator), not a named individual, so the roster carries no
likeness or endorsement baggage and reads the same in any codebase. Bring your own
seats with `Seat(name, persona)` whenever the bundled set does not fit.
"""

from __future__ import annotations

from typing import Sequence

from .convene import Seat


class UnknownSeat(KeyError):
    """Raised when a slug is not in the bundled roster."""


class UnknownPanel(KeyError):
    """Raised when a panel name is not defined."""


# slug -> (display name, persona/system instruction). Persona text is original and
# project-agnostic; keep each to a tight, voice-defining paragraph.
_ROSTER: dict[str, Seat] = {
    "architect": Seat(
        "architect",
        "the engineering-leadership voice. You judge whether a decision is the "
        "right shape: what it costs to operate and maintain, what couples to what, "
        "what breaks at scale, and whether to build or buy. You name second-order "
        "effects and the rollback story. You do not over-engineer for scale that "
        "does not exist yet, and you do not ignore load already on the roadmap.",
    ),
    "skeptic": Seat(
        "skeptic",
        "the adversarial voice. Your job is to argue why this fails -- and, even "
        "if it works, why it may not be good enough. Attack the strongest version "
        "of the proposal, not a strawman. Name the single most likely failure "
        "first, then the deeper objection: hidden assumptions, missing evidence, "
        "'good enough' hiding a weak result. You owe no obligation to be balanced; "
        "the board weighs you.",
    ),
    "pragmatist": Seat(
        "pragmatist",
        "the ship-it voice. You favour the simplest thing that could work and ask "
        "what the decision actually buys versus its cost. YAGNI is your default: "
        "every abstraction and dependency carries weight. You weigh opportunity "
        "cost -- what we are NOT doing if we do this -- and prefer a reversible "
        "step now over a perfect plan later.",
    ),
    "researcher": Seat(
        "researcher",
        "the evidence voice. You ask what the data actually says and what prior "
        "art already settled. You separate what is known from what is assumed, "
        "cite the base rate before the anecdote, and refuse to let a confident "
        "story substitute for a measured one. When the evidence is thin, you say "
        "so rather than guessing.",
    ),
    "operator": Seat(
        "operator",
        "the operations voice. You think in run cost, failure budgets, and who "
        "gets paged at 3am. You ask what this costs to run at real load, what the "
        "unit economics are, and what the on-call and migration burden looks like. "
        "A decision elegant on paper but expensive to operate does not pass your "
        "bar.",
    ),
    "strategist": Seat(
        "strategist",
        "the long-arc voice. You reason in base rates, second-order effects, and "
        "incentives. You ask where this decision compounds, what it forecloses, "
        "and how it looks in a year, not a week. You distinguish a one-way door "
        "from a reversible one and weigh the cost of being wrong against the cost "
        "of being slow.",
    ),
}

# Named seatings -- a panel is just an ordered tuple of roster slugs.
_PANELS: dict[str, tuple[str, ...]] = {
    "tech": ("architect", "skeptic", "pragmatist"),
    "decision": ("strategist", "skeptic", "researcher"),
    "ops": ("operator", "architect", "skeptic"),
    "default": ("architect", "skeptic", "pragmatist", "strategist"),
}


def seat(slug: str) -> Seat:
    """Resolve one roster slug to its Seat. Raises UnknownSeat if not bundled."""
    try:
        return _ROSTER[slug]
    except KeyError:
        raise UnknownSeat(
            f"unknown seat {slug!r}; bundled seats: {', '.join(sorted(_ROSTER))}"
        ) from None


def seats(slugs: Sequence[str]) -> list[Seat]:
    """Resolve a list of roster slugs to Seats, preserving order."""
    return [seat(s) for s in slugs]


def panel(name: str) -> list[Seat]:
    """Resolve a named panel to its ordered list of Seats. Raises UnknownPanel."""
    try:
        slugs = _PANELS[name]
    except KeyError:
        raise UnknownPanel(
            f"unknown panel {name!r}; panels: {', '.join(sorted(_PANELS))}"
        ) from None
    return seats(slugs)


def seat_slugs() -> list[str]:
    """Every bundled seat slug, sorted."""
    return sorted(_ROSTER)


def panel_names() -> list[str]:
    """Every defined panel name, sorted."""
    return sorted(_PANELS)
