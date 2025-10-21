"""
Command‑line entry point for running agentic patterns.

Use this script to experiment with the patterns defined in the
`agentic_patterns` package.  Depending on the pattern you choose,
different arguments are required.  Run with `--help` to see all options.
"""

from __future__ import annotations

import argparse
import asyncio
from typing import Any

try:
    from rich import print as rprint  # type: ignore
    from rich.console import Console  # type: ignore
    from rich.table import Table  # type: ignore
except ImportError:  # Fallback definitions if rich is not installed
    # Define simple stand‑ins for Console and Table so the CLI still runs.
    class Console:
        def print(self, *args: Any, **kwargs: Any) -> None:  # type: ignore
            print(*args)

    class Table:
        def __init__(self, title: str | None = None) -> None:  # type: ignore
            self.title = title
            self.rows: list[tuple[str, str]] = []

        def add_column(self, *args: Any, **kwargs: Any) -> None:  # type: ignore
            pass

        def add_row(self, *cells: str) -> None:  # type: ignore
            self.rows.append(cells)

        def __iter__(self):  # type: ignore
            return iter(self.rows)

        def __str__(self) -> str:  # type: ignore
            lines = []
            if self.title:
                lines.append(self.title)
            for row in self.rows:
                lines.append(" | ".join(row))
            return "\n".join(lines)

    # Fallback rprint just uses the built‑in print
    def rprint(*args: Any, **kwargs: Any) -> None:  # type: ignore
        print(*args)

    console = Console()
else:
    console = Console()

from agentic_patterns import (
    SequentialChain,
    Router,
    ParallelTranslation,
    Orchestrator,
    JudgeLoop,
)

console = Console()


def run_sequential(args: argparse.Namespace) -> None:
    chain = SequentialChain()
    result = asyncio.run(
        chain.run(product_description=args.input, target_language=args.target_language)
    )
    table = Table(title="Sequential Chain Result")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    table.add_row("Original Headline", result["original_copy"]["headline"])
    table.add_row("Original Body", result["original_copy"]["body"])
    table.add_row("Call to Action", result["original_copy"]["call_to_action"])
    table.add_row("Validation", result["validation"]["feedback"])
    if result["translated_copy"]:
        table.add_row("Translated Headline", result["translated_copy"]["translated_headline"])
        table.add_row("Translated Body", result["translated_copy"]["translated_body"])
        table.add_row(
            "Translated CTA", result["translated_copy"]["translated_call_to_action"]
        )
    table.add_row("Entities", result["entities"])
    table.add_row("Trace File", result["trace_file"])
    console.print(table)


def run_router(args: argparse.Namespace) -> None:
    router = Router()
    response = router.handle(args.input)
    console.print(f"[bold blue]Router response:[/bold blue] {response}")


def run_parallel(args: argparse.Namespace) -> None:
    parallel = ParallelTranslation(target_language=args.target_language)
    result = asyncio.run(parallel.run(args.input))
    table = Table(title="Parallel Translation Result")
    table.add_column("Attempt", style="cyan", no_wrap=True)
    table.add_column("Translation", style="green")
    for idx, translation in enumerate(result["translations"], start=1):
        table.add_row(str(idx), translation)
    table.add_row("Best", result["best"])
    console.print(table)


def run_orchestrator(args: argparse.Namespace) -> None:
    orchestrator = Orchestrator()
    result = orchestrator.run(args.project)
    table = Table(title="Orchestrator Result")
    table.add_column("Task", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Output", style="white")
    for res in result.results:
        status = "✅" if res.success else "❌"
        table.add_row(res.task_id, status, res.output or res.error or "")
    console.print(table)
    console.print(f"\nSummary:\n{result.summary}")


def run_judge(args: argparse.Namespace) -> None:
    loop = JudgeLoop()
    result = asyncio.run(loop.run(args.topic))
    table = Table(title="Judge Loop Result")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    table.add_row("Outline", result["outline"])
    table.add_row("Passed", str(result["passed"]))
    table.add_row("Iterations", str(result["iterations"]))
    table.add_row("Feedback", result["feedback"] or "None")
    table.add_row("Trace File", result["trace_file"])
    console.print(table)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run agentic design patterns.")
    subparsers = parser.add_subparsers(dest="pattern", required=True)

    # Sequential pattern
    seq_parser = subparsers.add_parser("sequential", help="Run the sequential marketing chain")
    seq_parser.add_argument("--input", required=True, help="Product description to generate copy from")
    seq_parser.add_argument(
        "--target_language",
        default="es",
        help="Two letter code of target language for translation (default 'es')",
    )
    seq_parser.set_defaults(func=run_sequential)

    # Router pattern
    router_parser = subparsers.add_parser("router", help="Route a message by language")
    router_parser.add_argument("--input", required=True, help="Text to route")
    router_parser.set_defaults(func=run_router)

    # Parallel translation pattern
    par_parser = subparsers.add_parser("parallel", help="Run parallel translations")
    par_parser.add_argument("--input", required=True, help="Text to translate")
    par_parser.add_argument(
        "--target_language",
        default="es",
        help="Target language for translation (default 'es')",
    )
    par_parser.set_defaults(func=run_parallel)

    # Orchestrator pattern
    orch_parser = subparsers.add_parser("orchestrator", help="Break down and execute a project plan")
    orch_parser.add_argument("--project", required=True, help="Project description with bullet points")
    orch_parser.set_defaults(func=run_orchestrator)

    # Judge loop pattern
    judge_parser = subparsers.add_parser("judge", help="Iteratively improve a story outline")
    judge_parser.add_argument("--topic", required=True, help="Topic for the story outline")
    judge_parser.set_defaults(func=run_judge)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()