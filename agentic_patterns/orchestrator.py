"""
Orchestrator pattern for breaking down and executing project tasks.

This module provides a simple `Orchestrator` class that analyses a project
description, breaks it down into discrete tasks and dispatches them to
specialised worker functions.  The goal is to show how an agent can act
as a coordinator for multiple sub‑agents, each with their own speciality.

The analysis is intentionally simplistic: bullet points containing the word
"UI" or "frontend" are assigned to the `frontend` worker, those containing
"API" or "backend" go to the `backend` worker, and everything else is
delegated to a generic `analysis` worker.  You can extend this logic
according to your own needs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from utils.tracing import Tracer


@dataclass
class Task:
    task_id: str
    description: str
    type: str
    dependencies: List[str] = field(default_factory=list)


@dataclass
class TaskResult:
    task_id: str
    success: bool
    output: str
    error: Optional[str] = None


@dataclass
class OrchestratorResult:
    all_tasks_completed: bool
    results: List[TaskResult]
    summary: str


class Orchestrator:
    """Break down a project into tasks and execute them via worker functions."""

    def __init__(self) -> None:
        # Map task type to worker function
        self.workers = {
            "backend": self.backend_worker,
            "frontend": self.frontend_worker,
            "analysis": self.analysis_worker,
        }

    def analyse_project(self, description: str) -> List[Task]:
        """Analyse the project description and return a list of tasks."""
        tasks: List[Task] = []
        lines = [line.strip() for line in description.split("\n") if line.strip()]
        for idx, line in enumerate(lines, start=1):
            # Determine type based on keywords
            if any(keyword in line.lower() for keyword in ["ui", "frontend"]):
                task_type = "frontend"
            elif any(keyword in line.lower() for keyword in ["api", "backend"]):
                task_type = "backend"
            else:
                task_type = "analysis"
            task = Task(
                task_id=f"task_{idx}",
                description=line,
                type=task_type,
                dependencies=[],
            )
            tasks.append(task)
        return tasks

    def backend_worker(self, task: Task) -> TaskResult:
        """Execute a backend task (mock implementation)."""
        output = f"Implemented API changes for: {task.description}"
        return TaskResult(task_id=task.task_id, success=True, output=output)

    def frontend_worker(self, task: Task) -> TaskResult:
        """Execute a frontend task (mock implementation)."""
        output = f"Updated UI components for: {task.description}"
        return TaskResult(task_id=task.task_id, success=True, output=output)

    def analysis_worker(self, task: Task) -> TaskResult:
        """Execute an analysis task (mock implementation)."""
        output = f"Analysed requirement: {task.description}"
        return TaskResult(task_id=task.task_id, success=True, output=output)

    def execute_tasks(self, tasks: List[Task]) -> List[TaskResult]:
        """Execute tasks sequentially in the order provided."""
        results: List[TaskResult] = []
        for task in tasks:
            worker = self.workers.get(task.type, self.analysis_worker)
            try:
                result = worker(task)
            except Exception as e:
                result = TaskResult(
                    task_id=task.task_id,
                    success=False,
                    output="",
                    error=str(e),
                )
            results.append(result)
        return results

    def synthesise_results(self, results: List[TaskResult]) -> str:
        """Create a summary string from the list of task results."""
        lines = []
        for res in results:
            status = "succeeded" if res.success else "failed"
            lines.append(f"{res.task_id} ({status}): {res.output or res.error}")
        return "\n".join(lines)

    def run(self, project_description: str) -> OrchestratorResult:
        """Analyse, execute and summarise a project plan."""
        tracer = Tracer()
        tracer.log(role="user", sender="client", content=project_description)
        tasks = self.analyse_project(project_description)
        tracer.log(role="agent", sender="orchestrator", content=f"Created {len(tasks)} tasks")
        results = self.execute_tasks(tasks)
        for res in results:
            tracer.log(
                role="agent",
                sender="worker",
                content=f"Task {res.task_id}: {res.output or res.error}"
            )
        summary = self.synthesise_results(results)
        tracer.log(role="agent", sender="orchestrator", content=f"Summary:\n{summary}")
        trace_path = tracer.finalize()
        return OrchestratorResult(
            all_tasks_completed=all(res.success for res in results),
            results=results,
            summary=summary + f"\nTrace saved to {trace_path}",
        )