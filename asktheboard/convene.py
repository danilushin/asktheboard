"""Live convening -- fan a decision across board seats and assemble a BoardMinute.

This is the W1 fan-out: each seat answers *through the caller's LLMClient* (BYOK),
returns its stance + probability + rationale on the pre-registered prediction, and
the board's consensus probability is the mean of the seats' calls. The result is a
fully-formed, graded-ready `BoardMinute` -- the integrity rules (no backfilling, no
early grading, frozen anchor) are enforced by `model.py` on construction, so a
convening cannot produce a dishonest minute.

The engine still makes zero calls of its own: every token of inference runs on the
client you pass. Swap in `HTTPLLMClient` for production, a fake for tests.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Sequence

from .decision_types import resolution_date_for
from .llm import LLMClient, require_client
from .model import BoardMinute, Prediction, SeatCall


class ConveneError(RuntimeError):
    """Raised when a seat's answer cannot be parsed into a valid SeatCall."""


@dataclass(frozen=True)
class Seat:
    """A board seat: a name plus the persona/expertise that shapes its system prompt."""

    name: str
    persona: str


_SEAT_INSTRUCTION = (
    "A decision is on the table and a falsifiable prediction has been registered.\n"
    "Question: {question}\n"
    "Board's decision: {decision}\n"
    'Pre-registered prediction (resolves {resolution_date}): "{statement}"\n\n'
    "Give YOUR independent call. Reply with ONLY a JSON object, no prose:\n"
    '{{"stance": "affirm" | "dissent", "probability": <number 0..1>, '
    '"rationale": "<one sentence>"}}\n'
    '- "stance": "affirm" if you back the board\'s decision, "dissent" if you break from it.\n'
    '- "probability": your own P(the prediction resolves TRUE), as a number in [0, 1].\n'
    "- Be willing to dissent: a contrarian who is right is worth more than a chorus."
)

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def _parse_seat_call(seat: str, raw: str) -> SeatCall:
    """Parse one seat's raw completion into a validated SeatCall."""
    text = raw.strip()
    # Strip a ```json ... ``` fence if the model added one.
    if text.startswith("```"):
        text = text.strip("`")
        text = text[4:] if text.lower().startswith("json") else text
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        m = _JSON_RE.search(raw)
        if not m:
            raise ConveneError(f"seat {seat!r}: no JSON object in answer: {raw!r}")
        try:
            obj = json.loads(m.group(0))
        except json.JSONDecodeError as e:
            raise ConveneError(f"seat {seat!r}: unparseable JSON: {raw!r}") from e
    if not isinstance(obj, dict):
        raise ConveneError(f"seat {seat!r}: expected a JSON object, got {obj!r}")
    try:
        stance = str(obj["stance"]).strip().lower()
        probability = float(obj["probability"])
    except (KeyError, TypeError, ValueError) as e:
        raise ConveneError(f"seat {seat!r}: missing/invalid stance|probability: {obj!r}") from e
    rationale = str(obj.get("rationale", "")).strip()
    try:
        return SeatCall(seat=seat, stance=stance, probability=probability, rationale=rationale)
    except ValueError as e:  # SeatCall enforces stance/probability domains
        raise ConveneError(f"seat {seat!r}: {e}") from e


def convene(
    *,
    id: str,
    question: str,
    prior: str,
    decision: str,
    statement: str,
    seats: Sequence[Seat],
    client: Optional[LLMClient],
    resolution_date: Optional[date] = None,
    decision_type: Optional[str] = None,
    created_at: Optional[datetime] = None,
) -> BoardMinute:
    """Convene the board on a decision and return a pre-registered BoardMinute.

    Provide the resolution horizon either directly (`resolution_date`) or by naming
    a `decision_type` whose default horizon is applied from the anchor. Every seat
    answers through `client` (BYOK); the board probability is the mean of their
    calls. Raises NoProviderConfigured if `client` is None, ConveneError on an
    unparseable seat answer, and IntegrityError if the horizon is in the past.
    """
    client = require_client(client)
    if not seats:
        raise ConveneError("convene requires at least one seat")
    anchor = created_at or datetime.now()
    if resolution_date is None:
        if decision_type is None:
            raise ConveneError("pass either resolution_date or decision_type")
        resolution_date = resolution_date_for(decision_type, anchor.date())

    calls: list[SeatCall] = []
    for seat in seats:
        prompt = _SEAT_INSTRUCTION.format(
            question=question,
            decision=decision,
            statement=statement,
            resolution_date=resolution_date.isoformat(),
        )
        raw = client.complete(prompt, system=f"You are {seat.name}. {seat.persona}")
        calls.append(_parse_seat_call(seat.name, raw))

    board_probability = sum(c.probability for c in calls) / len(calls)
    prediction = Prediction(
        statement=statement,
        resolution_date=resolution_date,
        board_probability=board_probability,
    )
    return BoardMinute(
        id=id,
        question=question,
        prior=prior,
        decision=decision,
        prediction=prediction,
        seats=calls,
        created_at=anchor,
    )
