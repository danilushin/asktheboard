from datetime import date, datetime, timedelta

import pytest

from asktheboard.convene import ConveneError, Seat, _parse_seat_call, convene
from asktheboard.llm import NoProviderConfigured
from asktheboard.model import BoardMinute


class FakeLLMClient:
    """Canned, key-free LLMClient for tests. Answers are keyed by seat name; the
    seat name is carried in the system prompt (`You are <name>. ...`)."""

    def __init__(self, answers):
        self.answers = answers  # dict[name -> raw str]  OR  a single raw str for all
        self.calls = []

    def complete(self, prompt: str, *, system: str = "") -> str:
        self.calls.append((prompt, system))
        if isinstance(self.answers, str):
            return self.answers
        for name, ans in self.answers.items():
            if f"You are {name}." in system:
                return ans
        raise AssertionError(f"no canned answer for system={system!r}")


SEATS = [Seat("karpathy", "ML researcher"), Seat("skeptic", "argue why it fails")]


def _answers():
    return {
        "karpathy": '{"stance": "affirm", "probability": 0.8, "rationale": "scales fine"}',
        "skeptic": '{"stance": "dissent", "probability": 0.35, "rationale": "ops cost"}',
    }


def test_convene_builds_minute_with_mean_board_probability():
    client = FakeLLMClient(_answers())
    m = convene(
        id="m1",
        question="postgres+pgvector or a dedicated vector DB?",
        prior="leaning postgres",
        decision="postgres + pgvector",
        statement="pgvector handles our scale through next year",
        seats=SEATS,
        client=client,
        decision_type="library",
        created_at=datetime(2026, 1, 1, 12, 0, 0),
    )
    assert isinstance(m, BoardMinute)
    assert len(m.seats) == 2
    # board probability is the mean of the seat calls
    assert m.prediction.board_probability == pytest.approx((0.8 + 0.35) / 2)
    # decision_type drove the horizon (library = 90d)
    assert m.prediction.resolution_date == date(2026, 1, 1) + timedelta(days=90)
    # the dissent vector is preserved end-to-end (the moat mechanic)
    assert {s.seat: s.stance for s in m.seats} == {"karpathy": "affirm", "skeptic": "dissent"}
    # one LLM call per seat -- the fan-out fired
    assert len(client.calls) == 2


def test_convene_explicit_resolution_date_wins():
    client = FakeLLMClient(_answers())
    m = convene(
        id="m2", question="q", prior="", decision="d", statement="s",
        seats=SEATS, client=client,
        resolution_date=date(2027, 6, 1),
        created_at=datetime(2026, 1, 1, 12, 0, 0),
    )
    assert m.prediction.resolution_date == date(2027, 6, 1)


def test_convene_requires_client():
    with pytest.raises(NoProviderConfigured):
        convene(id="m", question="q", prior="", decision="d", statement="s",
                seats=SEATS, client=None, decision_type="library")


def test_convene_requires_a_horizon():
    client = FakeLLMClient(_answers())
    with pytest.raises(ConveneError):
        convene(id="m", question="q", prior="", decision="d", statement="s",
                seats=SEATS, client=client)  # neither resolution_date nor decision_type


def test_convene_requires_seats():
    with pytest.raises(ConveneError):
        convene(id="m", question="q", prior="", decision="d", statement="s",
                seats=[], client=FakeLLMClient("{}"), decision_type="library")


def test_parse_handles_prose_wrapped_json():
    sc = _parse_seat_call("x", 'Sure!\n{"stance":"dissent","probability":0.2}\nhope that helps')
    assert sc.stance == "dissent" and sc.probability == 0.2


def test_parse_handles_code_fence():
    sc = _parse_seat_call("x", '```json\n{"stance":"affirm","probability":0.9}\n```')
    assert sc.stance == "affirm" and sc.probability == 0.9


def test_parse_rejects_bad_stance():
    with pytest.raises(ConveneError):
        _parse_seat_call("x", '{"stance":"maybe","probability":0.5}')


def test_parse_rejects_out_of_range_probability():
    with pytest.raises(ConveneError):
        _parse_seat_call("x", '{"stance":"affirm","probability":1.5}')


def test_parse_rejects_no_json():
    with pytest.raises(ConveneError):
        _parse_seat_call("x", "I refuse to answer in JSON")
