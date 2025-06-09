from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from .project import Project, ExecutedProject # ExecutedProject will be used by ProjectResult
from .code import CodeFile # Imported for List[CodeFile]


class TestResult(BaseModel):
    """Represents the result of a test execution."""
    success: bool = Field(description="Indicates if the test passed or failed.")
    message: str = Field(description="Output message from the test execution, e.g., error details.")
    test_code: str = Field(description="The code of the test that was executed.")
    original_code_path: str = Field(description="Path to the original code file that this test targets.")


class TaskResult(BaseModel):
    """Represents the result of a single task's execution."""
    task_id: str = Field(description="Identifier of the task that was executed.")
    success: bool = Field(description="Indicates if the task execution was successful.")
    output: str = Field(description="General output or summary from the task execution.")
    modified_files: Dict[str, str] = Field(default_factory=dict, description="Dictionary of file paths to content for modified files by this task. Prefer using ProjectResult for final file states.")
    new_files: Dict[str, str] = Field(default_factory=dict, description="Dictionary of file paths to content for new files created by this task. Prefer using ProjectResult for final file states.")
    test_results: Optional[List[TestResult]] = Field(default=None, description="Results of any tests executed as part of this task.")


class AgentResult(BaseModel):
    """Represents the collected results from all tasks executed by an agent."""
    agent_name: str = Field(description="Name of the agent.")
    task_results: List[TaskResult] = Field(default_factory=list, description="List of results from tasks executed by this agent.")


class ProjectResult(BaseModel):
    """
    Represents the overall result of a project execution, including final file states.
    This model should reflect the definitive state of the codebase after all agent operations.
    """
    project: ExecutedProject = Field(description="The executed project state, including all agents and their executed tasks.")
    modified_files: List[CodeFile] = Field(default_factory=list, description="List of code files that were modified from their original state.")
    new_files: List[CodeFile] = Field(default_factory=list, description="List of new code files created during the project execution.")
    unchanged_files: List[CodeFile] = Field(default_factory=list, description="List of code files that were part of the initial codebase and remain unchanged.")
    thought_process: List[str] = Field(default_factory=list, description="A log of thoughts or key decisions made during the project execution by the orchestrating agent.")


class FinalResult(BaseModel):
    """
    Represents the final, comprehensive result of the Autonoma execution,
    packaging the project result with output location information.
    """
    project_result: ProjectResult = Field(description="The detailed results of the project execution.")
    output_directory: str = Field(description="Directory where output files, logs, or results are stored.")


class ExecutionResult(BaseModel):
    """Represents the result of a generic code execution attempt."""
    success: bool = Field(description="Whether the code execution was successful.")
    output: str = Field(description="Standard output (stdout) from the execution.")
    error: Optional[str] = Field(default=None, description="Standard error (stderr) from the execution, if any.")
    mocked_modules: List[str] = Field(default_factory=list, description="List of modules that were mocked during execution.")
