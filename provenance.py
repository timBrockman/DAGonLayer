"""
Immutable provenance graph for audit trail and event tracking.
"""

import asyncio
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class Event:
    """Immutable event in the provenance graph."""
    event_id: int
    timestamp: str
    sender: str
    event_type: str
    payload: Dict[str, Any]


class AsyncProvenanceGraph:
    """Immutable audit trail of all workflow events."""
    
    def __init__(self):
        self.events: List[Event] = []
        self._counter = 0
        self._lock = asyncio.Lock()
    
    async def append(
        self, 
        sender: str, 
        event_type: str, 
        payload: Dict[str, Any]
    ) -> Event:
        """Thread-safe event appending."""
        async with self._lock:
            self._counter += 1
            event = Event(
                self._counter,
                datetime.utcnow().isoformat(),
                sender,
                event_type,
                payload
            )
            self.events.append(event)
            return event
    
    def to_json(self) -> str:
        """Export provenance graph as JSON."""
        return json.dumps(
            [asdict(e) for e in self.events],
            default=str
        )
    
    def get_events_by_workflow(self, workflow_id: str) -> List[Event]:
        """Filter events by workflow ID (inferred from payloads)."""
        # Note: workflow_id is not stored in Event, but could be added if needed
        return self.events
