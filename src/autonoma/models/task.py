from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class TaskType(str, Enum):
    CODE_IMPLEMENTATION = "code_implementation"
    DOCUMENTATION = "documentation"


class TaskStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionType(str, Enum):
    LLM_CALL = "llm_call"
    CODE_EXECUTION = "code_execution"


class Task(BaseModel):
    """Represents a single task in the Autonoma system."""

    id: str
    description: str
    task_type: TaskType
    status: TaskStatus = Field(default=TaskStatus.NOT_STARTED)
    execution_type: ExecutionType
    file_paths: List[str]
    estimated_complexity: str = Field(default="Medium")
    cmd: Optional[str] = None
    prompt_llm: Optional[str] = None
    relevant_code: Dict[str, str] = Field(default_factory=dict)
