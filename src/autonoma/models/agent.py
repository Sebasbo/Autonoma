from typing import List
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class TaskType(str, Enum):
    CODE_IMPLEMENTATION = "code_implementation"
    CODE_ANALYSIS = "code_analysis"


class TaskStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionType(str, Enum):
    LLM_CALL = "llm_call"
    CODE_EXECUTION = "code_execution"


class Task(BaseModel):
    id: str
    description: str
    task_type: TaskType
    status: TaskStatus = Field(default=TaskStatus.NOT_STARTED)
    execution_type: ExecutionType
    file_paths: list[str]
    estimated_complexity: str = Field(default="Medium")
    relevant_code: Optional[dict] = Field(default={})


class ExecutedTask(Task):
    output: str = Field(default="")
    pass_context: bool = Field(default=False)


class Agent(BaseModel):
    name: str
    role: str
    goal: str
    tasks: List[Task] = Field(default_factory=list)


class ExecutedAgent(Agent):
    tasks: List[ExecutedTask] = Field(default_factory=list)


class Project(BaseModel):
    agents: List[Agent] = Field(default_factory=list)


class ExecutedProject(Project):
    agents: List[ExecutedAgent] = Field(default_factory=list)


class CodeFile(BaseModel):
    path: str
    content: str


class ProjectResult(BaseModel):
    project: ExecutedProject
    modified_files: List[CodeFile] = Field(default_factory=list)
    new_files: List[CodeFile] = Field(default_factory=list)
    unchanged_files: List[CodeFile] = Field(default_factory=list)
    thought_process: List[str] = Field(default_factory=list)
