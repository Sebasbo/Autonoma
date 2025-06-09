from pydantic import BaseModel, Field
from typing import List
from .code import CodeFile


class PlanRequest(BaseModel):
    """Represents a request for creating a query plan for code modification or analysis."""
    query: str = Field(description="The natural language query describing the desired operation.")
    code_base: List[CodeFile] = Field(description="A list of CodeFile objects representing the current state of the codebase relevant to the query.")
