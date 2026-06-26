"""A minimal, dependency-free OpenAI-compatible LLMClient (BYOK).

Stdlib `urllib` only -- no `openai`, no `requests` -- so the open-source core stays
zero-dependency and the BYOK promise is literal: you bring the key, you bring the
endpoint, the engine bundles neither. Works against any OpenAI-compatible
`/chat/completions` API (OpenAI, OpenRouter, Together, a local server) by setting
`base_url` + `model`.

This satisfies the `LLMClient` Protocol structurally; nothing imports a vendor SDK.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


class HTTPLLMClient:
    """OpenAI-compatible chat client. Reads your key; pays your inference."""

    def __init__(
        self,
        *,
        model: str,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 60.0,
        temperature: float = 0.7,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "no API key: pass api_key= or set OPENAI_API_KEY. ask-the-board is "
                "bring-your-own-key -- it ships no provider and no credentials."
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.temperature = temperature

    def complete(self, prompt: str, *, system: str = "") -> str:
        """POST a chat completion and return the assistant's text."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = json.dumps(
            {"model": self.model, "messages": messages, "temperature": self.temperature}
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:  # surface the provider's error body
            body = e.read().decode("utf-8", "replace")
            raise RuntimeError(f"LLM request failed ({e.code}): {body}") from e
        return data["choices"][0]["message"]["content"]
