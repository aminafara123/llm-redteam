"""Thin OpenAI-compatible chat client (the single place the harness talks to an LLM).

Defaults to a local ollama server. Configured only by environment variables, never
hardcode a key. The "target under test" is reached through `chat()`.

Env:
  LLM_BASE_URL  default http://127.0.0.1:11434/v1
  LLM_MODEL     default qwen3:30b-a3b-instruct-2507-q4_K_M
  LLM_API_KEY   default "ollama" (ollama ignores it; a hosted provider would use it)

Stdlib only (urllib) so the harness has no HTTP dependency.
"""
import json
import os
import urllib.error
import urllib.request

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:11434/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3:30b-a3b-instruct-2507-q4_K_M")
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")


class LLMError(Exception):
    """Raised when the target endpoint is unreachable or returns an unusable reply."""


def chat(messages, model=None, temperature=0.0, timeout=60, base_url=None, api_key=None):
    """Call an OpenAI-compatible /chat/completions endpoint and return the reply text.

    Raises LLMError on any network/protocol problem so callers can degrade gracefully
    instead of crashing.
    """
    url = (base_url or LLM_BASE_URL).rstrip("/") + "/chat/completions"
    payload = {"model": model or LLM_MODEL, "messages": messages, "temperature": temperature}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key or LLM_API_KEY}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = json.loads(r.read())
        return body["choices"][0]["message"]["content"]
    except (urllib.error.URLError, OSError, KeyError, IndexError, ValueError) as e:
        raise LLMError(f"request to {url} failed: {e}") from e
