from datetime import date, datetime

from asktheboard.adr import render_adr
from asktheboard.model import BoardMinute, Prediction, SeatCall


def _minute(seats=None):
    return BoardMinute(
        id="2026-01-postgres",
        question="Adopt Postgres over a dedicated vector DB?",
        prior="Tempted by the dedicated vector DB",
        decision="Stay on Postgres + pgvector",
        prediction=Prediction(
            statement="No migration off Postgres within 3 months",
            resolution_date=date(2026, 4, 1),
            board_probability=0.75,
        ),
        seats=seats or [SeatCall("skeptic", "dissent", 0.3, "scale will bite")],
        created_at=datetime(2026, 1, 1, 9, 0, 0),
    )


def test_pre_registered_adr_has_no_resolution_section():
    md = render_adr(_minute())
    assert md.startswith("# ADR-2026-01-postgres:")
    assert "Pre-registered" in md
    assert "**Anchored:** 2026-01-01T09:00:00" in md
    assert "## Pre-registered prediction" in md
    assert "75%" in md
    assert "## Resolution" not in md  # not graded yet
    # no Brier column before resolution
    assert "Brier" not in md


def test_resolved_adr_shows_verdict_and_briers():
    m = _minute()
    m.resolve(False, resolved_at=datetime(2026, 4, 2, 12, 0, 0))
    md = render_adr(m)
    assert "REFUTED" in md  # board leaned TRUE, reality FALSE
    assert "## Resolution" in md
    assert "**Realized outcome:** FALSE" in md
    assert "Brier" in md  # column now present
    assert "**Contrarian wins:** skeptic" in md  # dissent (0.3) beat board (0.75)


def test_adr_is_newline_terminated_and_stable():
    md = render_adr(_minute())
    assert md.endswith("\n")
    assert render_adr(_minute()) == md  # deterministic
