"""
Configuration management for workflow definitions.
"""

import yaml
from pathlib import Path
from typing import Dict, Any


class WorkflowConfig:
    """Manages workflow configuration loading and validation."""
    
    def __init__(self, yaml_path: str = "workflow.yml"):
        self.yaml_path = Path(yaml_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load and validate YAML config."""
        if not self.yaml_path.exists():
            raise FileNotFoundError(f"Config not found: {self.yaml_path}")
        
        with open(self.yaml_path, "r") as f:
            return yaml.safe_load(f)
    
    def get_state_rules(self, state: str) -> Dict[str, Any]:
        """Get rules for a specific state."""
        return self.config.get("states", {}).get(state, {})
    
    def get_all_states(self) -> Dict[str, Any]:
        """Get all state definitions."""
        return self.config.get("states", {})
    
    def reload(self):
        """Reload configuration from disk."""
        self.config = self._load_config()
