# 60-second quickstart -- no API key needed

`create` -> `resolve` -> `score` is pure data: no LLM, no key, no network. You can
watch the board keep score in under a minute. (`convene` is the only path that
calls an LLM -- that one is BYOK; see the [root README](../README.md).)

## Run it

```bash
# 1. pre-register a decision as a board-minute (the spec ships with the repo)
python -m asktheboard.cli create  --spec tests/sample_minute.json

# 2. on/after the resolution date, grade it against reality
python -m asktheboard.cli resolve --id 2026-01-postgres-vs-vectordb --outcome true

# 3. per-seat calibration scoreboard, best-calibrated first
python -m asktheboard.cli score
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
