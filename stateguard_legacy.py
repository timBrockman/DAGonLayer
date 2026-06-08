import asyncio
import json
import yaml
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel, Field, ValidationError

# ==========================================
# PYDANTIC GUARDS (Strict Schemas)
# ==========================================
class ResearcherOutputSchema(BaseModel):
    key_findings: List[str] = Field(..., description="Vetted structured research findings.")
    confidence_score: float = Field(..., ge=0.0, le=1.0)

class HumanOverrideSchema(BaseModel):
    key_findings: List[str]
    confidence_score: float = 1.0

class WriterOutputSchema(BaseModel):
    summary_draft: str = Field(..., min_length=10)

SCHEMA_REGISTRY = {
    "RESEARCH_COMPLETE": ResearcherOutputSchema,
    "READY_FOR_WRITING": HumanOverrideSchema,
    "WRITING_COMPLETE": WriterOutputSchema
}

# ==========================================
# IMMUTABLE PROVENANCE GRAPH
# ==========================================
@dataclass
class Event:
    event_id: int
    timestamp: str
    sender: str
    event_type: str
    payload: Dict[str, Any]

class AsyncProvenanceGraph:
    def __init__(self):
        self.events: List[Event] = []
        self._counter = 0

    async def append(self, sender: str, event_type: str, payload: Dict[str, Any]) -> Event:
        self._counter += 1
        event = Event(self._counter, datetime.utcnow().isoformat(), sender, event_type, payload)
        self.events.append(event)
        return event

# ==========================================
# CONTEXT-ISOLATED AGENTS (AI & Human)
# ==========================================
class AsyncAgentsRegistry:
    def __init__(self):
        self.attempts = {}

    async def researcher_agent(self, topic: str, workflow_id: str, _error_occurred: bool = False, _error_message: str = "") -> Dict[str, Any]:
        self.attempts[workflow_id] = self.attempts.get(workflow_id, 0) + 1
        print(f"📡 [{workflow_id}] 🤖 [Researcher] Executing attempt #{self.attempts[workflow_id]}...")
        await asyncio.sleep(0.5)

        # Force a recovery loop check on Workflow 102
        if workflow_id == "WF-102" and self.attempts[workflow_id] == 1:
            print(f"📡 [{workflow_id}] ❌ [Researcher] Intentionally outputting broken schema...")
            return {"bad_response": "broken structural payload"}

        # Force a Human Escalation branch check on Workflow 103
        score = 0.45 if workflow_id == "WF-103" else 0.95
        return {
            "key_findings": [f"Discovery Alpha for {topic}", f"Discovery Beta for {topic}"],
            "confidence_score": score
        }

    async def human_override_queue(self, flagged_findings: List[str], original_score: float, workflow_id: str) -> Dict[str, Any]:
        print(f"\n👥 [{workflow_id}] 🔍 [HUMAN OVERRIDE QUEUE] Low confidence alert ({original_score}). Reviewing raw logs: {flagged_findings}")
        await asyncio.sleep(0.2)
        print(f"👥 [{workflow_id}] 📝 [Human] Review complete. Data overridden and clean.\n")
        return {
            "key_findings": ["Human Vetted Metric A", "Human Vetted Metric B"],
            "confidence_score": 1.0
        }

    async def writer_agent(self, findings: List[str], workflow_id: str) -> Dict[str, Any]:
        print(f"📡 [{workflow_id}] 🤖 [Writer] Compiling isolated report context...")
        await asyncio.sleep(0.5)
        return {"summary_draft": f"Report Content: {', '.join(findings)}"}

# ==========================================
# CORE ASYNCHRONOUS ORCHESTRATION ENGINE
# ==========================================
class DistributedHybridOrchestrator:
    def __init__(self, yaml_config_str: str, agents_instance: AsyncAgentsRegistry):
        self.config = yaml.safe_load(yaml_config_str)
        self.agent_registry = agents_instance

    def _extract_context(self, payload: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        return {agent_arg: payload[graph_key] for graph_key, agent_arg in mapping.items() if graph_key in payload}

    async def execute_workflow(self, workflow_id: str, initial_topic: str) -> Dict[str, Any]:
        graph = AsyncProvenanceGraph()
        current_state = "TASK_CREATED"
        latest_payload = {"topic": initial_topic}
        await graph.append("SYSTEM", current_state, latest_payload)

        error_occurred, error_message, retry_count = False, "", 0

        while True:
            state_rules = self.config["states"].get(current_state)
            if not state_rules:
                print(f"✅ [{workflow_id}] [Engine] Pipeline execution terminated at state: {current_state}")
                break

            # Process dynamic branching conditions
            if "routing_rules" in state_rules:
                for rule in state_rules["routing_rules"]:
                    if eval(rule["condition"], {}, latest_payload):
                        print(f"🔀 [{workflow_id}] [Router] '{rule['condition']}' matched -> Heading to state {rule['target_state']}")
                        current_state = rule["target_state"]
                        break
                continue

            agent_name = state_rules.get("agent")
            next_event_type = state_rules["next_event"]
            max_allowed_retries = state_rules.get("max_retries", 1)

            if not agent_name:
                print(f"✅ [{workflow_id}] [Engine] Standard termination reached.")
                break

            # Map precise arguments (Ensures isolated, minimal context visibility)
            agent_kwargs = self._extract_context(latest_payload, state_rules["context_mapping"])
            agent_kwargs["workflow_id"] = workflow_id

            if error_occurred:
                agent_kwargs["_error_occurred"] = True
                agent_kwargs["_error_message"] = error_message

            # Call async agent execution method
            agent_callable = getattr(self.agent_registry, agent_name)
            raw_output = await agent_callable(**agent_kwargs)

            # Route through structural type validation guard
            schema = SCHEMA_REGISTRY.get(next_event_type)
            if schema:
                try:
                    validated_model = schema(**raw_output)
                    clean_payload = validated_model.model_dump()
                    
                    # Reset failure loop states upon successful execution pass
                    error_occurred, error_message, retry_count = False, "", 0
                    await graph.append(agent_name.upper(), next_event_type, clean_payload)
                    current_state = next_event_type
                    latest_payload = clean_payload
                except (ValidationError, TypeError, KeyError) as e:
                    retry_count += 1
                    print(f"🚨 [{workflow_id}] [Guard Failure] State '{current_state}' failed verification ({retry_count}/{max_allowed_retries})")
                    
                    if retry_count >= max_allowed_retries:
                        print(f"⚠️ [{workflow_id}] [Engine] Max retries exhausted! Escalate path to HUMAN_INTERVENTION state.")
                        error_occurred, error_message, retry_count = False, "", 0
                        current_state = "HUMAN_INTERVENTION"
                        continue
                    
                    error_occurred = True
                    error_message = str(e)
            else:
                await graph.append(agent_name.upper(), next_event_type, raw_output)
                current_state = next_event_type
                latest_payload = raw_output

        return graph.events[-1].payload

# ==========================================
# MULTI-TASK CONCURRENT RUNNER
# ==========================================
async def main():
    with open("workflow.yml", "r") as f:
        yaml_config = f.read()

    agents = AsyncAgentsRegistry()
    orchestrator = DistributedHybridOrchestrator(yaml_config, agents)

    tasks = [
        ("WF-101", "Quantum Cryptography"), # Smooth happy path through pipeline
        ("WF-102", "Autonomous Vehicles"),   # Hits error boundary then self-corrects
        ("WF-103", "Deep-Sea Engineering")   # Triggers low confidence and pulls in human review
    ]

    print("🚀 Booting Async Workflow Orchestration Matrix...")
    await asyncio.gather(*(orchestrator.execute_workflow(w_id, topic) for w_id, topic in tasks))
    print("🏁 Parallel runs finalized successfully.")

if __name__ == "__main__":
    asyncio.run(main())
