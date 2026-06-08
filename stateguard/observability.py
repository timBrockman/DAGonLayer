"""
Observability and telemetry for workflow execution.
"""

import logging
from typing import Optional, List
from contextlib import contextmanager
from datetime import datetime


class WorkflowObserver:
    """Observability & telemetry for workflow execution."""
    
    def __init__(self, enable_logging: bool = True, enable_tracing: bool = False):
        self.enable_logging = enable_logging
        self.enable_tracing = enable_tracing
        self.logger = self._setup_logger() if enable_logging else None
        self.trace_events: List[dict] = []
    
    def _setup_logger(self) -> logging.Logger:
        """Setup structured logging."""
        logger = logging.getLogger("stateguard")
        
        # Avoid adding duplicate handlers
        if logger.handlers:
            return logger
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger
    
    @contextmanager
    def trace_span(self, workflow_id: str, operation: str):
        """Context manager for tracing operations."""
        start_time = datetime.utcnow()
        
        if self.logger:
            self.logger.info(f"[{workflow_id}] START: {operation}")
        
        try:
            yield
        finally:
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            if self.logger:
                self.logger.info(f"[{workflow_id}] END: {operation} ({duration:.2f}s)")
            
            if self.enable_tracing:
                self.trace_events.append({
                    "workflow_id": workflow_id,
                    "operation": operation,
                    "duration_seconds": duration,
                    "timestamp": start_time.isoformat()
                })
    
    def log_state_transition(self, workflow_id: str, from_state: str, to_state: str):
        """Log state transitions."""
        if self.logger:
            self.logger.info(f"[{workflow_id}] STATE: {from_state} -> {to_state}")
    
    def log_agent_call(self, workflow_id: str, agent_name: str, kwargs: dict):
        """Log agent invocations."""
        if self.logger:
            safe_kwargs = {k: v for k, v in kwargs.items() if k != "_error_message"}
            self.logger.info(f"[{workflow_id}] AGENT: {agent_name} with {safe_kwargs}")
    
    def log_validation_error(self, workflow_id: str, state: str, error: str):
        """Log validation failures."""
        if self.logger:
            self.logger.error(f"[{workflow_id}] VALIDATION FAILED in {state}: {error}")
    
    def get_trace_events(self) -> List[dict]:
        """Get all recorded trace events."""
        return self.trace_events
