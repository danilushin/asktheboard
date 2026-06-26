from datetime import date, timedelta

import pytest

from asktheboard import decision_types as dt
from asktheboard.decision_types import (
    UnknownDecisionType,
    resolution_date_for,
)


def test_catalog_has_exactly_the_named_types():
    assert set(dt.keys()) == {"library", "migration", "architecture"}


def test_short_latency_first():
    # The ordering is load-bearing: a fresh board earns signal on fast calls first.
    horizons = [dt.CATALOG[k].horizon_days for k in dt.keys()]
    assert horizons == sorted(horizons)
    assert dt.keys()[0] == "library"
    assert dt.keys()[-1] == "architecture"


def test_resolution_date_math():
    anchor = date(2026, 1, 1)
    assert resolution_date_for("library", anchor) == anchor + timedelta(days=90)
    assert resolution_date_for("migration", anchor) == anchor + timedelta(days=180)
    assert dt.get("architecture").resolution_date(anchor) == anchor + timedelta(days=365)


def test_unknown_type_raises():
    with pytest.raises(UnknownDecisionType):
        dt.get("nope")
    with pytest.raises(UnknownDecisionType):
        resolution_date_for("nope", date(2026, 1, 1))
