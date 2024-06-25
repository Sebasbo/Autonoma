from pydantic import BaseModel, Field


class TestCode(BaseModel):
    """Represents a generated test code."""

    test_code: str
    test_path: str
    original_code_path: str


class TestCodeResponse(BaseModel):
    """Represents the response from test code generation."""

    tests: list[TestCode]
