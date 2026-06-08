"""
Unit tests for the orchestrator and components.
"""

import asyncio
import pytest

from dagonlayer.config import WorkflowConfig
from dagonlayer.agents import PydanticAIRegistry
from dagonlayer.orchestrator import DistributedHybridOrchestrator
from dagonlayer.observability import WorkflowObserver


@pytest.fixture
def mock_agents():
    """Fixture: Mock agents for testing."""
    return PydanticAIRegistry(model="mock://")


@pytest.fixture
def mock_observer():
    """Fixture: Observer with logging disabled."""
    return WorkflowObserver(enable_logging=False, enable_tracing=True)


@pytest.fixture
def mock_config(tmp_path):
    """Fixture: Minimal workflow configuration."""
    config_content = """
states:
  TASK_CREATED:
    agent: researcher_agent
    next_event: RESEARCH_COMPLETE
    context_mapping:
      topic: topic
    max_retries: 2
  
  RESEARCH_COMPLETE:
    agent: writer_agent
    next_event: WRITING_COMPLETE
    context_mapping:
      key_findings: findings
"""
    config_file = tmp_path / "workflow.yml"
    config_file.write_text(config_content)
    return WorkflowConfig(str(config_file))


@pytest.mark.asyncio
async def test_workflow_happy_path(mock_config, mock_agents, mock_observer):
    """Test happy path: successful workflow execution."""
    orchestrator = DistributedHybridOrchestrator(
        mock_config, 
        mock_agents, 
        mock_observer
    )
    
    result = await orchestrator.execute_workflow("WF-TEST", "Test Topic")
    
    assert result is not None
    assert "summary_draft" in result


@pytest.mark.asyncio
async def test_trace_events_recorded(mock_config, mock_agents, mock_observer):
    """Test that trace events are recorded."""
    orchestrator = DistributedHybridOrchestrator(
        mock_config, 
        mock_agents, 
        mock_observer
    )
    
    await orchestrator.execute_workflow("WF-TEST", "Test Topic")
    
    trace_events = mock_observer.get_trace_events()
    assert len(trace_events) > 0
    assert any("state:" in event["operation"] for event in trace_events)


@pytest.mark.asyncio
async def test_context_isolation(mock_agents):
    """Test that context mapping isolates agent access."""
    mapping = {
        "key_findings": "findings",
        "confidence_score": "score"
    }
    
    payload = {
        "key_findings": ["A", "B"],
        "confidence_score": 0.9,
        "secret_data": "should_not_be_accessible"
    }
    
    orchestrator = DistributedHybridOrchestrator(
        WorkflowConfig(),
        mock_agents,
        WorkflowObserver(enable_logging=False)
    )
    
    context = orchestrator._extract_context(payload, mapping)
    
    assert context["findings"] == ["A", "B"]
    assert context["score"] == 0.9
    assert "secret_data" not in context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
