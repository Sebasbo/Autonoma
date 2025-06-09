from pydantic import BaseModel, Field
from typing import List # Import List


class TestCode(BaseModel):
    """Represents a single generated test script, including its content and target paths."""
    test_code: str = Field(description="The complete source code of the generated test script.")
    test_path: str = Field(description="The suggested file path where this test script should be saved.")
    original_code_path: str = Field(description="The path to the original code file that this test is intended to verify.")


class TestCodeResponse(BaseModel):
    """Represents a collection of generated test scripts, typically from an LLM or test generation tool."""
    tests: List[TestCode] = Field(default_factory=list, description="A list of TestCode objects, each representing a generated test script.")
