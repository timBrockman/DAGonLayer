# Stateguard | A Configuration-Driven, Deterministic, Multi-Agent Engine
## 📂 Lightweight Data-Driven Multi-Agent Framework

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
### 1. Define the Workflow Configuration (workflow.yml)
The demo `workflow.yml` configuration models an advanced pipeline: it pulls context, enforces retry caps, handles data-driven branching criteria, and registers human intervention fallback loops.

### 2. Implement the Core Runtime Engine (stateguard.py)
Save the following code as stateguard.py. It reads the configuration file, maps context isolation, evaluates expressions, manages errors, and runs concurrently.
- [ ] todo - create actual package

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
### 📦 Phase 0: Create package
### 📈 Phase 1: High Availability & Persistence

* Distributed Persistent State Store (Redis/PostgreSQL): Swap out the in-memory array AsyncProvenanceGraph for an asynchronous DB driver interface. This allows long-running workflows to survive server restarts or crashes.
* Webhook Event Broker Subscriptions: Expose endpoints where human-in-the-loop task notifications publish directly to communication tools (e.g., Slack, email, or a frontend dashboard) and sleep until webhooks post back data payloads.

### 🧠 Phase 2: Dynamic Lifecycle Compaction

* Token Pruning Summarizer Workers: Implement a background cleanup routine that uses small, cost-efficient models to compress older historical events inside massive logs into atomic context sheets, maximizing prompt efficiency.
* Semantic Token Router Routing Fallback: Introduce vector searches on the central configuration scheduler so that if a workflow enters an unknown state, tasks map to matching agents based on prompt embeddings instead of rigid configuration rules.

------------------------------
## 🤝 Advancing the Architecture
This project is a super early prototype designed to get some ideas out and into code.
