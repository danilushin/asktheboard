# Changelog

All notable changes are documented here. This project follows
[Semantic Versioning](https://semver.org/); before `1.0`, minor versions may
introduce breaking changes.

## [0.2.4] -- 2026-07-02

### Changed
- **Bet #1 resolved -- REFUTED.** June 2026 nonfarm payrolls came in at +114K (below the +150K
  threshold). The board's 56% call was wrong; the skeptic's 40% dissent was most accurate
  (Brier 0.160 vs board average 0.314). The skeptic earns round 1's contrarian win.
- `examples/2026-06-jobs-report.json` and `.md` updated with resolution, realized outcome, and
  per-seat Brier scores.
- `examples/scoreboard.txt` regenerated: researcher/strategist added (their first resolved minute);
  skeptic now 2 minutes, 1 contrarian win.
- Landing page (`docs/index.html`): live-bet section updated from LIVE to REFUTED with outcome
  and Brier scores; "See it keep score" scoreboard updated to reflect actual live bet results.

## [0.2.3] -- 2026-06-27

### Added
- **Live public bet #1** (`examples/2026-06-jobs-report.{json,md}`): a fast-resolving,
  git-anchored board call on the June 2026 US jobs report -- filed 2026-06-27, resolving
  2026-07-02 against the BLS Employment Situation release. The board says +150k or more at
  56%; the skeptic dissents at 40%. The first bet of a public, recurring cadence, so the
  launch scoreboard shows a real call graded against reality, not a 0-0 promise.
- **Machine-ingest substrate** for answer engines / AI crawlers: `docs/llms.txt`,
  `docs/llms-full.txt`, `docs/robots.txt` (GPTBot / ClaudeBot / PerplexityBot /
  Google-Extended explicitly allowed), and `docs/sitemap.xml`.
- **JSON-LD** `SoftwareApplication` structured data plus a canonical link on the landing
  page (`docs/index.html`), so the project is machine-readable and citable.

### Changed
- Landing page + README now lead the live bet above the fold ("come back and watch it
  grade") and sharpen the positioning toward pre-registered, falsifiable forecasting. No
  engine or API changes -- behavior is identical to 0.2.2.

## [0.2.2] -- 2026-06-26

### Changed
- Renamed the demo/example seat `karpathy` to the generic role `pragmatist`
  across the README, landing page (`docs/index.html`), animated demo
  (`docs/demo.svg`), and the `examples/` artifacts (plus the test fixtures).
  The shipped roster is generic role archetypes by design; the sample data now
  matches that and avoids using a real person's name. No code or API changes --
  engine behavior is identical to 0.2.1.

## [0.2.1] -- 2026-06-26

### Added
- README: a "Hosted tier -- join the waitlist" section (email capture). No code
  or API changes -- engine behavior is identical to 0.2.0.
- A self-contained landing page (`docs/index.html`) served via GitHub Pages at
  https://danilushin.github.io/asktheboard/ -- linked from the README and the
  PyPI project sidebar (`Documentation` / `Homepage` URLs).
- An animated terminal demo (`docs/demo.svg`, dependency-free SMIL/CSS) of
  `create -> resolve -> score`, embedded at the top of the README and in the
  landing-page hero.
- A 1200x630 social-preview image (`docs/og.png`) wired as `og:image` /
  `twitter:image` on the landing page (and usable as the GitHub repo social card).
- A real, open board-minute (`examples/open-minute.{json,md}`) pre-registering
  this project's own inbound-only launch bet -- anchored 2026-06-26, resolving
  2026-09-24, unresolved on purpose so the repo keeps score in public from day 0.

### Changed
- README + landing page lead with `pip install` and the demo before the rationale;
  the Quick start opens with `pip install` instead of `python -m pytest`.
- The showcase scoreboard is now captioned honestly as a *mechanism on sample
  data* (you supply the outcome with `resolve`), not a track record -- the
  integrity claim rests on the anchor timestamp, not the demo numbers.

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
