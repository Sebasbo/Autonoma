import json
from typing import List, Dict, Any, Optional

# --- ADK Imports (Placeholders - actual paths may vary) ---
# HYPOTHETICAL: Assuming these were found after exploration.
# In a real scenario, these would be validated by attempting actual imports.
try:
    from google_adk.workflows import SequentialAgent # HYPOTHETICAL Path
    from google_adk.tools.code_execution import CodeExecutionTool as AdkBuiltInCodeExecutionTool # HYPOTHETICAL Path and Class

    # HYPOTHETICAL: Define a Pydantic model for the ADK Code Execution tool's result if its structure is known/assumed
    from pydantic import BaseModel as AdkBaseModel
    class AdkCodeExecutionResult(AdkBaseModel): # HYPOTHETICAL Model
        success: bool # True if the command itself ran without crashing, not necessarily test pass
        stdout: str
        stderr: str
        # Assuming it might also return an exit code or specific error if the process failed
        exit_code: Optional[int] = None
        error_message: Optional[str] = None # For errors like "command not found"

except ImportError:
    print("Warning: Real google_adk components not found. Using placeholders.")
    class SequentialAgent: # Placeholder base class
        def __init__(self, *args, **kwargs):
            pass
        def run(self, *args, **kwargs):
            raise NotImplementedError("This is a placeholder SequentialAgent.")

    class AdkBuiltInCodeExecutionTool: # Placeholder for ADK's code executor
        def __init__(self, *args: Any, **kwargs: Any): # Placeholder init
            pass
        def execute(self, script_to_execute: str, files_in_context: Dict[str, str], command_args: Optional[List[str]] = None) -> AdkCodeExecutionResult: # Changed to direct type
            print(f"Placeholder AdkBuiltInCodeExecutionTool.execute called for {script_to_execute}")
            # Simulate a result structure
            return AdkCodeExecutionResult(success=True, stdout="Placeholder output", stderr="", exit_code=0)

    from pydantic import BaseModel as AdkBaseModel # Fallback for AdkCodeExecutionResult
    class AdkCodeExecutionResult(AdkBaseModel): # Fallback Model
        success: bool
        stdout: str
        stderr: str
        exit_code: Optional[int] = None
        error_message: Optional[str] = None


# --- Custom Tool Imports ---
from autonoma.adk_tools.planning_tool import PlanningTool, PlanningToolInput, PlanningToolOutput, LLMInterface as PlanningLLMInterface
from autonoma.adk_tools.coding_tool import CodeGenerationTool, GenerateInitialCodeInput, RefineCodeInput, LLMInterface as CodingLLMInterface
from autonoma.adk_tools.testing_tool import TestExecutionTool, GenerateAndPrepareTestsInput, InterpretTestResultsInput, PreparedTest, InterpretedTestResult, LLMInterface as TestingLLMInterface # Added PreparedTest

# --- Autonoma Model Imports ---
from autonoma.models.code import CodeFile # For initial_codebase
from autonoma.models.project import Project # Output of PlanningTool
from autonoma.models.task import Task, TaskType # From the Project plan
from autonoma.models.code import CodeChange, GeneratedCode # For code generation results (Corrected: was models.coder)
from autonoma.models.agent import Agent # Added for typing agent_plan

# --- Placeholder for LLMInterface (if a single type is used across tools) ---
# For now, tools define their own LLMInterface placeholders.
# In a real app, a single, consistent LLMInterface would be injected.
class GlobalLLMInterface(PlanningLLMInterface, CodingLLMInterface, TestingLLMInterface): # Bases now expect api_key in __init__
    def __init__(self, api_key: str = "dummy_global_key", model_name: str = "global_dummy_model", temperature: float = 0.1):
        # Explicitly call one of the parent's __init__ or handle params directly if logic differs.
        # Since parent placeholders don't use these params in generate, just storing them here is fine.
        # Or, choose one parent's __init__ to call, e.g., PlanningLLMInterface.
        # For simplicity, we'll assume this GlobalLLMInterface might have its own logic or can just store them.
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        # If super() was needed & MRO was complex: super(GlobalLLMInterface, self).__init__(api_key=api_key, model_name=model_name, temperature=temperature)
        # But given placeholders, direct assignment is simpler.

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        # This is a more generic placeholder.
        # Specific dummy responses would be needed for actual testing.
        print(f"GlobalLLMInterface.generate called. Prompt: {prompt[:100]}...")
        if "You are an AI assistant specializing in software development and code modification" in prompt: # Planning
            return json.dumps({
                "agents": [{
                    "name": "Code Implementer", "role": "...", "goal": "...",
                    "tasks": [{
                        "id": "task1", "description": "Implement feature X in file_a.py",
                        "task_type": "code_implementation", "status": "not_started",
                        "execution_type": "llm_call", "file_paths": ["file_a.py"],
                        "relevant_code": {"file_a.py": "print('initial content')"},
                        "prompt_llm": "Implement feature X..."
                    }]
                }]
            })
        elif "Write Python code to accomplish" in prompt: # Code Gen
            return json.dumps({"code_changes": [{"code": "print('generated code for feature X')", "path": "file_a.py"}]})
        elif "Modify the following Python code to pass the given test" in prompt: # Code Refine
             return json.dumps({"code_changes": [{"code": "print('refined code for feature X')", "path": "file_a.py"}]})
        elif "Generate unit tests to verify the correctness" in prompt: # Test Gen
            return json.dumps({
                "tests": [{
                    "test_code": "import unittest\nclass T(unittest.TestCase):\n def test_x(self):\n  self.assertTrue(True)\nif __name__ == '__main__': unittest.main()",
                    "test_path": "test_file_a.py",
                    "original_code_path": "file_a.py"
                }]
            })
        return json.dumps({})


# Removed AdkCodeExecutorToolPlaceholder as we now hypothetically use AdkBuiltInCodeExecutionTool

# --- Main Sequential Agent ---
MAX_REFINEMENT_ITERATIONS = 2

# HYPOTHETICAL: The real ADK SequentialAgent might require specific tools to be registered
# or passed in a certain way. This __init__ signature might need adjustment.

class MainSequentialAgent(SequentialAgent):  # type: ignore # Ignore if SequentialAgent is a placeholder
    """
    Orchestrates a sequence of planning, coding, and testing operations
    using ADK tools and custom Autonoma tools.
    """
    def __init__(self,
                 llm_interface: GlobalLLMInterface,
                 planning_tool: PlanningTool,
                 code_generation_tool: CodeGenerationTool,
                 testing_tool: TestExecutionTool,
                 code_executor_tool: AdkBuiltInCodeExecutionTool):
        """
        Initializes the MainSequentialAgent.

        Args:
            llm_interface: An LLM interface for tools that require direct LLM access.
            planning_tool: Tool for generating the initial project plan.
            code_generation_tool: Tool for generating and refining code.
            testing_tool: Tool for generating tests and interpreting results.
            code_executor_tool: ADK tool for executing code and tests.
        """
        super().__init__() # Assuming base class needs initialization
        self.llm_interface: GlobalLLMInterface = llm_interface

        self.planning_tool: PlanningTool = planning_tool
        self.code_generation_tool: CodeGenerationTool = code_generation_tool
        self.testing_tool: TestExecutionTool = testing_tool
        self.code_executor_tool: AdkBuiltInCodeExecutionTool = code_executor_tool

        self.current_codebase_state: Dict[str, str] = {}

    def _update_codebase_state(self, code_changes: List[CodeChange]) -> None:
        """Updates the internal codebase state with the latest code changes."""
        for change in code_changes:
            self.current_codebase_state[change.path] = change.code

    def run(self, query: str, initial_codebase: List[CodeFile]) -> Dict[str, Any]:
        """
        Main execution method for the sequential agent.
        Orchestrates planning, code generation, testing, and refinement.
        """
        print(f"--- MainSequentialAgent: Starting run for query: '{query}' ---")

        self.current_codebase_state = {cf.path: cf.content for cf in initial_codebase}

        final_results: Dict[str, Any] = {
            "query": query,
            "plan": None,
            "final_code_changes": [],
            "test_summary": [],
            "errors": []
        }

        # Step 1: Planning
        print("--- Step 1: Planning ---")
        planning_input: PlanningToolInput = PlanningToolInput(query=query, code_files=initial_codebase)
        try:
            plan_output: PlanningToolOutput = self.planning_tool.execute_planning(planning_input)
            project_plan: Project = plan_output.plan
            final_results["plan"] = project_plan.model_dump() # Use model_dump for Pydantic v2+
            print(f"Planning successful. Plan: {project_plan.model_dump_json(indent=2, exclude_none=True)}")
        except Exception as e:
            print(f"Error during planning: {e}")
            final_results["errors"].append(f"Planning failed: {str(e)}")
            return final_results # type: ignore # In case of error, type might not match full success

        # Step 2: Task Execution Loop
        print("\n--- Step 2: Task Execution ---")
        all_task_generated_code: List[CodeChange] = []

        agent_plan: Agent
        for agent_plan in project_plan.agents:
            task: Task
            for task in agent_plan.tasks:
                print(f"\nExecuting Task: {task.id} - {task.description}")
                if task.task_type == TaskType.CODE_IMPLEMENTATION:
                    current_task_code_changes: Optional[List[CodeChange]] = None
                    task_test_results_summary: List[Dict[str, Any]] = [] # Be more specific

                    relevant_code_for_task: Dict[str, str] = task.relevant_code.copy() if task.relevant_code else {}

                    path: str
                    for path in task.file_paths:
                        if path not in relevant_code_for_task:
                             relevant_code_for_task[path] = self.current_codebase_state.get(path, "")


                    # Initial Code Generation
                    print(f"  Generating initial code for task: {task.id}...")
                    gen_input: GenerateInitialCodeInput = GenerateInitialCodeInput(
                        task_description=task.description,
                        relevant_code=relevant_code_for_task
                    )
                    try:
                        generated_code_output: GeneratedCode = self.code_generation_tool.generate_initial_code(gen_input)
                        current_task_code_changes = generated_code_output.code_changes
                        if current_task_code_changes is not None: # Ensure it's not None before updating
                            self._update_codebase_state(current_task_code_changes)
                        print(f"  Initial code generated for {task.id}: {current_task_code_changes}")
                    except Exception as e:
                        print(f"  Error during initial code generation for task {task.id}: {e}")
                        final_results["errors"].append(f"Initial code gen failed for {task.id}: {str(e)}")
                        continue

                    if current_task_code_changes is None: # If generation failed and resulted in None
                        print(f"  Skipping test/refine for {task.id} due to prior generation failure or no changes.")
                        continue

                    # Test & Refine Loop
                    i: int
                    for i in range(MAX_REFINEMENT_ITERATIONS):
                        print(f"  Test & Refine Iteration {i + 1}/{MAX_REFINEMENT_ITERATIONS} for task {task.id}...")

                        print(f"    Generating tests...")
                        prepare_tests_input: GenerateAndPrepareTestsInput = GenerateAndPrepareTestsInput(
                            code_to_test=current_task_code_changes, # Should not be None here
                            existing_codebase_map=self.current_codebase_state
                        )
                        try:
                            # Assuming generate_and_prepare_tests returns GenerateAndPrepareTestsOutput
                            prepared_tests_output: GenerateAndPrepareTestsOutput = self.testing_tool.generate_and_prepare_tests(prepare_tests_input)
                            if not prepared_tests_output.prepared_tests:
                                print("    No tests generated. Assuming success for this iteration or task requires no tests.")
                                break
                        except Exception as e:
                            print(f"    Error generating tests: {e}")
                            final_results["errors"].append(f"Test generation failed for {task.id}: {str(e)}")
                            break

                        print(f"    Executing {len(prepared_tests_output.prepared_tests)} test(s)...")
                        raw_exec_results: List[Dict[str, Any]] = []
                        prep_test: PreparedTest
                        for prep_test in prepared_tests_output.prepared_tests:
                            current_exec_context: Dict[str, str] = self.current_codebase_state.copy()
                            current_exec_context[prep_test.test_script_path] = prep_test.test_script_content

                            change_obj: CodeChange # Type hint for loop variable
                            for change_obj in current_task_code_changes: # current_task_code_changes is List[CodeChange]
                                current_exec_context[change_obj.path] = change_obj.code

                            try:
                                adk_exec_result: AdkCodeExecutionResult = self.code_executor_tool.execute(
                                    script_to_execute=prep_test.test_script_path,
                                    files_in_context=current_exec_context,
                                    command_args=["python", prep_test.test_script_path]
                                )
                                adapted_result: Dict[str, Any] = {
                                    "test_script_path": prep_test.test_script_path,
                                    "stdout": adk_exec_result.stdout,
                                    "stderr": adk_exec_result.stderr,
                                    "process_success": adk_exec_result.success
                                }
                                if adk_exec_result.error_message or (adk_exec_result.exit_code is not None and adk_exec_result.exit_code != 0):
                                    if not adk_exec_result.success:
                                         adapted_result["process_success"] = False
                                raw_exec_results.append(adapted_result)
                            except Exception as adk_exec_e:
                                print(f"    ADK Code Execution tool failed: {adk_exec_e}")
                                raw_exec_results.append({
                                    "test_script_path": prep_test.test_script_path,
                                    "stdout": "",
                                    "stderr": f"ADK Code Execution tool error: {str(adk_exec_e)}",
                                    "process_success": False
                                })

                        print(f"    Interpreting test results...")
                        interpret_input: InterpretTestResultsInput = InterpretTestResultsInput(executed_tests_results=raw_exec_results)
                        try:
                            # Assuming interpret_test_results returns InterpretTestResultsOutput
                            interpreted_results_output: InterpretTestResultsOutput = self.testing_tool.interpret_test_results(interpret_input)
                            task_test_results_summary = [res.model_dump() for res in interpreted_results_output.failed_tests + interpreted_results_output.successful_tests]
                            print(f"    Test interpretation complete. Failures: {len(interpreted_results_output.failed_tests)}, Successes: {len(interpreted_results_output.successful_tests)}")
                        except Exception as e:
                            print(f"    Error interpreting test results: {e}")
                            final_results["errors"].append(f"Test interpretation failed for {task.id}: {str(e)}")
                            break

                        if not interpreted_results_output.failed_tests:
                            print(f"  All tests passed for task {task.id}. Moving to next task.")
                            break
                        else:
                            print(f"  {len(interpreted_results_output.failed_tests)} test(s) failed. Attempting refinement...")
                            feedback_str: str = "\n".join([
                                f"Test Script: {f.test_script_path}\nMessage: {f.message}" # f is InterpretedTestResult
                                for f in interpreted_results_output.failed_tests
                            ])
                            refine_input: RefineCodeInput = RefineCodeInput(
                                current_code=current_task_code_changes,
                                test_script="Multiple tests - see feedback.",
                                test_feedback=feedback_str,
                                original_task_description=task.description
                            )
                            try:
                                refined_code_output: GeneratedCode = self.code_generation_tool.refine_code_from_test_feedback(refine_input)
                                current_task_code_changes = refined_code_output.code_changes
                                if current_task_code_changes is not None: # Ensure not None before update
                                    self._update_codebase_state(current_task_code_changes)
                                print(f"  Code refined for task {task.id}: {current_task_code_changes}")
                            except Exception as e:
                                print(f"    Error during code refinement: {e}")
                                final_results["errors"].append(f"Code refinement failed for {task.id}: {str(e)}")
                                break
                    else:
                        print(f"  Max refinement iterations reached for task {task.id}. Using last generated code.")

                    if current_task_code_changes:
                        all_task_generated_code.extend(current_task_code_changes)
                    final_results["test_summary"].append({
                        "task_id": task.id,
                        "description": task.description,
                        "results": task_test_results_summary
                    })
                else:
                    print(f"  Skipping task {task.id} of type {task.task_type} (not code_implementation).")

        # Step 3: Aggregate and Return Results
        print("\n--- Step 3: Aggregation and Results ---")
        final_code_changes_map: Dict[str, CodeChange] = {}
        # Determine final code changes based on the accumulated `all_task_generated_code`
        # and the final `current_codebase_state`.
        # A file is considered changed if its path appears in any CodeChange object generated
        # during the tasks, and its final content in current_codebase_state is different
        # from its initial state (if it existed) or it's a new file.

        initial_code_content_map: Dict[str, str] = {cf.path: cf.content for cf in initial_codebase}

        # Paths that were subject to any code generation attempt
        touched_paths: set[str] = {cc.path for cc in all_task_generated_code}

        for path, current_content in self.current_codebase_state.items():
            initial_content = initial_code_content_map.get(path)
            # Include if:
            # 1. It's a new file that was touched by a task.
            # 2. It's an existing file whose content has changed.
            # 3. It was touched (e.g. an attempt was made to modify it) even if content didn't change (edge case, might include unchanged files if logic isn't precise)
            # For simplicity here, if a path was part of any code_change operation, and its current content
            # is different from initial (or it's new), include it.
            if path in touched_paths and (initial_content is None or current_content != initial_content):
                final_code_changes_map[path] = CodeChange(path=path, code=current_content)
            elif initial_content is None and path in touched_paths : # New file explicitly created
                 final_code_changes_map[path] = CodeChange(path=path, code=current_content)


        final_results["final_code_changes"] = [cc.model_dump() for cc in final_code_changes_map.values()]
        print("--- MainSequentialAgent: Run finished ---")
        return final_results


# --- Main Execution Block for Rudimentary Testing ---
# Define a single fallback executor class for the test block
class TestPlaceholderFallbackAdkCodeExecutor:
    def execute(self, script_to_execute: str, files_in_context: Dict[str, str], command_args: Optional[List[str]] = None) -> AdkCodeExecutionResult:
        print(f"TestPlaceholderFallbackAdkCodeExecutor.execute for {script_to_execute} with args {command_args}")
        # Provide a more detailed mock response if needed for testing specific scenarios
        if "test_file_a.py" in script_to_execute: # Example: simulate test output
            return AdkCodeExecutionResult(success=True, stdout=".", stderr="", exit_code=0)
        return AdkCodeExecutionResult(success=True, stdout="Test Fallback output", stderr="", exit_code=0)

if __name__ == "__main__":
    print("--- Starting MainSequentialAgent Test ---")

    mock_llm: GlobalLLMInterface = GlobalLLMInterface(api_key="dummy_sequential_agent_key", model_name="sequential_model", temperature=0.2)

    planning_tool_inst: PlanningTool = PlanningTool(llm_interface=mock_llm)
    coding_tool_inst: CodeGenerationTool = CodeGenerationTool(llm_interface=mock_llm)
    testing_tool_inst: TestExecutionTool = TestExecutionTool(llm_interface=mock_llm)

    code_exec_tool_inst: AdkBuiltInCodeExecutionTool # Type hint for clarity
    try:
        # Check if the 'real' AdkBuiltInCodeExecutionTool is not just the placeholder definition
        if "AdkBuiltInCodeExecutionTool" in globals() and \
           not type(AdkBuiltInCodeExecutionTool) == type(SequentialAgent): # Heuristic: if it's not the placeholder class itself
             print("Attempting to use 'real' AdkBuiltInCodeExecutionTool for test.")
             code_exec_tool_inst = AdkBuiltInCodeExecutionTool()
        else:
            print("Using placeholder AdkBuiltInCodeExecutionTool (TestPlaceholderFallback) for test.")
            code_exec_tool_inst = TestPlaceholderFallbackAdkCodeExecutor() # type: ignore # Assigning specific test placeholder
    except Exception as e:
        print(f"Could not instantiate AdkBuiltInCodeExecutionTool, using TestPlaceholderFallback: {e}")
        code_exec_tool_inst = TestPlaceholderFallbackAdkCodeExecutor() # type: ignore

    # 2. Instantiate MainSequentialAgent
    try:
        main_agent = MainSequentialAgent(
            llm_interface=mock_llm,
            planning_tool=planning_tool_inst,
            code_generation_tool=coding_tool_inst,
            testing_tool=testing_tool_inst,
            code_executor_tool=code_exec_tool_inst # Pass the (potentially real) ADK tool
        )
        print("MainSequentialAgent instantiated successfully (potentially with real ADK base class).")

        # 3. Sample query and initial codebase for a very simple test
        # To truly test ADK integration, we'd need a minimal `run` or specific method call.
        # For now, just instantiation is a good first step.
        # If we want to test a part of the run:
        # print("\n--- Testing a simplified planning step ---")
        # sample_query_simple = "Create a plan for a hello world function."
        # sample_codebase_simple = [CodeFile(path="dummy.py", content="# A dummy file")]
        # planning_input_simple = PlanningToolInput(query=sample_query_simple, code_files=sample_codebase_simple)
        # plan_output_simple = main_agent.planning_tool.execute_planning(planning_input_simple)
        # print(f"Simplified planning output: {plan_output_simple.plan.model_dump_json(indent=2)}")

        # Full run for structural check:
        sample_query = "Refactor file_a.py to include a new function 'greet' and add tests for it."
        sample_codebase = [
            CodeFile(path="file_a.py", content="print('Hello from file_a.py')"),
            CodeFile(path="requirements.txt", content="requests==2.25.1")
        ]
        results = main_agent.run(query=sample_query, initial_codebase=sample_codebase)
        print("\n--- Agent Run Results (with potentially real ADK components) ---")
        print(json.dumps(results, indent=2, default=str))


    except Exception as e:
        print(f"Error during MainSequentialAgent instantiation or simplified run: {e}")
        import traceback
        traceback.print_exc()

    # The following block was duplicated and caused a syntax error.
    # Removing the duplicated part. The original test block above is correct.

    print("\n--- MainSequentialAgent Test Finished ---")
