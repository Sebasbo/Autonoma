import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Assuming ADK Function Tool base class will be available
# from adk.tool_registry import FunctionTool

# Import necessary models
from autonoma.models.coder import CodeChange # For CodeToTest
from autonoma.models.test import TestCode, TestCodeResponse # For LLM response parsing

# Placeholder for LLMInterface - replace with actual interface
class LLMInterface:
    def __init__(self, api_key: str = "dummy_key", model_name: str = "dummy_model", temperature: float = 0.0): # Added params
        self.api_key = api_key # Not used by this placeholder's generate
        self.model_name = model_name
        self.temperature = temperature

    def generate(self, prompt: str) -> str:
        # This is a placeholder. In a real scenario, this would call the LLM.
        print(f"---- LLMInterface.generate called for tests ----")
        print(f"Prompt: {prompt[:150]}...")
        print(f"---- End LLMInterface.generate ----")

        # Dummy response for generate_and_prepare_tests
        # This structure matches TestCodeResponse
        dummy_response = {
            "tests": [
                {
                    "test_code": "import unittest\n\ndef function_to_test(a, b):\n    return a + b\n\nclass TestMyFunction(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(function_to_test(1, 2), 3)\n\nif __name__ == '__main__':\n    unittest.main()",
                    "test_path": "test_utils.py", # Suggests a path for the test script
                    "original_code_path": "utils.py" # Path of the code being tested
                }
            ]
        }
        return json.dumps(dummy_response)

# --- Pydantic Models for Tool I/O ---

class GenerateAndPrepareTestsInput(BaseModel):
    code_to_test: List[CodeChange] = Field(description="List of code changes (new or modified code) to be tested.")
    existing_codebase_map: Dict[str, str] = Field(default_factory=dict, description="Map of existing file paths to their content, for context.")

class PreparedTest(BaseModel):
    test_script_path: str = Field(description="The path where the test script should be saved/executed from.")
    test_script_content: str = Field(description="The content of the generated test script.")
    # files_for_execution_context: Dict[str, str] = Field(description="All files needed for the test execution environment. Key: path, Value: content.")
    # ADK Code Execution tool likely takes a list of file paths and a workspace, not a direct map.
    # The context will be constructed by placing these files in the exec environment.
    # For now, let's list the files that need to be present.
    # The actual content will be sourced from code_to_test and existing_codebase_map.
    required_files_for_context: List[str] = Field(description="List of file paths (original code, modified code) required for the test to run, in addition to the test script itself.")


class GenerateAndPrepareTestsOutput(BaseModel):
    prepared_tests: List[PreparedTest] = Field(description="List of test scripts prepared for execution.")

# Raw result from an ADK Code Execution tool (simulated)
class RawExecutionResult(BaseModel):
    success: bool # Typically, this means the command ran, not that tests passed
    stdout: str
    stderr: str
    # ran_without_errors: bool # This field might be redundant if `success` means process completion
    # Let's assume the ADK execution tool provides a clear signal for test pass/fail if possible,
    # otherwise, we parse stdout/stderr. For now, we'll rely on parsing stdout/stderr.
    # We also need to know which test script this result belongs to.
    # This would likely be part of the loop invoking the ADK exec tool, not part of its raw output for a single run.
    # Let's assume the calling ADK agent will correlate results with test_script_path.

class InterpretTestResultsInput(BaseModel):
    # Each item in this list corresponds to the execution of one PreparedTest
    executed_tests_results: List[Dict] = Field(description="List of raw execution results from the ADK Code Execution tool. Each dict should include 'test_script_path', 'stdout', 'stderr', and 'process_success' (whether the command ran).")
    # Example: [{"test_script_path": "test_utils.py", "stdout": "...", "stderr": "...", "process_success": True}]

class InterpretedTestResult(BaseModel):
    """Adapted from autonoma.models.test.TestResult"""
    success: bool = Field(description="True if the test passed, False otherwise.")
    message: str = Field(description="Combined stdout/stderr or a summary message.")
    test_script_path: str = Field(description="Path to the test script that was executed.")
    # original_code_path: Optional[str] = Field(None, description="Path of the original code file this test was targeting.") # This might be useful for reporting

class InterpretTestResultsOutput(BaseModel):
    successful_tests: List[InterpretedTestResult] = Field(default_factory=list)
    failed_tests: List[InterpretedTestResult] = Field(default_factory=list)


# --- TestExecutionTool Class ---

class TestExecutionTool: # Potentially: TestExecutionTool(FunctionTool)
    def __init__(self, llm_interface: LLMInterface):
        self.llm_interface = llm_interface

    def _generate_test_code_from_llm(self, code_changes: List[CodeChange]) -> TestCodeResponse:
        """
        Generates test code using the LLM.
        Adapts prompt from Tester.generate_test_code.
        """
        # Convert CodeChange list to dict for the prompt, similar to `code.dict()` in Tester
        code_to_prompt = {"code_changes": [cc.model_dump() for cc in code_changes]}

        prompt = f"""
        Given the following Python code changes:

        {json.dumps(code_to_prompt, indent=2)}

        Generate unit tests to verify the correctness of these changes.
        The tests should be self-contained.
        If the code change is for an existing file, assume functions/classes from that file are available.
        If the code change is for a new file, test its public interface.

        Return a JSON object with the following structure:
        {{
            "tests": [
                {{
                    "test_code": "The generated test code as a string (unittest framework)",
                    "test_path": "A suggested path for this test script (e.g., test_module_name.py)",
                    "original_code_path": "The path of the original/modified code file this test targets"
                }}
            ]
        }}

        Ensure that the test code for each test:
        1. Includes necessary import statements (e.g., `import unittest`).
        2. Defines a test class inheriting from `unittest.TestCase`.
        3. Contains one or more test methods (e.g., `def test_my_feature(self):`).
        4. Includes a block to run tests if the script is executed directly (e.g., `if __name__ == '__main__': unittest.main()`).
        5. Focus on testing the provided code_changes. Do not try to import the code being tested from its original_code_path, instead, assume the code is directly available or paste it if necessary for self-contained tests.
           However, if the original code is very long, you can assume it's importable from original_code_path for context.
           Prefer creating tests that can run if original_code_path and test_path are in the same directory or appropriate PYTHONPATH.

        Provide tests for each file in the code_changes.
        """
        raw_llm_response = self.llm_interface.generate(prompt)
        try:
            # TestCodeResponse.parse_raw expects a JSON string
            return TestCodeResponse.model_validate_json(raw_llm_response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM test generation output as JSON: {e}. Response: {raw_llm_response}")
        except Exception as e: # Catch Pydantic validation errors
            raise ValueError(f"Failed to validate LLM output against TestCodeResponse model: {e}. Response: {raw_llm_response}")

    def generate_and_prepare_tests(self, tool_input: GenerateAndPrepareTestsInput) -> GenerateAndPrepareTestsOutput:
        """
        Generates test scripts using LLM and prepares them for execution.
        """
        if not tool_input.code_to_test:
            return GenerateAndPrepareTestsOutput(prepared_tests=[])

        generated_test_payload = self._generate_test_code_from_llm(tool_input.code_to_test)

        prepared_tests_list: List[PreparedTest] = []

        # Create a map of the modified code for easy lookup
        modified_code_map = {change.path: change.code for change in tool_input.code_to_test}

        for test_case in generated_test_payload.tests:
            required_files = set()

            # The primary code file being tested
            if test_case.original_code_path in modified_code_map:
                required_files.add(test_case.original_code_path)
            elif test_case.original_code_path in tool_input.existing_codebase_map:
                required_files.add(test_case.original_code_path)
            # else: The file mentioned in original_code_path might be a new file itself,
            # and its content is within code_to_test.

            # Add all other modified files as they might be dependencies
            for change in tool_input.code_to_test:
                required_files.add(change.path)

            # The test script itself is implicitly needed but will be the entry point for execution.
            # The ADK execution tool will typically be told "run this script", and that script
            # needs to be able to import/access the `required_files`.

            prepared_tests_list.append(
                PreparedTest(
                    test_script_path=test_case.test_path,
                    test_script_content=test_case.test_code,
                    required_files_for_context=sorted(list(required_files))
                )
            )

        return GenerateAndPrepareTestsOutput(prepared_tests=prepared_tests_list)

    def interpret_test_results(self, tool_input: InterpretTestResultsInput) -> InterpretTestResultsOutput:
        """
        Interprets raw results from a code execution tool to determine test success/failure.
        """
        successful_tests: List[InterpretedTestResult] = []
        failed_tests: List[InterpretedTestResult] = []

        for raw_result_dict in tool_input.executed_tests_results:
            # Ensure all necessary keys are present in the dictionary
            test_script_path = raw_result_dict.get("test_script_path", "Unknown Test Script")
            stdout = raw_result_dict.get("stdout", "")
            stderr = raw_result_dict.get("stderr", "")
            # process_success indicates if the script ran, not if tests passed.
            process_success = raw_result_dict.get("process_success", False)

            message = f"Stdout:\n{stdout}\nStderr:\n{stderr}"
            test_passed = False

            if not process_success: # Script execution failed entirely
                message = f"Test script execution failed.\n{message}"
                test_passed = False
            else:
                # Basic interpretation: unittest prints "OK" for success, "FAIL" or "ERROR" for failures in stderr.
                # A more robust solution would parse unittest output more precisely.
                if "FAIL" not in stderr.upper() and "ERROR" not in stderr.upper() and "OK" in stdout: # Simplistic check
                    # Or if unittest is configured to exit with 0 on success and non-zero on failure,
                    # the ADK exec tool's own success code might be usable if it reflects script's exit code.
                    # For now, relying on output parsing.
                    test_passed = True
                    # If stdout contains "OK" and stderr is empty or contains no FAIL/ERROR, it's likely a pass.
                    # Many test runners output to stderr for failures.
                    if stderr.strip() and not ("FAIL" in stderr.upper() or "ERROR" in stderr.upper()):
                        # Some runners might print summary to stderr even on success.
                        # If stderr has content but no explicit failure markers, it's ambiguous without more rules.
                        # Let's assume for now that any significant stderr without "FAIL" or "ERROR" but with "OK" in stdout is still a pass.
                        pass # Keep test_passed = True
                    elif stderr.strip(): # Has stderr content
                        # If "FAIL" or "ERROR" is not in stderr, but there's other output, it's safer to mark as failed.
                        # Or, if "OK" is not definitively in stdout.
                        if not ("OK" in stdout and not ("FAIL" in stderr.upper() or "ERROR" in stderr.upper())):
                            test_passed = False


            interpreted_result = InterpretedTestResult(
                success=test_passed,
                message=message.strip(),
                test_script_path=test_script_path,
                # original_code_path could be added if known from the context this method is called in
            )

            if test_passed:
                successful_tests.append(interpreted_result)
            else:
                failed_tests.append(interpreted_result)

        return InterpretTestResultsOutput(successful_tests=successful_tests, failed_tests=failed_tests)


# Example Usage
if __name__ == "__main__":
    dummy_llm = LLMInterface(api_key="dummy_testing_key") # Updated instantiation
    testing_tool = TestExecutionTool(llm_interface=dummy_llm)

    # Test generate_and_prepare_tests
    print("\\n--- Testing generate_and_prepare_tests ---")
    code_to_test_list = [
        CodeChange(path="utils.py", code="def add(a, b):\n    return a + b\ndef subtract(a,b):\n    return a-b"),
        CodeChange(path="main.py", code="from utils import add\nprint(add(1,2))")
    ]
    existing_files = {"config.py": "API_KEY = '123'"}

    prepare_input = GenerateAndPrepareTestsInput(
        code_to_test=code_to_test_list,
        existing_codebase_map=existing_files
    )
    try:
        prepare_output = testing_tool.generate_and_prepare_tests(prepare_input)
        print("Prepared Tests Output:")
        print(prepare_output.model_dump_json(indent=2))
        # Expected: LLM is called, and it returns one or more test scripts.
        # The dummy LLM returns one test for "utils.py".
        # required_files_for_context for that test should include "utils.py" (from code_to_test)
        # and potentially "main.py" if the LLM thought it was relevant (our dummy LLM doesn't make such considerations).
        # The current dummy LLM output has original_code_path: "utils.py", test_path: "test_utils.py".
        # So, required_files_for_context for this test should be ["main.py", "utils.py"].
    except ValueError as e:
        print(f"Error: {e}")

    # Test interpret_test_results
    print("\\n--- Testing interpret_test_results ---")
    # Simulated raw results from an ADK Code Execution tool
    raw_results_input = InterpretTestResultsInput(
        executed_tests_results=[
            { # Test 1: Success
                "test_script_path": "test_utils.py",
                "stdout": "..\n----------------------------------------------------------------------\nRan 2 tests in 0.001s\n\nOK\n",
                "stderr": "",
                "process_success": True # Script ran
            },
            { # Test 2: Failure
                "test_script_path": "test_main.py",
                "stdout": "F.\n----------------------------------------------------------------------\nRan 2 tests in 0.002s\n\nFAILED (failures=1)\n",
                "stderr": "======================================================================\nFAIL: test_something (test_main.TestMainApp)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"test_main.py\", line 10, in test_something\n    self.assertEqual(main_function(), 'expected_output')\nAssertionError: 'actual_output' != 'expected_output'\n",
                "process_success": True # Script ran
            },
            { # Test 3: Script execution error
                "test_script_path": "test_config.py",
                "stdout": "",
                "stderr": "ImportError: No module named 'non_existent_module'",
                "process_success": False # Script itself failed to run properly
            }
        ]
    )
    try:
        interpret_output = testing_tool.interpret_test_results(raw_results_input)
        print("Interpreted Test Results Output:")
        print(interpret_output.model_dump_json(indent=2))
        # Expected:
        # Successful: test_utils.py
        # Failed: test_main.py, test_config.py
    except ValueError as e:
        print(f"Error: {e}")
