from datetime import date, datetime

import pytest

from asktheboard.ledger import Ledger
from asktheboard.model import BoardMinute, Prediction, SeatCall


def _resolved(mid, board_p, outcome, seats, created="2026-01-01T09:00:00",
              resolves="2026-04-01", resolved="2026-04-02T12:00:00"):
    m = BoardMinute(
        id=mid,
        question="q",
        prior="p",
        decision="d",
        prediction=Prediction("stmt", date.fromisoformat(resolves), board_p),
        seats=seats,
        created_at=datetime.fromisoformat(created),
    )
    m.resolve(outcome, resolved_at=datetime.fromisoformat(resolved))
    return m


def test_open_minutes_are_ignored():
    ledger = Ledger()
    open_m = BoardMinute(
        id="open", question="q", prior="p", decision="d",
        prediction=Prediction("s", date(2026, 12, 1), 0.6),
        seats=[SeatCall("skeptic", "dissent", 0.4)],
        created_at=datetime(2026, 1, 1, 9, 0, 0),
    )
    ledger.add(open_m)
    assert ledger.seat_calibration() == {}
    assert ledger.resolved_minutes == []


def test_per_seat_calibration_accumulates():
    ledger = Ledger()
    # skeptic dissents twice; once right (outcome FALSE, p=0.2), once wrong (outcome TRUE, p=0.2)
    ledger.add(_resolved("a", 0.8, False, [SeatCall("skeptic", "dissent", 0.2)]))
    ledger.add(_resolved("b", 0.8, True, [SeatCall("skeptic", "dissent", 0.2)],
                         resolves="2026-05-01", resolved="2026-05-02T12:00:00"))
    cal = ledger.seat_calibration()
    sk = cal["skeptic"]
    assert sk.resolved_count == 2
    # briers: (0.2-0)^2=0.04 and (0.2-1)^2=0.64 -> mean 0.34
    assert sk.mean_brier == pytest.approx(0.34)
    assert sk.contrarian_wins == 1   # the FALSE outcome
    assert sk.contrarian_losses == 1  # the TRUE outcome


def test_ranked_seats_best_calibrated_first():
    ledger = Ledger()
    ledger.add(_resolved(
        "a", 0.9, True,
        [SeatCall("oracle", "affirm", 0.95), SeatCall("noise", "affirm", 0.1)],
    ))
    ranked = ledger.ranked_seats()
    assert [sc.seat for sc in ranked] == ["oracle", "noise"]
    assert ranked[0].mean_brier < ranked[1].mean_brier
