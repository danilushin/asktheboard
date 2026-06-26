# 60-second quickstart -- no API key needed

`create` -> `resolve` -> `score` is pure data: no LLM, no key, no network. You can
watch the board keep score in under a minute. (`convene` is the only path that
calls an LLM -- that one is BYOK; see the [root README](../README.md).)

## Run it

```bash
# 1. pre-register a decision as a board-minute (the spec ships with the repo)
asktheboard create  --spec tests/sample_minute.json

# 2. on/after the resolution date, grade it against reality
asktheboard resolve --id 2026-01-postgres-vs-vectordb --outcome true

# 3. per-seat calibration scoreboard, best-calibrated first
asktheboard score
```

## What you'll see

A resolved, graded board-minute -- the affirming seat (`karpathy`) was right, the
dissenting `skeptic` was wrong, and the scoreboard ranks them by Brier score
(lower is better):

```
seat               n  mean_brier  wins  losses
----------------------------------------------
karpathy           1       0.040     0       0
skeptic            1       0.423     0       1
```

The three files in this folder are the **real** output of those commands:

- [`resolved-minute.json`](resolved-minute.json) -- the machine record
- [`resolved-minute.md`](resolved-minute.md) -- the git-committable ADR
- [`scoreboard.txt`](scoreboard.txt) -- the per-seat calibration table

Your own runs write to `board-minutes/` (gitignored). Commit those to your repo --
your git history is the external attestation of each anchor timestamp.

## A real, open bet -- keeping score before the fact

The resolved minute above is a worked example on sample data. This one is not:
[`open-minute.md`](open-minute.md) ([`.json`](open-minute.json)) is a genuine,
**unresolved** board-minute this project pre-registered about *its own launch* --
anchored in git on 2026-06-26, **before** the outcome was knowable, resolving
2026-09-24.

```
Status: Pre-registered (resolves 2026-09-24)
Decision: launch inbound-only (free OSS BYOK engine, no outbound)
Prediction: >=1 unsolicited external pull signal within 90 days  (board 55%)
Dissent:    skeptic at 25% -- "inbound-only with no audience is the base rate for silence"
```

No score yet -- that is the whole point. On 2026-09-24 the maintainer runs
`asktheboard resolve` against reality and the seats get graded in public. The
board may well be **wrong**, and the git anchor means it cannot quietly pretend
otherwise. That is what "keeps score, before the fact" means.
