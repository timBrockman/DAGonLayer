"""
Shared Pydantic schemas for workflow validation.
"""

from typing import List
from pydantic import BaseModel, Field


class ResearcherOutputSchema(BaseModel):
    """Output schema for research agent."""
    key_findings: List[str] = Field(..., description="Vetted structured research findings.")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in findings (0-1).")


class HumanOverrideSchema(BaseModel):
    """Output schema for human review."""
    key_findings: List[str] = Field(..., description="Human-reviewed findings.")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence after human review.")


class WriterOutputSchema(BaseModel):
    """Output schema for writer agent."""
    summary_draft: str = Field(..., min_length=10, description="Compiled report content.")


# Schema registry for validation during workflow execution
SCHEMA_REGISTRY = {
    "RESEARCH_COMPLETE": ResearcherOutputSchema,
    "READY_FOR_WRITING": HumanOverrideSchema,
    "WRITING_COMPLETE": WriterOutputSchema,
}
