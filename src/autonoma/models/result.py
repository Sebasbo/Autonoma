from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from .project import Project


class TestResult(BaseModel):
    """Represents the result of a test execution."""

    success: bool
    message: str
    test_code: str
    original_code_path: str


class TaskResult(BaseModel):
    """Represents the result of a task execution."""

    task_id: str
    success: bool
    output: str
    modified_files: Dict[str, str] = Field(default_factory=dict)
    new_files: Dict[str, str] = Field(default_factory=dict)
    test_results: Optional[List[TestResult]] = None


class AgentResult(BaseModel):
    """Represents the result of an agent's execution."""

    agent_name: str
    task_results: List[TaskResult]


class ProjectResult(BaseModel):
    """Represents the result of a project execution."""

    project: Project
    agent_results: List[AgentResult]
    modified_files: Dict[str, str]
    new_files: Dict[str, str]
    unchanged_files: Dict[str, str]
    thought_process: List[str]


class FinalResult(BaseModel):
    """Represents the final result of the Autonoma execution."""

    project_result: ProjectResult
    output_directory: str


class ExecutionResult(BaseModel):
    """Represents the result of code execution."""

    success: bool
    output: str
    mocked_modules: List[str] = Field(default_factory=list)
