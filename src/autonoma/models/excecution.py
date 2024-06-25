from enum import Enum
from pydantic import BaseModel


class ExecutionType(str, Enum):
    LLM_CALL = "llm_call"
    CODE_EXECUTION = "code_execution"


class TaskExecution(BaseModel):
    execution_type: ExecutionType
    content: str

    class Config:
        use_enum_values = True
