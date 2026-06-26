# Security Policy

## Reporting a vulnerability

Please report security issues privately to **support@chu6a.dev**. Do not open a
public issue for anything exploitable.

Include a description, reproduction steps, the affected version, and the impact.
You will get an acknowledgement within a few business days.

## Threat model

`asktheboard` ships no server and makes no network calls of its own. The single
network path is `HTTPLLMClient`, which POSTs to the OpenAI-compatible `base_url`
**you** configure, using the API key **you** supply.

- Keep your key in the environment (`OPENAI_API_KEY`), never in a committed
  board-minute, spec, or example file.
- Board-minute JSON is data you control; the engine does not execute it.

## Supported versions

This is a `0.x` release. Only the latest published version receives fixes.
