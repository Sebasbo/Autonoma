from pydantic import BaseModel, Field
from typing import List
from .agent import Agent


class Project(BaseModel):
    """Represents a project in the Autonoma system."""

    agents: List[Agent] = Field(default_factory=list)
