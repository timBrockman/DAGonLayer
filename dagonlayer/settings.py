"""Environment-driven runtime settings."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def get_env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on", "y"}


class Settings:
    """Application settings loaded from environment variables."""

    WORKFLOW_FILE: str = os.getenv("WORKFLOW_FILE", "workflow.yml")
    MODEL_ID: str = os.getenv("MODEL_ID", os.getenv("DAGONLAYER_MODEL", os.getenv("STATEGUARD_MODEL", "openai:gpt-4")))
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_API_BASE: Optional[str] = os.getenv("OPENAI_API_BASE")
    ENABLE_LOGGING: bool = get_env_bool("ENABLE_LOGGING", True)
    ENABLE_TRACING: bool = get_env_bool("ENABLE_TRACING", False)

    @classmethod
    def workflow_path(cls) -> Path:
        return Path(cls.WORKFLOW_FILE)
