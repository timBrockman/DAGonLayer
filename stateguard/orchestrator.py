"""
Core asynchronous orchestration engine.
Decoupled from schemas, agents, config, and observability.
"""

from typing import Dict, Any
from pydantic import ValidationError

from .config import WorkflowConfig
from .agents import PydanticAIRegistry
from .provenance import AsyncProvenanceGraph
from .schemas import SCHEMA_REGISTRY
from .observability import WorkflowObserver


class DistributedHybridOrchestrator:
    """
    Core async workflow orchestration engine.
    
    Orchestrates multi-agent workflows with:
    - Declarative YAML-based state machine configuration
    - Strict Pydantic schema validation at state boundaries
    - Automatic retry logic and error recovery
    - Human intervention escalation paths
    - Complete event provenance tracking
    """
    
    def __init__(
        self,
        config: WorkflowConfig,
        agent_registry: PydanticAIRegistry,
        observer: WorkflowObserver
    ):
        """
        Initialize the orchestrator.
        
        Args:
            config: Workflow configuration loader
            agent_registry: Registry of agents to invoke
            observer: Observability and telemetry handler
        """
        self.config = config
        self.agent_registry = agent_registry
        self.observer = observer
    
    def _extract_context(
        self, 
        payload: Dict[str, Any], 
        mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Extract context from payload based on mapping.
        
        Implements context isolation: agents only receive the fields
        they explicitly need from the workflow state.
        
        Args:
            payload: Current workflow state payload
            mapping: Mapping of {payload_key: agent_arg_name}
        
        Returns:
            Extracted context dict ready for agent invocation
        """
        return {
            agent_arg: payload[graph_key]
            for graph_key, agent_arg in mapping.items()
            if graph_key in payload
        }
    
    async def execute_workflow(
        self, 
        workflow_id: str, 
        initial_topic: str
    ) -> Dict[str, Any]:
        """
        Execute a single workflow from start to finish.
        
        State machine loop that:
        1. Loads state rules from configuration
        2. Evaluates routing conditions
        3. Invokes appropriate agent
        4. Validates output against schema
        5. Handles retries and escalations
        
        Args:
            workflow_id: Unique identifier for this workflow run
            initial_topic: Initial topic/input for the workflow
        
        Returns:
            Final payload from the last state in the workflow
        """
        graph = AsyncProvenanceGraph()
        current_state = "TASK_CREATED"
        latest_payload = {"topic": initial_topic}
        
        await graph.append("SYSTEM", current_state, latest_payload)
        
        error_occurred, error_message, retry_count = False, "", 0
        
        while True:
            with self.observer.trace_span(workflow_id, f"state:{current_state}"):
                state_rules = self.config.get_state_rules(current_state)
                
                # Terminal state: no rules found
                if not state_rules:
                    if self.observer.logger:
                        self.observer.logger.info(
                            f"✅ [{workflow_id}] Pipeline terminated at: {current_state}"
                        )
                    break
                
                # === ROUTING RULES ===
                # Dynamic branching based on payload conditions
                if "routing_rules" in state_rules:
                    for rule in state_rules["routing_rules"]:
                        # Evaluate condition in payload context
                        if eval(rule["condition"], {}, latest_payload):
                            self.observer.log_state_transition(
                                workflow_id, current_state, rule["target_state"]
                            )
                            current_state = rule["target_state"]
                            break
                    continue
                
                # === AGENT INVOCATION ===
                agent_name = state_rules.get("agent")
                next_event_type = state_rules["next_event"]
                max_allowed_retries = state_rules.get("max_retries", 1)
                
                # No agent: terminal state
                if not agent_name:
                    break
                
                # Extract and prepare agent arguments
                # Context isolation: agents only see what they need
                agent_kwargs = self._extract_context(
                    latest_payload, 
                    state_rules["context_mapping"]
                )
                agent_kwargs["workflow_id"] = workflow_id
                
                # Pass error context if retrying
                if error_occurred:
                    agent_kwargs["_error_occurred"] = True
                    agent_kwargs["_error_message"] = error_message
                
                self.observer.log_agent_call(workflow_id, agent_name, agent_kwargs)
                
                # === AGENT EXECUTION ===
                agent_callable = getattr(self.agent_registry, agent_name)
                raw_output = await agent_callable(**agent_kwargs)
                
                # === OUTPUT VALIDATION ===
                schema = SCHEMA_REGISTRY.get(next_event_type)
                if schema:
                    try:
                        # Validate output matches schema
                        validated_model = schema(**raw_output)
                        clean_payload = validated_model.model_dump()
                        
                        # Reset error tracking on success
                        error_occurred, error_message, retry_count = False, "", 0
                        
                        # Append to provenance graph
                        await graph.append(
                            agent_name.upper(), 
                            next_event_type, 
                            clean_payload
                        )
                        
                        self.observer.log_state_transition(
                            workflow_id, current_state, next_event_type
                        )
                        
                        current_state = next_event_type
                        latest_payload = clean_payload
                        
                    except (ValidationError, TypeError, KeyError) as e:
                        retry_count += 1
                        self.observer.log_validation_error(
                            workflow_id, current_state, str(e)
                        )
                        
                        # Exhausted retries: escalate to human intervention
                        if retry_count >= max_allowed_retries:
                            if self.observer.logger:
                                self.observer.logger.warning(
                                    f"⚠️ [{workflow_id}] Max retries ({max_allowed_retries}) exhausted. Escalating."
                                )
                            error_occurred, error_message, retry_count = False, "", 0
                            current_state = "HUMAN_INTERVENTION"
                            continue
                        
                        # Prepare for retry
                        error_occurred = True
                        error_message = str(e)
                else:
                    # No schema validation required for this state
                    await graph.append(
                        agent_name.upper(), 
                        next_event_type, 
                        raw_output
                    )
                    
                    self.observer.log_state_transition(
                        workflow_id, current_state, next_event_type
                    )
                    
                    current_state = next_event_type
                    latest_payload = raw_output
        
        return graph.events[-1].payload if graph.events else {}
