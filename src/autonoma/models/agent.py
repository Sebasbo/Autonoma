from pydantic import BaseModel, Field
from typing import List
from .task import Task, ExecutedTask # Import from the new location


class Agent(BaseModel):
    """
    Represents an agent in the Autonoma system, defined by its role, goals, and assigned tasks.
    """
    name: str = Field(description="The unique name of the agent.")
    role: str = Field(description="The role or specialization of the agent (e.g., 'Coder', 'Planner').")
    goal: str = Field(description="The primary objective or goal this agent is designed to achieve.")
    tasks: List[Task] = Field(default_factory=list, description="List of tasks assigned to this agent.")


class ExecutedAgent(Agent):
    """
    Represents an agent that has executed its tasks, including the results of those tasks.
    """
    tasks: List[ExecutedTask] = Field(default_factory=list, description="List of tasks after execution by this agent.")
