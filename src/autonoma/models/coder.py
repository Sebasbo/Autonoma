from pydantic import BaseModel, Field


class CodeChange(BaseModel):
    """Represents a code change in a specific file."""

    code: str
    path: str


class GeneratedCode(BaseModel):
    """Represents the generated code from the LLM."""

    code_changes: list[CodeChange] = Field(default_factory=list)
