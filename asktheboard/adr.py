"""Render a BoardMinute as a git-committable Architecture Decision Record.

The board-minute IS the artifact: a markdown ADR a user commits to their own
repo. Git history then provides the external attestation of the anchor timestamp
-- the thing a funded competitor cannot retroactively manufacture.
"""

from .model import BoardMinute


def _pct(p: float) -> str:
    return f"{round(p * 100)}%"


def render_adr(minute: BoardMinute) -> str:
    m = minute
    if m.resolution is None:
        status = f"Pre-registered (resolves {m.prediction.resolution_date.isoformat()})"
    else:
        verdict = "VINDICATED" if m.vindicated else "REFUTED"
        status = f"Resolved {m.resolution.resolved_at.date().isoformat()} -- {verdict}"

    lines: list[str] = []
    lines.append(f"# ADR-{m.id}: {m.question}")
    lines.append("")
    lines.append(f"- **Status:** {status}")
    lines.append(f"- **Anchored:** {m.created_at.isoformat()}")
    lines.append(f"- **Resolution date:** {m.prediction.resolution_date.isoformat()}")
    lines.append("")
    lines.append("## Context (stated prior)")
    lines.append("")
    lines.append(m.prior.strip() or "_none recorded_")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(m.decision.strip() or "_none recorded_")
    lines.append("")
    lines.append("## Pre-registered prediction")
    lines.append("")
    lines.append(f"> {m.prediction.statement.strip()}")
    lines.append("")
    lines.append(f"- **Board confidence:** {_pct(m.prediction.board_probability)} that this resolves TRUE")
    lines.append(f"- **Resolves:** {m.prediction.resolution_date.isoformat()}")
    lines.append("")
    lines.append("## Board seats (dissent vector)")
    lines.append("")
    if m.seats:
        resolved = m.resolution is not None
        header = "| Seat | Stance | P(true) | "
        sep = "|---|---|---|"
        if resolved:
            header += "Brier | "
            sep += "---|"
        header += "Rationale |"
        sep += "---|"
        lines.append(header)
        lines.append(sep)
        briers = m.seat_briers()
        for s in m.seats:
            row = f"| {s.seat} | {s.stance} | {_pct(s.probability)} | "
            if resolved:
                row += f"{briers[s.seat]:.3f} | "
            row += f"{s.rationale.strip().replace(chr(10), ' ')} |"
            lines.append(row)
    else:
        lines.append("_no seats recorded_")
    lines.append("")

    if m.resolution is not None:
        o = "TRUE" if m.resolution.realized_outcome else "FALSE"
        lines.append("## Resolution")
        lines.append("")
        lines.append(f"- **Realized outcome:** {o}")
        lines.append(f"- **Board Brier:** {m.board_brier():.3f} (lower is better)")
        winners = m.contrarian_winners()
        if winners:
            lines.append(f"- **Contrarian wins:** {', '.join(winners)} "
                         f"(dissented and beat the consensus)")
        if m.resolution.note.strip():
            lines.append(f"- **Note:** {m.resolution.note.strip()}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
