from pydantic import BaseModel
from typing import List
from .code import CodeFile


class PlanRequest(BaseModel):
    """Represents a request for creating a query plan."""

    query: str
    code_base: List[CodeFile]
