import json
import urllib.request

import pytest

from asktheboard.http_client import HTTPLLMClient


class _FakeResp:
    def __init__(self, payload):
        self._p = payload

    def read(self):
        return json.dumps(self._p).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_requires_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError):
        HTTPLLMClient(model="gpt-4o-mini")


def test_reads_key_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    c = HTTPLLMClient(model="m")
    assert c.api_key == "sk-test"


def test_complete_posts_openai_shape_and_parses(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["method"] = req.get_method()
        captured["headers"] = {k.lower(): v for k, v in req.header_items()}
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _FakeResp({"choices": [{"message": {"content": "hello"}}]})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    c = HTTPLLMClient(model="gpt-4o-mini", api_key="sk-x",
                      base_url="https://api.example.com/v1/")
    out = c.complete("hi there", system="be terse")

    assert out == "hello"
    assert captured["url"] == "https://api.example.com/v1/chat/completions"
    assert captured["method"] == "POST"
    assert captured["headers"]["authorization"] == "Bearer sk-x"
    assert captured["body"]["model"] == "gpt-4o-mini"
    assert captured["body"]["messages"] == [
        {"role": "system", "content": "be terse"},
        {"role": "user", "content": "hi there"},
    ]


def test_complete_omits_empty_system(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _FakeResp({"choices": [{"message": {"content": "ok"}}]})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    c = HTTPLLMClient(model="m", api_key="sk-x")
    c.complete("just user")
    assert captured["body"]["messages"] == [{"role": "user", "content": "just user"}]
