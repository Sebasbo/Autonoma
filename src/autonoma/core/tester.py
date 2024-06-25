"""Tester module for the Autonoma package."""

import json
from typing import List, Tuple
from pydantic import BaseModel
from ..utils.code_executor import CodeExecutor
from autonoma.models import CodeFile, TestCodeResponse, TestResult, CodeChange, GeneratedCode


class Tester:
    """Tester class for running tests on modified code."""

    def __init__(self, llm_interface):
        """
        Initialize the Tester.

        Args:
            llm_interface: An interface to the language model for generating test code.
        """
        self.llm_interface = llm_interface
        self.code_executor = CodeExecutor()

    def run_tests(
        self, modified_code: "GeneratedCode", codebase: List[CodeFile]
    ) -> Tuple[List[TestResult], List[TestResult]]:
        """
        Run tests on the modified code.

        Args:
            modified_code: The modified code to test.
            codebase: The entire codebase.

        Returns:
            A tuple containing lists of unsuccessful and successful test results.
        """
        test_code_response = self.generate_test_code(modified_code)

        unsuccessful_tests, successful_tests = [], []
        for test_code in test_code_response.tests:
            updated_codebase = {file.path: file.content for file in codebase}
            for file_change in modified_code.code_changes:
                updated_codebase[file_change.path] = file_change.code

            full_code = test_code.test_code
            result = self.code_executor.run(full_code, updated_codebase)

            test_result = TestResult(
                success=result.success,
                message=result.output,
                test_code=test_code.test_code,
                original_code_path=test_code.original_code_path,
            )

            if not result.success:
                unsuccessful_tests.append(test_result)
            else:
                successful_tests.append(test_result)

        return unsuccessful_tests, successful_tests

    def generate_test_code(self, code: "GeneratedCode") -> TestCodeResponse:
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
        response = self.llm_interface.generate(prompt)
        try:
            parsed_response = json.loads(response)
            return TestCodeResponse(**parsed_response)
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse LLM response as JSON. Raw response: {response}")


# This should be imported from the appropriate module
class GeneratedCode(BaseModel):
    """Represents the generated code from the LLM."""

    code_changes: List[CodeChange]


class CodeChange(BaseModel):
    """Represents a code change in a specific file."""

    code: str
    path: str
