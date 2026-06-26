from datetime import date, datetime

import pytest

from asktheboard.model import (
    BoardMinute,
    IntegrityError,
    Prediction,
    SeatCall,
    brier,
)


def _minute(created="2026-01-01T09:00:00", resolves="2026-04-01", board_p=0.7, seats=None):
    return BoardMinute(
        id="m1",
        question="Adopt Postgres over the new vector DB?",
        prior="Leaning toward the shiny vector DB",
        decision="Stay on Postgres + pgvector",
        prediction=Prediction(
            statement="No migration off Postgres within the horizon",
            resolution_date=date.fromisoformat(resolves),
            board_probability=board_p,
        ),
        seats=seats or [],
        created_at=datetime.fromisoformat(created),
    )


def test_brier_endpoints():
    assert brier(1.0, True) == 0.0
    assert brier(0.0, False) == 0.0
    assert brier(1.0, False) == 1.0
    assert brier(0.5, True) == 0.25
    with pytest.raises(ValueError):
        brier(1.2, True)


def test_cannot_pre_register_a_past_resolution():
    # resolution_date on/before created_at -> backfilling, rejected
    with pytest.raises(IntegrityError):
        _minute(created="2026-04-01T09:00:00", resolves="2026-04-01")
    with pytest.raises(IntegrityError):
        _minute(created="2026-05-01T09:00:00", resolves="2026-04-01")


def test_cannot_resolve_before_horizon():
    m = _minute()
    with pytest.raises(IntegrityError):
        m.resolve(True, resolved_at=datetime.fromisoformat("2026-03-31T12:00:00"))
    assert not m.resolved


def test_resolve_on_or_after_horizon():
    m = _minute()
    m.resolve(True, resolved_at=datetime.fromisoformat("2026-04-01T12:00:00"))
    assert m.resolved
    assert m.vindicated is True  # board said 0.7 (TRUE side), outcome TRUE


def test_double_resolve_rejected():
    m = _minute()
    m.resolve(True, resolved_at=datetime.fromisoformat("2026-04-02T12:00:00"))
    with pytest.raises(IntegrityError):
        m.resolve(False, resolved_at=datetime.fromisoformat("2026-04-03T12:00:00"))


def test_vindicated_logic_on_false_outcome():
    m = _minute(board_p=0.7)
    m.resolve(False, resolved_at=datetime.fromisoformat("2026-04-02T12:00:00"))
    assert m.vindicated is False  # board leaned TRUE, reality FALSE
    assert m.board_brier() == pytest.approx(0.49)  # (0.7 - 0)^2


def test_anchor_is_immutable_across_resolution():
    m = _minute()
    anchor = m.created_at
    m.resolve(True, resolved_at=datetime.fromisoformat("2026-04-02T12:00:00"))
    assert m.created_at == anchor  # grading never moves the anchor


def test_contrarian_winner_detection():
    seats = [
        SeatCall("karpathy", "affirm", 0.8, "boring tech wins"),
        SeatCall("skeptic", "dissent", 0.2, "you'll outgrow it"),
    ]
    m = _minute(board_p=0.8, seats=seats)
    # Reality: FALSE (they DID migrate). Skeptic (dissent, p=0.2) was more right.
    m.resolve(False, resolved_at=datetime.fromisoformat("2026-04-02T12:00:00"))
    briers = m.seat_briers()
    assert briers["karpathy"] == pytest.approx(0.64)  # (0.8-0)^2
    assert briers["skeptic"] == pytest.approx(0.04)   # (0.2-0)^2
    assert m.contrarian_winners() == ["skeptic"]


def test_no_contrarian_win_when_dissent_was_wrong():
    seats = [
        SeatCall("karpathy", "affirm", 0.8, ""),
        SeatCall("skeptic", "dissent", 0.2, ""),
    ]
    m = _minute(board_p=0.8, seats=seats)
    m.resolve(True, resolved_at=datetime.fromisoformat("2026-04-02T12:00:00"))
    assert m.contrarian_winners() == []  # board (TRUE) was right; dissent lost


def test_round_trip_serialization():
    seats = [SeatCall("skeptic", "dissent", 0.2, "noisy")]
    m = _minute(seats=seats)
    m.resolve(True, resolved_at=datetime.fromisoformat("2026-04-05T12:00:00"))
    again = BoardMinute.from_dict(m.to_dict())
    assert again.to_dict() == m.to_dict()
    assert again.resolved
    assert again.contrarian_winners() == m.contrarian_winners()


def test_seatcall_validation():
    with pytest.raises(ValueError):
        SeatCall("x", "maybe", 0.5)
    with pytest.raises(ValueError):
        SeatCall("x", "affirm", 1.5)
