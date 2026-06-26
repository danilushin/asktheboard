"""BYOK boundary -- the engine's only contract with an LLM provider.

Bring your own API key: ask-the-board ships NO bundled provider and makes NO
calls of its own. You implement (or plug in) a client that uses *your* key and
pays *your* inference. That is the structural reason the engine costs nothing to
run at any scale -- the cost lives with the user, not the host.

Keeping this an explicit Protocol from commit 1 (rather than hard-wiring a vendor
SDK) is the un-walk-back-able architectural choice that makes the open-source core
honestly free.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    """Minimal completion contract. Implementations own auth with the user's key."""

    def complete(self, prompt: str, *, system: str = "") -> str:
        """Return the model's text completion for `prompt`."""
        ...


class NoProviderConfigured(RuntimeError):
    """Raised when the engine is asked to generate without a BYOK client."""


def require_client(client: "LLMClient | None") -> "LLMClient":
    if client is None:
        raise NoProviderConfigured(
            "ask-the-board is bring-your-own-key: pass an LLMClient backed by your "
            "own provider API key. No provider is bundled by design."
        )
    return client
