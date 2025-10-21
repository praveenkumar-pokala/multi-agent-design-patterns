"""
Language routing pattern.

The `Router` class inspects incoming text, detects its language using the
`langdetect` library and dispatches the text to a handler for that
language.  If no handler exists for the detected language, a fallback
message is returned.  Handlers can be customised to perform translations,
answer questions or carry out other tasks.

Example:

>>> router = Router()
>>> router.handle("Hola, ¿cómo estás?")
'[es] Hola, ¿cómo estás?'  # stubbed translation
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

try:
    from langdetect import detect  # type: ignore
except ImportError:
    # Fallback detector: always return English when langdetect is unavailable.
    def detect(text: str) -> str:  # type: ignore
        return "en"

from utils.model_provider import call_model


class Router:
    """Detect the language of a message and route it to the appropriate handler."""

    def __init__(self) -> None:
        # Handlers keyed by ISO 639-1 language code.  Each handler receives the
        # original message and returns a response string.
        self.handlers: Dict[str, Callable[[str], str]] = {}

        # Register default handlers for English, Spanish and French.  These
        # demonstrate simple behaviour using the model provider stub.
        self.register_handler("en", self._handle_english)
        self.register_handler("es", self._handle_spanish)
        self.register_handler("fr", self._handle_french)

    def register_handler(self, lang_code: str, handler: Callable[[str], str]) -> None:
        """Register a custom handler for a language code."""
        self.handlers[lang_code] = handler

    def _handle_english(self, text: str) -> str:
        return f"[en] {text}"

    def _handle_spanish(self, text: str) -> str:
        # Use the model provider to translate to English as a simple demo
        prompt = f"Translate this to English: {text}"
        reply, _ = call_model([
            {"role": "user", "content": prompt}
        ])
        return f"[es] {reply}"

    def _handle_french(self, text: str) -> str:
        prompt = f"Translate this to English: {text}"
        reply, _ = call_model([
            {"role": "user", "content": prompt}
        ])
        return f"[fr] {reply}"

    def handle(self, message: str) -> str:
        """Detect the language of the message and invoke the matching handler."""
        try:
            lang = detect(message)
        except Exception:
            lang = "unknown"
        handler = self.handlers.get(lang)
        if handler:
            return handler(message)
        return f"[unknown] {message}"