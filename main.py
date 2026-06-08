"""
Entry point for workflow orchestration.
Configures and runs the distributed hybrid orchestrator.
"""

import asyncio
import sys

from config import WorkflowConfig
from agents import PydanticAIRegistry
from orchestrator import DistributedHybridOrchestrator
from observability import WorkflowObserver


async def main():
    """
    Entry point for workflow orchestration.
    
    Initializes all components and runs workflows concurrently.
    """
    try:
        # === COMPONENT INITIALIZATION ===
        config = WorkflowConfig("workflow.yml")
        agents = PydanticAIRegistry(model="openai:gpt-4")
        observer = WorkflowObserver(enable_logging=True, enable_tracing=True)
        
        orchestrator = DistributedHybridOrchestrator(config, agents, observer)
        
        # === WORKFLOW DEFINITIONS ===
        tasks = [
            ("WF-101", "Quantum Cryptography"),      # Happy path
            ("WF-102", "Autonomous Vehicles"),       # Error recovery
            ("WF-103", "Deep-Sea Engineering"),      # Human intervention
        ]
        
        print("🚀 Booting Async Workflow Orchestration Matrix...")
        
        # === CONCURRENT EXECUTION ===
        results = await asyncio.gather(
            *(orchestrator.execute_workflow(w_id, topic) for w_id, topic in tasks),
            return_exceptions=True
        )
        
        print("🏁 Parallel runs finalized successfully.")
        
        # === RESULTS ===
        for i, (w_id, topic) in enumerate(tasks):
            result = results[i]
            if isinstance(result, Exception):
                print(f"❌ {w_id}: {result}")
            else:
                print(f"✅ {w_id}: {result}")
        
        # === TELEMETRY EXPORT ===
        if observer.enable_tracing:
            trace_events = observer.get_trace_events()
            print(f"\n📊 Trace events recorded: {len(trace_events)}")
            for event in trace_events:
                print(f"  - {event['operation']}: {event['duration_seconds']:.3f}s")
        
        return 0
    
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
