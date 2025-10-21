"""
Sequential chain pattern for marketing copy generation, validation and
translation.

This module defines a `SequentialChain` class that guides a piece of text
through a series of steps: generating marketing copy from a product
description, validating the copy against simple heuristics, and optionally
translating the copy into a target language.  Each step logs its actions to
an instance of `Tracer` and updates a sliding window and entity memory for
contextual continuity.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional, Dict

from pydantic import BaseModel

from utils.memory import SlidingWindowMemory, EntityMemory
from utils.tracing import Tracer
from utils.model_provider import call_model


class MarketingCopy(BaseModel):
    """Data model for generated marketing copy."""
    headline: str
    body: str
    call_to_action: str


class ValidationResult(BaseModel):
    """Validation result for marketing copy."""
    is_valid: bool
    feedback: str


class TranslatedCopy(BaseModel):
    """Data model for the translated marketing copy."""
    original: MarketingCopy
    translated_headline: str
    translated_body: str
    translated_call_to_action: str


class SequentialChain:
    """Run a marketing workflow through generation, validation and translation."""

    def __init__(self, memory_size: int = 4) -> None:
        # Memory components track recent interactions and entities
        self.memory = SlidingWindowMemory(memory_size)
        self.entities = EntityMemory()

    async def run(self, *, product_description: str, target_language: str = "es") -> Dict[str, any]:
        """Execute the sequential chain.

        Parameters
        ----------
        product_description: str
            Description of the product to use when generating marketing copy.
        target_language: str
            Two‑letter code of the target language for translation (default 'es').

        Returns
        -------
        dict
            A dictionary containing the original and translated copy along with
            validation feedback.
        """
        tracer = Tracer()

        # Step 1: Generate marketing copy
        generation_prompt = (
            f"Create a catchy marketing headline, body and call to action for: {product_description}"
        )
        tracer.log(role="user", sender="client", content=generation_prompt)
        response, usage = call_model([
            {"role": "user", "content": generation_prompt}
        ])
        # For simplicity the stub returns a generic marketing message.  Split into parts.
        headline = response.split(".")[0].strip()
        body = response
        call_to_action = "Learn more"
        marketing_copy = MarketingCopy(
            headline=headline,
            body=body,
            call_to_action=call_to_action,
        )
        tracer.log(
            role="agent",
            sender="generator",
            content=f"Generated copy: {marketing_copy.dict()}"
        )
        self.memory.add(marketing_copy.body)
        self.entities.ingest(marketing_copy.headline)

        # Step 2: Validate marketing copy
        feedback_messages = []
        is_valid = True
        if len(marketing_copy.headline) > 60:
            feedback_messages.append("Headline is too long (max 60 characters).")
            is_valid = False
        if len(marketing_copy.body) < 100:
            feedback_messages.append("Body is too short (min 100 characters).")
            is_valid = False
        if not any(
            phrase in marketing_copy.call_to_action.lower()
            for phrase in ["buy", "learn", "try", "get", "start"]
        ):
            feedback_messages.append(
                "Call to action should include an action word like buy, learn or try."
            )
            is_valid = False
        validation_result = ValidationResult(
            is_valid=is_valid,
            feedback="\n".join(feedback_messages) if feedback_messages else "All checks passed!",
        )
        tracer.log(
            role="agent",
            sender="validator",
            content=f"Validation result: {validation_result.dict()}"
        )
        self.memory.add(validation_result.feedback)

        # Step 3: Translate marketing copy if valid
        translated_copy: Optional[TranslatedCopy] = None
        if validation_result.is_valid:
            # Translate each part individually using the model provider
            def translate_text(text: str) -> str:
                prompt = f"Translate this marketing phrase to {target_language}: {text}"
                reply, _ = call_model([
                    {"role": "user", "content": prompt}
                ])
                return reply

            translated_headline = translate_text(marketing_copy.headline)
            translated_body = translate_text(marketing_copy.body)
            translated_cta = translate_text(marketing_copy.call_to_action)
            translated_copy = TranslatedCopy(
                original=marketing_copy,
                translated_headline=translated_headline,
                translated_body=translated_body,
                translated_call_to_action=translated_cta,
            )
            tracer.log(
                role="agent",
                sender="translator",
                content=f"Translated copy: {translated_copy.dict()}"
            )
            self.memory.add(translated_body)
            self.entities.ingest(translated_headline)

        # Finalise trace and return
        trace_path = tracer.finalize()
        result: Dict[str, any] = {
            "original_copy": marketing_copy.dict(),
            "validation": validation_result.dict(),
            "translated_copy": translated_copy.dict() if translated_copy else None,
            "entities": self.entities.context(),
            "trace_file": trace_path,
        }
        return result