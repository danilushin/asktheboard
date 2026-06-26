from datetime import datetime

import pytest

from asktheboard.convene import Seat, convene
from asktheboard.roster import (
    UnknownPanel,
    UnknownSeat,
    panel,
    panel_names,
    seat,
    seat_slugs,
    seats,
)


class FakeLLMClient:
    """Key-free client whose answer is keyed by the seat name in the system prompt."""

    def __init__(self, answer):
        self.answer = answer
        self.calls = []

    def complete(self, prompt: str, *, system: str = "") -> str:
        self.calls.append((prompt, system))
        return self.answer


def test_seat_resolves_to_a_populated_seat():
    s = seat("architect")
    assert isinstance(s, Seat)
    assert s.name == "architect"
    assert s.persona  # non-empty voice


def test_unknown_seat_raises():
    with pytest.raises(UnknownSeat):
        seat("nope")


def test_unknown_panel_raises():
    with pytest.raises(UnknownPanel):
        panel("nope")


def test_seats_preserves_order():
    resolved = seats(["skeptic", "architect"])
    assert [s.name for s in resolved] == ["skeptic", "architect"]


def test_panel_tech_is_architect_skeptic_pragmatist():
    assert [s.name for s in panel("tech")] == ["architect", "skeptic", "pragmatist"]


def test_every_panel_references_only_real_seats():
    # a panel must never name a slug that is not in the roster (integrity)
    valid = set(seat_slugs())
    for name in panel_names():
        for s in panel(name):
            assert s.name in valid


def test_seat_slugs_and_panel_names_sorted():
    assert seat_slugs() == sorted(seat_slugs())
    assert panel_names() == sorted(panel_names())


def test_skeptic_is_in_every_panel():
    # the forced-dissent voice belongs on every default seating
    for name in panel_names():
        assert "skeptic" in [s.name for s in panel(name)]


def test_convene_with_a_bundled_panel():
    # the whole point of the port: seat a board by name and run the live path
    client = FakeLLMClient('{"stance": "affirm", "probability": 0.6, "rationale": "ok"}')
    m = convene(
        id="roster-1",
        question="adopt library X?",
        prior="leaning yes",
        decision="adopt X",
        statement="X is still our choice in 90 days",
        seats=panel("tech"),
        client=client,
        decision_type="library",
        created_at=datetime(2026, 1, 1, 12, 0, 0),
    )
    # one call per panel seat; the named board produced a real minute
    assert len(client.calls) == 3
    assert {s.seat for s in m.seats} == {"architect", "skeptic", "pragmatist"}
    assert m.prediction.board_probability == pytest.approx(0.6)
