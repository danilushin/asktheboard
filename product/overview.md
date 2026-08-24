# ask-the-board — Product Overview

**A board of expert personas whose every decision is a pre-registered,
time-anchored, reality-graded bet.** Not a chatbot that agrees with you — a
board that keeps score, *before* the fact.

- **Distribution:** Python package on PyPI (`pip install asktheboard`), MIT
  license, Python 3.10+.
- **Docs / landing:** <https://danilushin.github.io/asktheboard/>

## Why it exists

The "panel of AI personas" debate mechanic is a commodity. What it leaves out
is the thing that makes advice worth trusting: a record of having been right
*before the outcome was knowable*. That record is hard to fake — you can buy
model outputs, but you can't back-date a timestamp. It accrues the slow way:
by calling decisions in advance and letting reality grade them.

## Core mechanism

For every decision the board records:

1. the **stated prior** (what you believed going in),
2. the **per-seat dissent vector** — each seat's stance + its own probability,
3. a **dated, falsifiable prediction**, anchored *before* the outcome is
   knowable,
4. on the resolution date, reality's **realized outcome**, auto-reconciled into
   a **Brier/calibration score per seat**.

The board-minute is a **git-committable ADR**; git history is the external
attestation of the anchor timestamp. `create → resolve → score` is pure data —
no LLM, no key, no network required for the scoring loop.

## Repo layout (top level)

- `asktheboard/` — the engine (package source)
- `tests/` — test suite (incl. `sample_minute.json` walkthrough fixture)
- `examples/` — committed worked-example artifacts
- `docs/` — landing page + demo assets
- `product/` — this dir: overview, roadmap, specs, PRDs (eng-flow work surface)
- `decisions/` — accepted ADRs produced by the engineering flow
