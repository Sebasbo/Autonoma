from pydantic import BaseModel, Field
from .task import ExecutionType # Import from .task


class TaskExecution(BaseModel):
    """
    Represents the details for executing a specific part of a task,
    specifying the type of execution and the content (e.g., script or prompt).
    """
    execution_type: ExecutionType = Field(description="The type of execution required (e.g., LLM call or code execution).")
    content: str = Field(description="The actual content to be executed, such as a script for code execution or a prompt for an LLM call.")

    class Config:
        use_enum_values = True # Ensures that the enum values (strings) are used in serialization
