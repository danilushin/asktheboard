"""Accumulate per-seat calibration across many resolved board-minutes.

This is the scoreboard's data source: for each seat, how well-calibrated it has
been over its resolved calls (mean Brier, lower is better), and its contrarian
record -- how often it broke from the board and reality proved it right.
"""

from dataclasses import dataclass, field

from .model import BoardMinute


@dataclass
class SeatScore:
    seat: str
    resolved_count: int = 0
    brier_sum: float = 0.0
    contrarian_wins: int = 0
    contrarian_losses: int = 0  # dissented, but the board was more right

    @property
    def mean_brier(self) -> float:
        if self.resolved_count == 0:
            return float("nan")
        return self.brier_sum / self.resolved_count

    def to_dict(self) -> dict:
        return {
            "seat": self.seat,
            "resolved_count": self.resolved_count,
            "mean_brier": self.mean_brier,
            "contrarian_wins": self.contrarian_wins,
            "contrarian_losses": self.contrarian_losses,
        }


class Ledger:
    """A running tally over resolved minutes. Open minutes are ignored."""

    def __init__(self) -> None:
        self.minutes: list[BoardMinute] = []

    def add(self, minute: BoardMinute) -> None:
        self.minutes.append(minute)

    def extend(self, minutes) -> None:
        for m in minutes:
            self.add(m)

    @property
    def resolved_minutes(self) -> list[BoardMinute]:
        return [m for m in self.minutes if m.resolved]

    def seat_calibration(self) -> dict[str, SeatScore]:
        scores: dict[str, SeatScore] = {}
        for m in self.resolved_minutes:
            briers = m.seat_briers()
            board = m.board_brier()
            o = m.resolution.realized_outcome
            for s in m.seats:
                sc = scores.setdefault(s.seat, SeatScore(seat=s.seat))
                sc.resolved_count += 1
                sc.brier_sum += s.brier(o)
                if s.stance == "dissent":
                    if s.brier(o) < board:
                        sc.contrarian_wins += 1
                    else:
                        sc.contrarian_losses += 1
        return scores

    def ranked_seats(self) -> list[SeatScore]:
        """Seats ordered best-calibrated first (lowest mean Brier)."""
        return sorted(self.seat_calibration().values(), key=lambda sc: sc.mean_brier)
