# Contributing

Thanks for considering a contribution.

## Ground rules

- The engine stays **provider-agnostic and dependency-free**. The core makes no
  network calls of its own; anything that talks to an LLM goes behind the
  `asktheboard.llm.LLMClient` protocol (BYOK). PRs that bundle a provider SDK or
  add a hard runtime dependency will be declined.
- Keep the integrity rules intact: a prediction cannot be back-dated, a minute
  cannot be graded before its resolution date, the anchor is frozen. These are the
  whole point of the project, and `tests/test_model.py` guards them.
- Add or update tests for any behaviour change. `python -m pytest` must stay green.

## Interface stability

The public API is **`0.x` / unstable**. The `LLMClient` / `HTTPLLMClient` surface
and the board-minute JSON schema may change before `1.0`. Pin a version if you
depend on them.

## Developer Certificate of Origin (DCO)

This project uses the [DCO](https://developercertificate.org/) instead of a CLA.
Sign off every commit -- it certifies you wrote the patch, or have the right to
submit it under the MIT license:

```bash
git commit -s -m "your message"
```

That appends a `Signed-off-by: Your Name <you@example.com>` line. PRs without
sign-off cannot be merged.

## Questions

Open an issue, or reach the maintainer at **dilushin@chu6a.dev**.
