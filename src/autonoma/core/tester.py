"""Tester module for the Autonoma package."""

import json
from typing import List, Tuple, Optional, Protocol
from pydantic import BaseModel # Keep for local TestCodeResponse if not moved
from ..utils.code_executor import CodeExecutor

# Updated model imports to reflect their new locations
from autonoma.models.code import CodeFile, GeneratedCode, CodeChange
from autonoma.models.result import TestResult
# Assuming TestCodeResponse might be a local definition or from a non-relocated model path for now
# If TestCodeResponse is a shared model, its import might need to point to models.test or similar
from autonoma.models import TestCodeResponse # Placeholder if it's in models/__init__.py


class LLMInterfaceProtocol(Protocol):
    """Protocol for Language Model Interface."""
    def generate(self, user_prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 150) -> str:
        ...


class Tester:
    """Tester class for running tests on modified code."""

    def __init__(self, llm_interface: LLMInterfaceProtocol):
        """
        Initialize the Tester.

        Args:
            llm_interface: An interface to the language model for generating test code.
        """
        self.llm_interface: LLMInterfaceProtocol = llm_interface
        self.code_executor = CodeExecutor()

    def run_tests(
        self, modified_code: GeneratedCode, codebase: List[CodeFile]
    ) -> Tuple[List[TestResult], List[TestResult]]:
        """
        Run tests on the modified code.

        Args:
            modified_code: The modified code to test.
            codebase: The entire codebase.

        Returns:
            A tuple containing lists of unsuccessful and successful test results.
        """
        test_code_response: TestCodeResponse = self.generate_test_code(modified_code)

        unsuccessful_tests: List[TestResult] = []
        successful_tests: List[TestResult] = []
        for test_code_item in test_code_response.tests: # Assuming TestCodeResponse has a 'tests' attribute
            updated_codebase = {file.path: file.content for file in codebase}
            for file_change in modified_code.code_changes:
                updated_codebase[file_change.path] = file_change.code

            full_code_to_execute = test_code_item.test_code # Assuming test_code_item has 'test_code'
            # Ensure CodeExecutor.run returns a structure compatible with this logic
            execution_result = self.code_executor.run(full_code_to_execute, updated_codebase)

            test_result_obj = TestResult(
                success=execution_result.success,
                message=execution_result.output, # Or error, depending on CodeExecutor's result structure
                test_code=test_code_item.test_code,
                original_code_path=test_code_item.original_code_path, # Assuming test_code_item has 'original_code_path'
            )

            if not execution_result.success:
                unsuccessful_tests.append(test_result_obj)
            else:
                successful_tests.append(test_result_obj)

        return unsuccessful_tests, successful_tests

    def generate_test_code(self, code: GeneratedCode) -> TestCodeResponse:
        """
        Generate test code for the given code.

        Args:
            code: The code to generate tests for.

        Returns:
            A TestCodeResponse object containing the generated test code.
        """
        prompt = f"""
        Given the following Python code:
        
        {json.dumps(code.dict(), default=lambda o: o.dict() if hasattr(o, 'dict') else str(o))}
        
        Generate unit tests to verify its correctness. The tests should be self-contained and not rely on importing from external modules.
        Include the original function in the test code and use it directly.

        Return a JSON object with the following structure:
        {{
            "tests": [
                {{
                    "test_code": "The generated test code as a string",
                    "test_path": "specific file for which the tests are",
                    "original_code_path": "the path of the original file"
                }}
            ]
        }}

        Ensure that the test code:
        1. Defines any necessary functions from the original code
        2. Includes import statements for unittest
        3. Defines a test class that inherits from unittest.TestCase
        4. Includes at least one test method
        5. Has a block to run the tests if the script is run directly
        6. Writes all the tests for a file separately

        Do not use any import statements other than for the unittest module.
        """
        response: str = self.llm_interface.generate(prompt)
        try:
            # Assuming TestCodeResponse is a Pydantic model that can parse this
            parsed_response = json.loads(response)
            return TestCodeResponse(**parsed_response)
        except json.JSONDecodeError as e:
            # It's good practice to include the original error for context
            raise ValueError(f"Failed to parse LLM response as JSON. Raw response: {response}. Error: {e}")
# Removed local redefinitions of GeneratedCode and CodeChange as they are now imported.
