# Stateguard | A Configuration-Driven, Deterministic, Multi-Agent Engine
## 📂 Lightweight Data-Driven Multi-Agent Orchestrator

A minimalist, high-performance, prototype Python framework for orchestrating specialized multi-agent workflows. By pairing a Strict Configuration-Driven Scheduler with an immutable Unified Provenance Graph, this architecture eliminates conversational prompt drift, slashes token overhead, and provides a reliable execution audit trail.

------------------------------
## 🚀 Key Framework Features

* 📜 Configuration-Driven Routing (YAML): No nested Python if/elif statements. Workflows, edge transitions, and states are defined completely in a declarative YAML file.
* 🛡️ Boundary Protection (Pydantic Guards): Every agent output is tightly validated against strict types before it hits the state layer. Malformed LLM outputs are caught and blocked at the runtime border.
* 🔄 Automated Self-Healing Loop: If an LLM breaks a Pydantic validation rule, the framework captures the structural error message and funnels it back to the agent with instructions to rewrite the response.
* 👥 First-Class Human Intervention (HITL): When agents exhaust their max retries, tasks gracefully route to human queues using identical context-mapping logic—preventing system crashes.
* 🔀 Conditional Expressions: Workflows branch dynamically based on payload evaluation metrics (e.g., checking score values or quality metrics).
* ⚡ Asynchronous Concurrency: Built from the ground up using asyncio to execute thousands of unique workflows in parallel without thread-locking or data cross-contamination.

------------------------------
## 🛠️ Complete Usage Guide
### 1. Define the Workflow Configuration (`workflow.yml`)
The current `workflow.yml` is the declarative state machine for the engine. It defines state transitions, `context_mapping`, `agent` bindings, retry caps, routing rules, and terminal states.

### 2. Run the Entry Point (`main.py`)
The refactor splits the runtime into focused modules and uses `main.py` as the bootstrapper.

```bash
pip install -r requirements.txt
python main.py
```

### 3. How the Engine Works
* `config.py` loads the workflow definition from YAML.
* `orchestrator.py` evaluates states, executes agents, validates outputs, and routes workflow transitions.
* `agents.py` contains the `PydanticAIRegistry` and mock agent implementations, with clear hooks for real Pydantic AI integration.
* `schemas.py` defines strict output contracts and exposes `SCHEMA_REGISTRY` for runtime validation.
* `provenance.py` captures an immutable audit trail for each workflow event.
* `observability.py` instruments execution with logging and trace spans.

## 📊 Architectural Trade-off Matrix
This grid reflects our engineering choices to maintain maximum isolation, token efficiency, and deterministic predictability versus mainstream multi-agent design alternatives.

| Architectural Vector | Choice Made in Framework | Core Strengths | Operational Cost / Vulnerabilities | Practical Alternatives |
|---|---|---|---|---|
| State Tracking Pattern | Immutable Unified Provenance Graph | • Absolute auditing records • Zero tracking state loss • Trivial local troubleshooting playback. | • Memory arrays expand infinitely unless compacted or dropped to disk database lakes. | Dynamic Chat Logs / Blackboard Systems: High operational token drift and easy vector history pollution. |
| Orchestration / Task Routing | Strict External YAML Scheduler | • 100% predictable workflows • Simple, human-readable pipelines • Zero router model overhead costs. | • Brittle when coping with unstructured or random, exploratory workflows. | Autonomous Router Prompts / Swarms: Agents dynamically decide who handles tasks using semantic similarity matches. |
| Agent Input Boundary Interface | Isolated Context Extractor Mapping | • Minimal token windows • Eliminates downstream data leakage or noise hallucinations. | • Tangential, unmapped findings discovered during execution are thrown away. | Shared Context Windows: Entire conversation log maps into every agent call, dramatically expanding context windows. |
| Boundary Protection Strategy | Strict Pydantic Schema Guards | • Fail-safe data pipelines • Automated regex, range, and type validation rules. | • Demands up-front data design models; system halts if unforeseen schemas appear. | Freeform Markdown Text Responses: High processing failure rates down the pipeline due to unparseable response formatting. |

------------------------------
## 🗺️ Future Roadmap Suggestions
### 📦 Phase 0: Package and Stabilize the Refactor
* Create a package entrypoint around `main.py` and expose the orchestrator as a reusable module.
* Add environment configuration for model selection, API keys, and runtime options.
* Verify the new file-level design with stronger tests and clear module contracts.

### 📈 Phase 1: Real Pydantic AI and Production Integration
* Replace mocked agent implementations in `agents.py` with real `pydantic_ai` agent instances.
* Add optional model configuration so the registry can target `openai:gpt-4`, `anthropic:claude-3`, or similar backends.
* Extend observability to export traces to a production telemetry backend.

### 🧠 Phase 2: Persistence and Human Workflow Support
* Add an async persistent store for provenance events so long-running workflows survive restarts.
* Build an actual human intervention queue and callback workflow for `HUMAN_INTERVENTION` state.
* Add webhook/event broker integration so manual review requests can be sent and resumed from external systems.

------------------------------
## 🤝 Advancing the Architecture
This project is a modular prototype built to move beyond a single-file proof of concept. The current refactor makes it easier to extend, validate, test, and eventually connect to real LLMs and production telemetry.
