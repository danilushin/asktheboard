"""ask-the-board (OSS) -- a board of expert personas whose every decision is a
pre-registered, time-anchored, reality-graded bet.

BYOK (bring your own API key): you supply your own LLM key, you pay your own
inference, the engine costs nothing to run at any scale. The durable asset is the
accumulating, externally attested track record -- the board that keeps score,
before the fact.
"""

from .model import (
    BoardMinute,
    IntegrityError,
    Prediction,
    Resolution,
    SeatCall,
    brier,
)
from .ledger import Ledger, SeatScore
from .llm import LLMClient, NoProviderConfigured, require_client
from .convene import ConveneError, Seat, convene
from .http_client import HTTPLLMClient
from .decision_types import (
    CATALOG,
    DecisionType,
    UnknownDecisionType,
    resolution_date_for,
)
from .roster import (
    UnknownPanel,
    UnknownSeat,
    panel,
    panel_names,
    seat,
    seat_slugs,
    seats,
)

__all__ = [
    "BoardMinute",
    "Prediction",
    "Resolution",
    "SeatCall",
    "IntegrityError",
    "brier",
    "Ledger",
    "SeatScore",
    "LLMClient",
    "NoProviderConfigured",
    "require_client",
    "Seat",
    "convene",
    "ConveneError",
    "HTTPLLMClient",
    "DecisionType",
    "CATALOG",
    "UnknownDecisionType",
    "resolution_date_for",
    "seat",
    "seats",
    "panel",
    "seat_slugs",
    "panel_names",
    "UnknownSeat",
    "UnknownPanel",
]

__version__ = "0.2.0"
