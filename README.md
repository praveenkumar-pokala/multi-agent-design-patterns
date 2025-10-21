# Agentic Patterns Playground

This repository demonstrates a set of **agentic AI design patterns** built in a
modular and extensible way. 

## Features

* **Modular architecture:** All patterns live under the `agentic_patterns` package
  and share common helpers in the `utils` package.  Each pattern can be used
  independently or composed with others.
* **Sequential chains:** Demonstrates a marketing workflow that generates
  marketing copy, validates it against simple heuristics, and optionally
  translates it to another language.  The pattern uses a sliding window
  memory and produces a JSON trace of each step.
* **Language router:** Detects the language of an incoming message and
  dispatches it to a specialised handler.  Handlers can be extended to
  implement translations, summaries or other tasks.
* **Parallel execution:** Runs multiple translation attempts concurrently and
  selects the best result using a simple voting mechanism.  Useful when
  combining the outputs of several agents.
* **Orchestrator pattern:** Breaks down a project description into discrete
  tasks and dispatches them to worker functions.  This pattern sketches how
  to coordinate complex jobs across specialised agents.
* **Judge loop:** Illustrates an iterative improvement loop where one agent
  generates content and another agent critiques it until a pass condition is
  met.
* **Utility helpers:** Includes environment loading, a simple sliding window
  memory, a tracer for JSONL logging, and a pluggable model provider that can
  be swapped out for your preferred LLM.
* **CLI runner:** Use `python runner.py` to run any of the patterns from the
  command line without having to write your own scripts.

## Quick start

1. **Clone** this repository and change into the project directory:

   ```bash
   git clone <your-fork-url>
   cd agentic_patterns_new
   ```

2. **Create a virtual environment** (optional but recommended) and install
   dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set environment variables** (optional).  If you plan to call an actual
   large language model you can supply an API key via the `.env` file.  Copy
   `.env.example` to `.env` and fill in the values:

   ```bash
   cp .env.example .env
   # then edit .env with your API keys
   ```

4. **Run a pattern** using the CLI.  For example, to run the sequential
   marketing chain:

   ```bash
   python runner.py --pattern sequential --input "Describe an innovative AI product" --target_language es
   ```

   To route a message by language:

   ```bash
   python runner.py --pattern router --input "Bonjour tout le monde"
   ```

   To run the parallel translation demo:

   ```bash
   python runner.py --pattern parallel --input "Hello, world!"
   ```

   To execute a simple project plan with the orchestrator:

   ```bash
   python runner.py --pattern orchestrator --project "Add user authentication and update the UI"
   ```

   To iterate on a story outline until it passes evaluation:

   ```bash
   python runner.py --pattern judge --topic "A futuristic detective story"
   ```

Each command will print the result to the console and save a JSON trace of the
interaction in the `traces/` directory.

## Folder structure

```
agentic_patterns_new/
├── agentic_patterns/      # Pattern implementations
│   ├── __init__.py
│   ├── sequential_chain.py
│   ├── router.py
│   ├── parallel.py
│   ├── orchestrator.py
│   └── judge_loop.py
├── utils/                 # Shared helpers
│   ├── __init__.py
│   ├── env_loader.py
│   ├── memory.py
│   ├── tracing.py
│   └── model_provider.py
├── traces/                # Generated JSONL traces (gitignored)
├── runner.py              # Command‑line interface to run patterns
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

We hope this improved structure provides a solid foundation for exploring
agentic design patterns.  Feel free to extend the modules, add new patterns or
integrate your own large language model via the `utils.model_provider` hook.
