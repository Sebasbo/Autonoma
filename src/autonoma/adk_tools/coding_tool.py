import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field

# Assuming ADK Function Tool base class will be available
# from adk.tool_registry import FunctionTool

# Import necessary models
from autonoma.models.code import CodeChange, GeneratedCode # Updated: Was models.coder

# Placeholder for LLMInterface - replace with actual interface
class LLMInterface:
    def __init__(self, api_key: str = "dummy_key", model_name: str = "dummy_model", temperature: float = 0.0): # Added params
        self.api_key = api_key # Not used by this placeholder's generate
        self.model_name = model_name
        self.temperature = temperature

    def generate(self, user_prompt: str, system_prompt: str) -> str:
        # This is a placeholder. In a real scenario, this would call the LLM.
        # For now, it might return a dummy JSON string for testing.
        # This dummy response needs to be tailored to the expected output format.
        print(f"---- LLMInterface.generate called ----")
        print(f"System Prompt: {system_prompt[:100]}...")
        print(f"User Prompt: {user_prompt[:100]}...")
        print(f"---- End LLMInterface.generate ----")

        # Example dummy response for generate_initial_code
        if "Write Python code to accomplish" in user_prompt:
            dummy_response = {
                "code_changes": [
                    {"code": "def hello_world():\n    print('Hello, world!')", "path": "src/example.py"}
                ]
            }
        # Example dummy response for refine_code
        elif "Modify the following Python code to pass the given test" in user_prompt:
            dummy_response = {
                "code_changes": [
                    {"code": "def hello_world():\n    # Refined code\n    print('Hello, refined world!')", "path": "src/example.py"}
                ]
            }
        else:
            dummy_response = {"code_changes": []}

        return json.dumps(dummy_response)

# Input Schemas
class GenerateInitialCodeInput(BaseModel):
    task_description: str = Field(description="Detailed description of the coding task.")
    relevant_code: Dict[str, str] = Field(description="Dictionary of relevant file paths to their content.")
    # agent_context might be too broad or might be passed differently in ADK.
    # For now, using a simple dict. Could be a Pydantic model if structure is known.
    # Based on CoderAgent, it seems like the 'agent' (role, goal) is part of the system prompt.
    # We might not need a full 'agent_context' if the system prompt is constructed within the tool.
    # Let's assume for now the tool itself embodies the agent's role for the system prompt.
    # If specific agent details are needed from the caller, this can be adjusted.


class RefineCodeInput(BaseModel):
    current_code: List[CodeChange] = Field(description="List of current code changes to be refined.")
    test_script: str = Field(description="The test script that was executed.")
    test_feedback: str = Field(description="The feedback or results from the test execution (e.g., error messages).")
    original_task_description: str = Field(description="The original task description that led to the current_code.")

# Output Schemas (using GeneratedCode directly as it matches the structure)
# class GenerateInitialCodeOutput(BaseModel):
#     generated_code: GeneratedCode
#
# class RefineCodeOutput(BaseModel):
#     refined_code: GeneratedCode
# Using GeneratedCode directly for return type hinting.

# This would be the base class from ADK, e.g. @FunctionTool.from_defaults(...)
class CodeGenerationTool: # Potentially: CodeGenerationTool(FunctionTool):
    def __init__(self, llm_interface: LLMInterface):
        """
        Initialize the CodeGenerationTool.

        Args:
            llm_interface: An interface to the language model.
        """
        self.llm_interface = llm_interface

    def _construct_system_prompt_for_generation(self) -> str:
        # Simplified system prompt, assuming the tool itself has a defined role.
        # If more dynamic agent context is needed, it should be passed in.
        # This is adapted from CoderAgent's system_prompt for generate_code.
        # We'll make it generic for the tool.
        return """
        You are an expert AI programmer. Your task is to write clean, efficient, and correct code
        based on the user's requirements. Ensure the code is well-commented and follows best practices.
        Return the output in the specified JSON format.
        """

    def _construct_system_prompt_for_refinement(self) -> str:
        # Adapted from CoderAgent's system_prompt for modify_code_based_on_test.
        return """
        You are an expert Python developer tasked with modifying code to pass tests.
        Focus on making minimal necessary changes to fix the failing tests.
        Ensure your modifications maintain the overall structure and intent of the original code.
        If the test is already passing, return the original code unchanged.
        Ensure you mock all the imports if necessary for the context.
        Return the output in the specified JSON format.
        """

    # This would be a method ADK calls, e.g. @generate_initial_code_tool.run
    def generate_initial_code(self, tool_input: GenerateInitialCodeInput) -> GeneratedCode:
        """
        Generates initial code based on a task description and relevant code.
        Adapts logic from CoderAgent.generate_code.
        """
        user_prompt = f"""
        Write Python code to accomplish the following task:
        {tool_input.task_description}

        The following code snippets are provided as context. You may need to modify them or use them as reference:
        {json.dumps(tool_input.relevant_code, indent=2)}

        Return only the code, without any explanations.
        Use JSON return format:
        {{
            "code_changes": [
                {{"code": "full code content for the file", "path": "path/to/file.py"}}
            ]
        }}
        If you are modifying an existing file, provide the complete new content for that file.
        If you are creating a new file, provide its full content.
        Ensure each entry in "code_changes" represents a complete file's content.
        """

        system_prompt = self._construct_system_prompt_for_generation()

        raw_llm_response = self.llm_interface.generate(user_prompt=user_prompt, system_prompt=system_prompt)

        try:
            # GeneratedCode.parse_raw expects a JSON string
            return GeneratedCode.model_validate_json(raw_llm_response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM output as JSON: {e}. Response: {raw_llm_response}")
        except Exception as e: # Catch Pydantic validation errors
            raise ValueError(f"Failed to validate LLM output against GeneratedCode model: {e}. Response: {raw_llm_response}")

    # This would be another method ADK calls, e.g. @refine_code_tool.run
    def refine_code_from_test_feedback(self, tool_input: RefineCodeInput) -> GeneratedCode:
        """
        Refines existing code based on test feedback.
        Adapts logic from CoderAgent.modify_code_based_on_test.
        """
        # Convert List[CodeChange] to a more readable format for the prompt
        current_code_str = json.dumps([cc.model_dump() for cc in tool_input.current_code], indent=2)

        user_prompt = f"""
        Modify the following Python code to pass the given test:

        Current code (as a list of file changes):
        {current_code_str}

        Test script/description:
        {tool_input.test_script}

        Test result/feedback:
        {tool_input.test_feedback}

        Original Task Description:
        {tool_input.original_task_description}

        Analyze the test result and modify the code to make it pass the test.
        Return only the modified code, without any explanations.
        Use JSON return format:
        {{
            "code_changes": [
                {{"code": "complete modified code content for the file", "path": "path/to/file.py"}}
            ]
        }}
        Ensure each entry in "code_changes" represents a complete file's content.
        If a file from the original code is not modified, you can omit it from the response
        or include it with its original code. For clarity, prefer to only include changed files.
        """

        system_prompt = self._construct_system_prompt_for_refinement()

        raw_llm_response = self.llm_interface.generate(user_prompt=user_prompt, system_prompt=system_prompt)

        try:
            return GeneratedCode.model_validate_json(raw_llm_response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM output as JSON: {e}. Response: {raw_llm_response}")
        except Exception as e: # Catch Pydantic validation errors
            raise ValueError(f"Failed to validate LLM output against GeneratedCode model: {e}. Response: {raw_llm_response}")


# Example Usage (for testing purposes)
if __name__ == "__main__":
    dummy_llm = LLMInterface(api_key="dummy_coding_key") # Updated instantiation
    coding_tool = CodeGenerationTool(llm_interface=dummy_llm)

    # Test generate_initial_code
    print("\\n--- Testing generate_initial_code ---")
    initial_code_input = GenerateInitialCodeInput(
        task_description="Create a Python function in a new file 'utils.py' that adds two numbers.",
        relevant_code={"main.py": "print('hello')"} # Existing code context
    )
    try:
        initial_output = coding_tool.generate_initial_code(initial_code_input)
        print("Generated Code Output:")
        # .model_dump_json() is the Pydantic v2 way
        print(initial_output.model_dump_json(indent=2))
    except ValueError as e:
        print(f"Error: {e}")

    # Test refine_code_from_test_feedback
    print("\\n--- Testing refine_code_from_test_feedback ---")
    # Assume initial_output from above is what we're refining, or define a new one
    current_code_changes = [
        CodeChange(path="src/example.py", code="def hello_world():\n    print('Hello, world!')")
    ]

    refine_input = RefineCodeInput(
        current_code=current_code_changes,
        test_script="assert hello_world() == 'Hello, refined world!'",
        test_feedback="AssertionError: 'Hello, world!' != 'Hello, refined world!'",
        original_task_description="Create a function that prints a greeting."
    )
    try:
        refined_output = coding_tool.refine_code_from_test_feedback(refine_input)
        print("Refined Code Output:")
        print(refined_output.model_dump_json(indent=2))
    except ValueError as e:
        print(f"Error: {e}")

    # Example with slightly different dummy response for generate_initial_code
    # To ensure the dummy LLM can be flexible if needed for testing various scenarios
    class FlexibleLLMInterface(LLMInterface): # Inherits updated __init__ from placeholder LLMInterface
        def generate(self, user_prompt: str, system_prompt: str) -> str:
            print(f"---- FlexibleLLMInterface.generate called ----")
            # Accessing model_name and temperature to show they are available, though not used by mock logic
            print(f"---- Using model: {self.model_name}, temp: {self.temperature} ----")
            if "adds two numbers" in user_prompt : # From initial_code_input
                 response = {
                    "code_changes": [
                        {"code": "def add(a, b):\n    return a + b", "path": "utils.py"}
                    ]
                }
            elif "original_task_description" in user_prompt: # From refine_input
                 response = {
                    "code_changes": [
                        {"code": "def hello_world():\n    return 'Hello, refined world!'", "path": "src/example.py"}
                    ]
                }
            else:
                response = {"code_changes": []}
            return json.dumps(response)

    print("\\n--- Testing with FlexibleLLMInterface ---")
    flexible_llm = FlexibleLLMInterface(api_key="dummy_flexible_key", model_name="gpt-flex", temperature=0.5) # Updated instantiation
    coding_tool_flexible = CodeGenerationTool(llm_interface=flexible_llm)

    try:
        initial_output_flexible = coding_tool_flexible.generate_initial_code(initial_code_input)
        print("Generated Code Output (Flexible LLM):")
        print(initial_output_flexible.model_dump_json(indent=2))

        # Use the output from the flexible LLM for refinement input
        refine_input_flexible = RefineCodeInput(
            current_code=initial_output_flexible.code_changes, # Using actual output
            test_script="assert add(1, 2) == 4", # A failing test for the add function
            test_feedback="AssertionError: 3 != 4",
            original_task_description="Create a Python function that adds two numbers."
        )
        # Need to adjust FlexibleLLMInterface to handle this new refinement task
        # For simplicity, let's assume it would return a fix for `add`
        # (This part highlights the complexity of good dummy/mock LLMs for testing)
        # For now, the FlexibleLLMInterface will not have a specific rule for this refine_input_flexible
        # and might return an empty list or a default response.

        # To make this test more meaningful, we'd update FlexibleLLMInterface or use a more specific mock
        # For example, if FlexibleLLMInterface was updated to:
        # elif "assert add(1, 2) == 4" in user_prompt:
        #     response = {"code_changes": [{"code": "def add(a, b):\n    # Fixed to meet test\n    if a==1 and b==2: return 4\n    return a + b", "path": "utils.py"}]}

        refined_output_flexible = coding_tool_flexible.refine_code_from_test_feedback(refine_input_flexible)
        print("Refined Code Output (Flexible LLM):")
        print(refined_output_flexible.model_dump_json(indent=2))


    except ValueError as e:
        print(f"Error (Flexible LLM): {e}")
