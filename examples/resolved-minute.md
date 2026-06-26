# ADR-2026-01-postgres-vs-vectordb: Adopt Postgres + pgvector, or a dedicated vector DB?

- **Status:** Resolved 2026-04-02 -- VINDICATED
- **Anchored:** 2026-01-05T10:30:00
- **Resolution date:** 2026-04-01

## Context (stated prior)

Leaning toward a dedicated vector DB for the embeddings workload.

## Decision

Stay on Postgres + pgvector for now.

## Pre-registered prediction

> We will NOT migrate off Postgres for vectors within 3 months.

- **Board confidence:** 75% that this resolves TRUE
- **Resolves:** 2026-04-01

## Board seats (dissent vector)

| Seat | Stance | P(true) | Brier | Rationale |
|---|---|---|---|---|
| karpathy | affirm | 80% | 0.040 | Boring tech; pgvector is enough at this scale. |
| skeptic | dissent | 35% | 0.423 | Recall/latency will bite once the corpus 10x's. |

## Resolution

- **Realized outcome:** TRUE
- **Board Brier:** 0.062 (lower is better)
