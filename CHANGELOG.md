# Changelog

All notable changes are documented here. This project follows
[Semantic Versioning](https://semver.org/); before `1.0`, minor versions may
introduce breaking changes.

## [0.2.0] -- 2026-06-26

Initial public release.

### Added
- Foresight data model: pre-registered, time-anchored, falsifiable board-minutes
  with a per-seat dissent vector and frozen anchor timestamps.
- Reality grading: per-seat Brier scores, contrarian-win detection, and a
  calibration scoreboard (`score`).
- Git-committable ADR rendering for every board-minute.
- BYOK live convening (`convene`) behind the `asktheboard.llm.LLMClient` protocol;
  zero-dependency, OpenAI-compatible `HTTPLLMClient` (OpenAI, OpenRouter, Together,
  or a local server).
- Bundled roster of role archetypes + named panels.
- Decision-type default horizons (library 90d / migration 180d / architecture 365d).
- CLI: `create`, `resolve`, `score`, `convene`, `roster`.

### Notes
- The public API is `0.x` / unstable until `1.0`.
