"""
Parallel translation pattern.

This module defines a `ParallelTranslation` class that can run multiple
translation attempts concurrently and then pick a best translation from
among the results.  It demonstrates how to use `asyncio.gather` to run
calls in parallel and how to perform a simple selection over the outputs.
"""

from __future__ import annotations

import asyncio
from collections import Counter
from typing import List, Dict, Tuple

from utils.model_provider import call_model


class ParallelTranslation:
    """Translate a message multiple times in parallel and pick the best."""

    def __init__(self, target_language: str = "es") -> None:
        self.target_language = target_language

    async def translate_once(self, message: str) -> str:
        """Run a single translation attempt using the model provider."""
        prompt = f"Translate this to {self.target_language}: {message}"
        reply, _ = call_model([
            {"role": "user", "content": prompt}
        ])
        return reply

    async def run(self, message: str) -> Dict[str, any]:
        """Execute three parallel translations and pick the best one."""
        # Launch three translation tasks concurrently
        results: Tuple[str, str, str] = await asyncio.gather(
            self.translate_once(message),
            self.translate_once(message),
            self.translate_once(message),
        )
        translations: List[str] = list(results)

        # Select the most common translation (simple voting).  If tie, pick first.
        counter = Counter(translations)
        best_translation = counter.most_common(1)[0][0]

        return {
            "input": message,
            "translations": translations,
            "best": best_translation,
        }