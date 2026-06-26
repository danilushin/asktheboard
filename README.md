# ask-the-board

[![CI](https://github.com/danilushin/asktheboard/actions/workflows/ci.yml/badge.svg)](https://github.com/danilushin/asktheboard/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/asktheboard.svg)](https://pypi.org/project/asktheboard/)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**A board of expert personas whose every decision is a pre-registered,
time-anchored, reality-graded bet.** Not a chatbot that agrees with you -- a board
that keeps score, *before* the fact.

> Status: Phase-0 core + live convening. The **foresight engine** (data model +
> grading + committable ADR) and the **BYOK LLM fan-out** that *produces* a
> board-minute (`asktheboard.convene`, behind the `asktheboard.llm` Protocol) are
> both in. No provider is bundled -- you plug in your own key.

## Why this exists

Anyone can clone a "panel of AI personas" in a weekend, and a dozen have. The
debate mechanic is a commodity. What it leaves out is the thing that makes advice
worth trusting: a record of having been right *before the outcome was knowable*.
That record is **hard to fake** -- you can buy model outputs, but you can't
back-date a timestamp. It only accrues the slow way: by calling decisions in
advance and letting reality grade them, one resolution date at a time.

So ask-the-board records, for every decision:

1. your **stated prior** (what you believed going in),
2. the **per-seat dissent vector** -- each seat's stance + its own probability,
3. a **dated, falsifiable prediction**, anchored *before* the outcome is knowable,
4. on the resolution date, reality's **realized outcome**, auto-reconciled into a
   **Brier/calibration score per seat**.

The board-minute is a **git-committable ADR**. Your git history is the external
attestation of the anchor timestamp. The accumulating, reality-graded record is
the durable asset.

## See it keep score (60s, no API key)

`create -> resolve -> score` is pure data -- no LLM, no key, no network. The
[`examples/`](examples/) folder holds a **real** resolved board-minute: the
affirming seat called it right, the dissenting `skeptic` got it wrong, and the
scoreboard ranks them by Brier score (lower is better).

```bash
# pip-installed (no repo)? paste the sample spec below. Cloned the repo?
# skip the heredoc and use --spec tests/sample_minute.json instead.
cat > sample_minute.json <<'JSON'
{
  "id": "2026-01-postgres-vs-vectordb",
  "question": "Adopt Postgres + pgvector, or a dedicated vector DB?",
  "prior": "Leaning toward a dedicated vector DB for the embeddings workload.",
  "decision": "Stay on Postgres + pgvector for now.",
  "prediction": {
    "statement": "We will NOT migrate off Postgres for vectors within 3 months.",
    "resolution_date": "2026-04-01",
    "board_probability": 0.75
  },
  "seats": [
    {"seat": "karpathy", "stance": "affirm", "probability": 0.8, "rationale": "Boring tech; pgvector is enough at this scale."},
    {"seat": "skeptic", "stance": "dissent", "probability": 0.35, "rationale": "Recall/latency will bite once the corpus 10x's."}
  ],
  "created_at": "2026-01-05T10:30:00"
}
JSON

python -m asktheboard.cli create  --spec sample_minute.json
python -m asktheboard.cli resolve --id 2026-01-postgres-vs-vectordb --outcome true
python -m asktheboard.cli score
```

```
seat               n  mean_brier  wins  losses
----------------------------------------------
karpathy           1       0.040     0       0
skeptic            1       0.423     0       1
```

Full walkthrough + committed artifacts: [`examples/README.md`](examples/README.md).

## BYOK (bring your own API key)

The engine ships no provider and makes no calls of its own. You supply your own
LLM key; you pay your own inference. The open-source core therefore costs nothing
to run at any scale -- the cost lives with the user, not a host. (A managed,
capped hosted tier -- for people who would rather not manage keys -- is the
separate, paid product.)

## Integrity guarantees (enforced in code)

- A prediction **cannot be pre-registered to resolve in the past** (no backfilling
  an "old" call onto a known outcome).
- A minute **cannot be graded before its resolution date** -- the outcome must not
  be knowable yet. That is what makes it *foresight*.
- The anchor timestamp and the prediction are **frozen** once created; grading
  never moves them.

See `tests/test_model.py` -- these are the load-bearing tests.

## Quick start

```bash
python -m pytest                       # run the suite

# pre-register a decision (the board-minute spec is JSON)
python -m asktheboard.cli create  --spec tests/sample_minute.json

# ... months later, on/after the resolution date, grade it against reality
python -m asktheboard.cli resolve --id 2026-01-postgres-vs-vectordb --outcome false

# per-seat calibration scoreboard, best-calibrated first
python -m asktheboard.cli score
```

`create` writes both `<id>.json` (the record) and `<id>.md` (the committable ADR)
into `board-minutes/`.

## Convene a board (BYOK)

`create` pre-registers a minute you wrote by hand. `convene` runs the **live LLM
fan-out**: every seat answers through *your* key, and the board's consensus
probability is the mean of the seats' calls. It ships no provider -- bring an
OpenAI-compatible endpoint (`HTTPLLMClient` is stdlib-only, zero dependencies).

```python
from asktheboard import convene, Seat, HTTPLLMClient

minute = convene(
    id="pgvector-scale",
    question="Will pgvector hold our scale, or do we need a dedicated vector DB?",
    prior="leaning postgres to avoid a new service",
    decision="stay on postgres + pgvector",
    statement="pgvector serves p95<150ms at 50M embeddings without a dedicated DB",
    seats=[Seat("karpathy", "ML researcher"), Seat("skeptic", "find the failure mode")],
    client=HTTPLLMClient(model="gpt-4o-mini"),   # reads OPENAI_API_KEY
    decision_type="library",                     # -> 90-day resolution horizon
)
```

Or from the CLI (key in `OPENAI_API_KEY`):

```bash
python -m asktheboard.cli convene --spec convene.json --model gpt-4o-mini
```

Any OpenAI-compatible API works -- point `--base-url` (or `HTTPLLMClient(base_url=...)`)
at OpenRouter, Together, or a local server. The engine still makes no calls of its
own; it only ever speaks through the client you pass.

### Bundled roster -- seat a board by name

You can always hand-write `Seat(name, persona)`. But a sensible default board ships
in the box: a curated set of *role archetypes* (the architect, the skeptic, the
operator -- functions, not impersonations of real people) and a few named panels,
so seating one is a single lookup.

```python
from asktheboard import convene, panel, seats, HTTPLLMClient

minute = convene(
    id="pgvector-scale",
    question="Will pgvector hold our scale, or do we need a dedicated vector DB?",
    prior="leaning postgres",
    decision="stay on postgres + pgvector",
    statement="pgvector serves p95<150ms at 50M embeddings without a dedicated DB",
    seats=panel("tech"),                  # architect + skeptic + pragmatist
    # seats=seats(["architect", "operator", "skeptic"]),   # or pick your own
    client=HTTPLLMClient(model="gpt-4o-mini"),
    decision_type="library",
)
```

From the CLI, pass `--panel` or `--seats` instead of putting seats in the spec:

```bash
python -m asktheboard.cli roster                                   # list seats + panels
python -m asktheboard.cli convene --spec d.json --model gpt-4o-mini --panel tech
python -m asktheboard.cli convene --spec d.json --model gpt-4o-mini --seats architect,skeptic
```

| seat | voice |
|---|---|
| `architect` | shape, maintenance cost, what breaks at scale, build-vs-buy |
| `skeptic` | forced dissent -- the most likely failure first, then the deeper objection |
| `pragmatist` | simplest thing that ships; YAGNI; opportunity cost |
| `researcher` | what the data actually says; base rate before anecdote |
| `operator` | run cost, failure budget, who gets paged at 3am |
| `strategist` | base rates, second-order effects, one-way vs reversible doors |

Panels: `tech` (architect/skeptic/pragmatist), `decision` (strategist/skeptic/researcher),
`ops` (operator/architect/skeptic), `default` (architect/skeptic/pragmatist/strategist).
`skeptic` sits on every panel by design -- a board with no dissent keeps no honest score.

### Decision types -> default horizons

A minute is only foresight if it has a date by which reality can grade it.
`decision_type` picks a sensible default horizon so the common case is one lookup
(and a 5-year horizon on a library swap stands out as dishonest):

| type | horizon | when |
|---|---|---|
| `library` | 90d | adopt/swap/drop a dependency |
| `migration` | 180d | move a datastore, platform, or pipeline |
| `architecture` | 365d | a structural design bet you live with |

Short-latency first on purpose: a fresh board earns a track record on fast `library`
calls before anyone trusts its slow `architecture` bets. Pass an explicit
`resolution_date=` to override.

## A contrarian win

When a seat **dissents** from the board and turns out more right than the
consensus, that is a *contrarian win* -- the gold the public scoreboard is built
from. The board changed (or should have changed) its mind, and reality later
stamped the dissenter vindicated.

## Stability

The public API is **`0.x` / unstable**. The `LLMClient` / `HTTPLLMClient` surface
and the board-minute JSON schema may change before `1.0` -- pin a version if you
depend on them.

## Built with

Built by [Dan Ilushin](https://github.com/danilushin) with Claude (Anthropic) in
the loop. Contributions welcome -- see [CONTRIBUTING.md](CONTRIBUTING.md)
(DCO sign-off) and [SECURITY.md](SECURITY.md).

## License

MIT. (c) 2026 Dan Ilushin.
