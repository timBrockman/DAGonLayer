# Modular Refactor: Pydantic AI Integration (Option 3)

This branch implements a fully modular, production-ready version of stateguard with **Pydantic AI integration** while maintaining ownership of orchestration logic.

## Architecture Overview

```
main.py (entry point)
    ↓
orchestrator.py (state machine engine)
    ├→ config.py (workflow definitions)
    ├→ agents.py (agent registry)
    ├→ schemas.py (pydantic validation)
    ├→ provenance.py (event audit trail)
    └→ observability.py (telemetry)
```

## Files

| File | Purpose |
|------|---------|
| **schemas.py** | Pydantic models & SCHEMA_REGISTRY |
| **agents.py** | Agent definitions (Pydantic AI integration point) |
| **provenance.py** | Immutable event graph for audit trail |
| **config.py** | YAML workflow configuration loading |
| **observability.py** | Logging and telemetry (pluggable) |
| **orchestrator.py** | Core state machine engine |
| **main.py** | Entry point and component initialization |
| **test_orchestrator.py** | Unit tests |
| **requirements.txt** | Dependencies |

## Design Principles

### 1. **Single Responsibility**
Each module has one purpose:
- `schemas.py` → Define contracts
- `agents.py` → Invoke LLMs/agents
- `orchestrator.py` → Orchestrate workflow
- `observability.py` → Monitor execution

### 2. **Dependency Injection**
Components are passed to `DistributedHybridOrchestrator`:

```python
orchestrator = DistributedHybridOrchestrator(config, agents, observer)
```

This makes testing easy and allows swapping implementations.

### 3. **Context Isolation**
Agents only receive the data they explicitly need:

```python
# Workflow state
{"topic": "...", "secret_key": "xxx", "api_token": "yyy"}

# Agent receives only
{"topic": "..."} # via context_mapping
```

### 4. **Pydantic AI Integration Point**
In `agents.py`, swap this line to use real LLMs:

```python
# Current (mock)
return {"key_findings": [...], "confidence_score": 0.95}

# With Pydantic AI
result = await self.researcher.run(f"Research topic: {topic}")
return result.model_dump()
```

### 5. **Observability First**
Tracing, logging, and metrics are built-in, not bolted on:

```python
with self.observer.trace_span(workflow_id, "operation_name"):
    # Operation automatically timed and logged
```

## Usage

### Basic Execution

```python
python main.py
```

### With Custom Config

```python
from config import WorkflowConfig
from agents import PydanticAIRegistry
from orchestrator import DistributedHybridOrchestrator

config = WorkflowConfig("my_workflow.yml")
agents = PydanticAIRegistry(model="anthropic:claude-3")
orchestrator = DistributedHybridOrchestrator(config, agents, observer)

result = await orchestrator.execute_workflow("WF-001", "My Topic")
```

### Testing

```bash
pip install pytest pytest-asyncio
pytest test_orchestrator.py -v
```

## Integration with Pydantic AI

### Current State (Mock)
Agents return dict → Validated against Pydantic schema

### Production (with Pydantic AI)

In `agents.py`, replace:

```python
def _init_agents(self):
    from pydantic_ai import Agent
    
    self.researcher = Agent(
        model=self.model,
        result_type=ResearcherOutputSchema,
        system_prompt="You are a research analyst..."
    )

async def researcher_agent(self, topic: str, workflow_id: str, **kwargs):
    result = await self.researcher.run(f"Research: {topic}")
    return result.model_dump()  # Already validated by Pydantic AI
```

That's it. No changes needed to orchestrator, schemas, or tests.

## Upgrade Path

### Phase 1: Mock Testing (Current)
- All agents are mock implementations
- Test workflow logic without LLM costs

### Phase 2: Real LLMs
```python
agents = PydanticAIRegistry(model="openai:gpt-4")  # Swap model
```

### Phase 3: Observability
```python
observer = WorkflowObserver(enable_logging=True, enable_tracing=True)
# Connect trace_events to LangSmith, DataDog, etc.
```

### Phase 4: Scale (if needed)
```python
# If you outgrow this, migrate to LangGraph without rewriting orchestrator
# The agent interface remains the same
```

## Key Differences from Original

| Aspect | Original | Refactored |
|--------|----------|-----------|
| **File Organization** | Single 200-line file | 8 modular files (50-150 lines each) |
| **Testability** | Hard to test components | Each component testable independently |
| **Agent Integration** | Mock only | Ready for Pydantic AI |
| **Observability** | None | Built-in logging + tracing |
| **Context Isolation** | Implicit | Explicit via context_mapping |
| **Configuration** | Inline | External YAML + typed loader |
| **Error Handling** | Basic | Comprehensive with recovery |

## Example: Adding a New Agent

### 1. Define Schema (schemas.py)
```python
class ResummarizerSchema(BaseModel):
    summary: str = Field(..., min_length=20)
```

### 2. Register in SCHEMA_REGISTRY
```python
SCHEMA_REGISTRY = {
    ...,
    "SUMMARIZED": ResummarizerSchema
}
```

### 3. Implement Agent (agents.py)
```python
async def resummary_agent(self, content: str, workflow_id: str):
    result = await self.summarizer.run(f"Summarize: {content}")
    return result.model_dump()
```

### 4. Add to Workflow (workflow.yml)
```yaml
WRITING_COMPLETE:
  agent: resummary_agent
  next_event: SUMMARIZED
  context_mapping:
    summary_draft: content
```

### 5. Test It
```python
@pytest.mark.asyncio
async def test_new_agent():
    orchestrator = ...
    result = await orchestrator.execute_workflow("WF-NEW", "topic")
    assert "summary" in result
```

## Contributing

When extending this codebase:

1. **Keep modules focused** — if a file grows > 200 lines, consider splitting
2. **Use type hints** — all functions should be fully typed
3. **Add docstrings** — document public APIs
4. **Write tests** — add tests in `test_orchestrator.py`
5. **No cross-imports** — avoid circular dependencies

## Next Steps

1. Replace mock agents with real Pydantic AI calls
2. Add environment configuration (API keys, model selection)
3. Connect observability to production telemetry system
4. Consider async database integration for provenance storage
5. Add human intervention queue implementation

## Resources

- [Pydantic AI Docs](https://ai.pydantic.dev/)
- [AsyncIO Guide](https://docs.python.org/3/library/asyncio.html)
- [Pydantic Validation](https://docs.pydantic.dev/)
