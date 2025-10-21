"""
Pluggable model provider for agentic patterns.

This module exposes a `call_model` function that returns a response string
given a sequence of messages (role/content pairs).  It supports two modes:

* **Stub mode (default):** When the environment variable `USE_OPENAI` is
  unset or set to a falsy value, a simple rule‑based stub is used.  The stub
  generates predictable outputs for demonstration purposes, such as
  generating marketing copy or translating short phrases based on a small
  dictionary.  It returns a tuple of `(response, usage)`, where `usage` is a
  dictionary with mock token counts.

* **OpenAI mode:** When `USE_OPENAI=true` and a valid `OPENAI_API_KEY` is
  provided in the environment, the function delegates to the OpenAI chat
  completion API.  It returns the assistant's message and actual token
  usage (if provided by the API).

You can extend this module to support other providers or custom logic.
"""

from __future__ import annotations

import os
import random
from typing import Dict, List, Tuple


# Simple translation dictionary for the stub.  Extend as needed.
_TRANSLATIONS = {
    "es": {
        "Buy now": "Comprar ahora",
        "Learn more": "Más información",
        "Try it free": "Pruébalo gratis",
    },
    "fr": {
        "Buy now": "Achetez maintenant",
        "Learn more": "En savoir plus",
        "Try it free": "Essayez gratuitement",
    },
}


def _stub_response(prompt: str) -> str:
    """Return a deterministic response based on the prompt."""
    lower = prompt.lower()
    # Marketing copy generation
    if "marketing copy" in lower or "headline" in lower:
        return (
            "Introducing our latest innovation – a product that seamlessly blends "
            "cutting‑edge technology with everyday usability. Unlock new "
            "possibilities today!"
        )
    # Translation request
    if "translate" in lower and "to" in lower:
        # naive parse: assume format "Translate this ... to {lang}: {text}"
        try:
            target_lang = lower.split("to")[-1].split()[0][:2]
            # extract original text after the colon
            original = prompt.split(":", 1)[-1].strip()
            return _TRANSLATIONS.get(target_lang, {}).get(
                original, f"[{target_lang}] {original}"
            )
        except Exception:
            return f"[translation error] {prompt}"
    # Story outline generation
    if "story outline" in lower:
        topics = [
            "An unexpected journey leads to self‑discovery.",
            "A mysterious artifact sparks an intergalactic adventure.",
            "A detective unravels secrets in a future metropolis.",
        ]
        return random.choice(topics)
    # Fallback response
    return "OK"


def call_model(messages: List[Dict[str, str]]) -> Tuple[str, Dict[str, int]]:
    """Call an LLM or stub with a list of message dicts and return its reply.

    Each message must have `role` and `content` keys.  The last message in
    the list is assumed to contain the user's prompt.  The returned
    dictionary in the second element contains mock token usage counts.
    """
    use_openai = os.getenv("USE_OPENAI", "false").lower() == "true"
    if use_openai:
        # Attempt to call OpenAI's chat API
        try:
            import openai  # type: ignore

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "OPENAI_API_KEY must be set in the environment when USE_OPENAI=true"
                )
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": m.get("role", "user"), "content": m["content"]}
                    for m in messages
                ],
                temperature=0.2,
            )
            reply = response.choices[0].message.content
            usage = {
                "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                "completion_tokens": getattr(response.usage, "completion_tokens", 0),
            }
            return reply, usage
        except Exception as e:
            # Fallback to stub on any error
            stub_reply = _stub_response(messages[-1]["content"])
            return stub_reply, {"prompt_tokens": 0, "completion_tokens": 0}
    else:
        reply = _stub_response(messages[-1]["content"])
        # Simulate token usage
        tokens = max(1, len(reply.split()) // 5)
        return reply, {"prompt_tokens": tokens, "completion_tokens": tokens}