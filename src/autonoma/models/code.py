from pydantic import BaseModel, Field
from typing import List


class CodeFile(BaseModel):
    """Represents a code file in the Autonoma system."""

    path: str
    content: str


class CodeChange(BaseModel):
    """Represents a code change in a specific file."""

    code: str
    path: str


class GeneratedCode(BaseModel):
    """Represents the generated code from the LLM."""

    code_changes: List[CodeChange] = Field(default_factory=list)
