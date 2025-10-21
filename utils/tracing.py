"""
Lightweight tracing for agent interactions.

The `Tracer` class records a sequence of messages or events and writes
them to a JSONL file.  Each trace is stored under `traces/{task_id}.jsonl`.
This makes it easy to debug workflows or replay conversations later.

Example usage:

>>> tracer = Tracer(task_id="example")
>>> tracer.log(role="agent", sender="Generator", content="Hello")
>>> tracer.finalize()
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


class Tracer:
    """Record events in a workflow and persist them as JSON lines."""

    def __init__(self, task_id: Optional[str] = None) -> None:
        self.task_id = task_id or uuid.uuid4().hex
        self.events: List[Dict[str, Any]] = []
        # Determine traces directory relative to project root
        self.trace_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "traces"
        )
        os.makedirs(self.trace_dir, exist_ok=True)

    def log(
        self,
        *,
        role: str,
        sender: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append an event to the current trace."""
        self.events.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "role": role,
                "sender": sender,
                "content": content,
                **(metadata or {}),
            }
        )

    def finalize(self) -> str:
        """Persist the trace to disk and return the path to the file."""
        path = os.path.join(self.trace_dir, f"{self.task_id}.jsonl")
        with open(path, "a", encoding="utf-8") as f:
            for event in self.events:
                f.write(json.dumps(event) + "\n")
        # Reset events to prevent duplicate writes
        self.events = []
        return path