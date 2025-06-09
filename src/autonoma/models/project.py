from pydantic import BaseModel, Field
from typing import List
from .agent import Agent, ExecutedAgent # Assuming Agent and ExecutedAgent will remain/be in agent.py


class Project(BaseModel):
    """
    Represents a project in the Autonoma system, composed of multiple agents.
    """
    agents: List[Agent] = Field(default_factory=list, description="List of agents assigned to this project.")


class ExecutedProject(Project):
    """
    Represents a project that has been executed, including the executed state of its agents.
    """
    agents: List[ExecutedAgent] = Field(default_factory=list, description="List of executed agents within this project.")
