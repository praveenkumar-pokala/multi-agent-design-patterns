"""
Simple memory helpers for conversational agents.

The `SlidingWindowMemory` keeps the most recent messages in a buffer of
fixed size.  It is useful for providing a short-term context to a model
without exceeding token limits.  The `EntityMemory` collects capitalised
tokens and can be used to recall proper nouns and other important entities
across turns.
"""

from __future__ import annotations

from collections import deque
import re
from typing import Deque, List


class SlidingWindowMemory:
    """A memory that stores the most recent items up to a fixed length."""

    def __init__(self, max_length: int = 5):
        if max_length <= 0:
            raise ValueError("max_length must be positive")
        self.buffer: Deque[str] = deque(maxlen=max_length)

    def add(self, text: str) -> None:
        """Add a new piece of text to the memory."""
        self.buffer.append(text)

    def context(self) -> str:
        """Return the concatenated contents of the memory."""
        return "\n".join(self.buffer)


class EntityMemory:
    """Collect and recall capitalised tokens (simple entity extractor)."""

    def __init__(self) -> None:
        self.entities: set[str] = set()

    def ingest(self, text: str) -> None:
        """Extract capitalised words and add them to the entity set."""
        for match in re.finditer(r"\b([A-Z][a-zA-Z0-9]{2,})\b", text):
            self.entities.add(match.group(1))

    def context(self) -> str:
        """Return a summary string listing all known entities."""
        if not self.entities:
            return ""
        return "Known entities: " + ", ".join(sorted(self.entities))