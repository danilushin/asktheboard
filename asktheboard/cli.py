"""Local CLI: convene a board (BYOK), persist board-minutes, grade, and score seats.

`create`/`resolve`/`score` need no network or key -- the foresight ledger runs
entirely on local files. `convene` is the BYOK fan-out: it reads YOUR key
(OPENAI_API_KEY) and runs the live LLM calls that *produce* a minute.

Usage:
  python -m asktheboard.cli convene --spec convene.json --model <m> [--base-url ...]
  python -m asktheboard.cli create  --spec minute.json [--dir board-minutes]
  python -m asktheboard.cli resolve --id <id> --outcome true|false [--note ...]
  python -m asktheboard.cli score   [--dir board-minutes]
"""

import argparse
import json
import math
import sys
from pathlib import Path

from .adr import render_adr
from .convene import Seat, convene
from .http_client import HTTPLLMClient
from .ledger import Ledger
from .model import BoardMinute
from .roster import panel as roster_panel
from .roster import panel_names, seat_slugs, seats as roster_seats


def _store(dirpath: str) -> Path:
    p = Path(dirpath)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _load_all(store: Path) -> list[BoardMinute]:
    out = []
    for f in sorted(store.glob("*.json")):
        out.append(BoardMinute.from_dict(json.loads(f.read_text(encoding="utf-8"))))
    return out


def _save(store: Path, minute: BoardMinute) -> Path:
    jpath = store / f"{minute.id}.json"
    jpath.write_text(json.dumps(minute.to_dict(), indent=2), encoding="utf-8")
    apath = store / f"{minute.id}.md"
    apath.write_text(render_adr(minute), encoding="utf-8")
    return apath


def _resolve_seats(args: argparse.Namespace, spec: dict) -> list[Seat]:
    """Seats from --seats > --panel > the spec's own seat list."""
    if args.seats:
        return roster_seats([s.strip() for s in args.seats.split(",") if s.strip()])
    if args.panel:
        return roster_panel(args.panel)
    spec_seats = spec.get("seats")
    if not spec_seats:
        raise SystemExit(
            "no seats: pass --seats <slugs> or --panel <name>, "
            'or put a "seats" list in the spec'
        )
    return [Seat(name=s["name"], persona=s.get("persona", "")) for s in spec_seats]


def cmd_convene(args: argparse.Namespace) -> int:
    store = _store(args.dir)
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    seats = _resolve_seats(args, spec)
    client = HTTPLLMClient(model=args.model, base_url=args.base_url)
    minute = convene(
        id=spec["id"],
        question=spec["question"],
        prior=spec.get("prior", ""),
        decision=spec["decision"],
        statement=spec["statement"],
        seats=seats,
        client=client,
        decision_type=spec.get("decision_type"),
        resolution_date=_date_or_none(spec.get("resolution_date")),
    )
    adr = _save(store, minute)
    print(f"convened {minute.id}: board P(true)={minute.prediction.board_probability:.2f}, "
          f"{len(minute.seats)} seats, resolves "
          f"{minute.prediction.resolution_date.isoformat()}")
    print(f"  ADR -> {adr}")
    return 0


def _date_or_none(s):
    from datetime import date
    return date.fromisoformat(s) if s else None


def cmd_roster(args: argparse.Namespace) -> int:
    print("bundled seats:")
    for slug in seat_slugs():
        print(f"  {slug}")
    print("\npanels:")
    for name in panel_names():
        members = ", ".join(s.name for s in roster_panel(name))
        print(f"  {name:<10} {members}")
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    store = _store(args.dir)
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    minute = BoardMinute.from_dict(spec)
    adr = _save(store, minute)
    print(f"created {minute.id}: pre-registered, resolves "
          f"{minute.prediction.resolution_date.isoformat()}")
    print(f"  ADR -> {adr}")
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    store = _store(args.dir)
    jpath = store / f"{args.id}.json"
    if not jpath.exists():
        print(f"no such minute: {args.id}", file=sys.stderr)
        return 1
    minute = BoardMinute.from_dict(json.loads(jpath.read_text(encoding="utf-8")))
    outcome = args.outcome.lower() in ("true", "t", "yes", "y", "1")
    minute.resolve(outcome, note=args.note or "")
    _save(store, minute)
    verdict = "VINDICATED" if minute.vindicated else "REFUTED"
    print(f"resolved {minute.id}: outcome={'TRUE' if outcome else 'FALSE'} -- {verdict}")
    print(f"  board Brier {minute.board_brier():.3f}")
    winners = minute.contrarian_winners()
    if winners:
        print(f"  contrarian wins: {', '.join(winners)}")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    store = _store(args.dir)
    ledger = Ledger()
    ledger.extend(_load_all(store))
    ranked = ledger.ranked_seats()
    if not ranked:
        print("no resolved minutes yet -- nothing to score")
        return 0
    print(f"{'seat':<16} {'n':>3} {'mean_brier':>11} {'wins':>5} {'losses':>7}")
    print("-" * 46)
    for sc in ranked:
        mb = "n/a" if math.isnan(sc.mean_brier) else f"{sc.mean_brier:.3f}"
        print(f"{sc.seat:<16} {sc.resolved_count:>3} {mb:>11} "
              f"{sc.contrarian_wins:>5} {sc.contrarian_losses:>7}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="asktheboard", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("convene", help="BYOK: run the live LLM fan-out to produce a minute")
    v.add_argument("--spec", required=True, help="path to the convene JSON spec")
    v.add_argument("--model", required=True, help="model id (e.g. gpt-4o-mini)")
    v.add_argument("--base-url", default="https://api.openai.com/v1",
                   help="OpenAI-compatible API base URL")
    v.add_argument("--seats", default="",
                   help="comma-separated roster slugs (e.g. architect,skeptic); "
                        "overrides the spec's seats")
    v.add_argument("--panel", default="",
                   help="a named panel from the bundled roster (e.g. tech); "
                        "used if --seats is absent")
    v.add_argument("--dir", default="board-minutes", help="store directory")
    v.set_defaults(func=cmd_convene)

    rb = sub.add_parser("roster", help="list the bundled seats and panels")
    rb.set_defaults(func=cmd_roster)

    c = sub.add_parser("create", help="pre-register a board-minute from a JSON spec")
    c.add_argument("--spec", required=True, help="path to the minute JSON spec")
    c.add_argument("--dir", default="board-minutes", help="store directory")
    c.set_defaults(func=cmd_create)

    r = sub.add_parser("resolve", help="grade a minute against reality")
    r.add_argument("--id", required=True)
    r.add_argument("--outcome", required=True, help="true|false")
    r.add_argument("--note", default="")
    r.add_argument("--dir", default="board-minutes")
    r.set_defaults(func=cmd_resolve)

    s = sub.add_parser("score", help="per-seat calibration over resolved minutes")
    s.add_argument("--dir", default="board-minutes")
    s.set_defaults(func=cmd_score)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
