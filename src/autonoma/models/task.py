from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class TaskType(str, Enum):
    """Defines the types of tasks the agent can perform."""
    CODE_IMPLEMENTATION = "code_implementation"
    CODE_ANALYSIS = "code_analysis"
    DOCUMENTATION = "documentation"


class TaskStatus(str, Enum):
    """Defines the possible statuses of a task."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionType(str, Enum):
    """Defines how a task's execution component should be handled."""
    LLM_CALL = "llm_call"
    CODE_EXECUTION = "code_execution"


class Task(BaseModel):
    """Represents a single task in the Autonoma system."""
    id: str = Field(description="Unique identifier for the task.")
    description: str = Field(description="Detailed description of what the task entails.")
    task_type: TaskType = Field(description="The category of the task.")
    status: TaskStatus = Field(default=TaskStatus.NOT_STARTED, description="Current status of the task.")
    execution_type: ExecutionType = Field(description="Specifies the method of execution for the task.")
    file_paths: List[str] = Field(default_factory=list, description="List of file paths relevant to this task.")
    estimated_complexity: str = Field(default="Medium", description="A subjective measure of task complexity.")
    cmd: Optional[str] = Field(default=None, description="Command to be executed, if task_type is code_execution.")
    prompt_llm: Optional[str] = Field(default=None, description="Prompt to be used for LLM, if task_type is llm_call.")
    relevant_code: Dict[str, str] = Field(default_factory=dict, description="Snippets of relevant code, with file path as key.")


class ExecutedTask(Task):
    """Represents a task that has been executed, including its output."""
    output: str = Field(default="", description="The output or result of executing the task.")
    pass_context: bool = Field(default=False, description="Whether to pass this task's output as context to subsequent tasks.")
