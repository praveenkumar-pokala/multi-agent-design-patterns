"""
Judge loop pattern.

This module implements a simple iterative improvement loop.  A generator
creates a story outline based on a topic, and an evaluator judges the
outline, providing feedback if it is not good enough.  The generator
incorporates the feedback on subsequent iterations until the evaluator
returns a pass.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Tuple, Dict

from utils.tracing import Tracer
from utils.model_provider import call_model


@dataclass
class EvaluationFeedback:
    feedback: str
    score: str  # either "pass" or "needs_improvement"


class JudgeLoop:
    """Generate and iteratively improve a story outline until it passes."""

    def __init__(self, max_iterations: int = 5) -> None:
        self.max_iterations = max_iterations

    async def generate_outline(self, topic: str, feedback: str = "") -> str:
        """Generate a story outline using the model provider."""
        if feedback:
            prompt = f"Write a very short story outline about {topic}. Improve based on feedback: {feedback}"
        else:
            prompt = f"Write a very short story outline about {topic}."
        reply, _ = call_model([
            {"role": "user", "content": prompt}
        ])
        return reply

    def evaluate(self, outline: str) -> EvaluationFeedback:
        """Judge the outline and return feedback.  Simple heuristics."""
        # If the outline contains certain keywords or is sufficiently long, pass
        if len(outline.split()) > 8 and any(word in outline.lower() for word in ["unexpected", "mysterious", "detective"]):
            return EvaluationFeedback(feedback="", score="pass")
        # Otherwise provide feedback
        suggestions = [
            "Add an element of mystery",
            "Introduce a twist to keep the reader engaged",
            "Describe the protagonist more vividly",
        ]
        feedback = suggestions[0]
        return EvaluationFeedback(feedback=feedback, score="needs_improvement")

    async def run(self, topic: str) -> Dict[str, any]:
        """Iteratively improve a story outline until it passes or limit reached."""
        tracer = Tracer()
        tracer.log(role="user", sender="client", content=topic)
        feedback = ""
        outline = ""
        for iteration in range(1, self.max_iterations + 1):
            outline = await self.generate_outline(topic, feedback)
            tracer.log(role="agent", sender="generator", content=f"Iteration {iteration}: {outline}")
            evaluation = self.evaluate(outline)
            tracer.log(role="agent", sender="evaluator", content=f"Evaluation: {evaluation.score} - {evaluation.feedback}")
            if evaluation.score == "pass":
                tracer.log(role="agent", sender="loop", content=f"Outline approved on iteration {iteration}")
                break
            feedback = evaluation.feedback
        trace_path = tracer.finalize()
        return {
            "outline": outline,
            "passed": evaluation.score == "pass",
            "iterations": iteration,
            "feedback": feedback,
            "trace_file": trace_path,
        }