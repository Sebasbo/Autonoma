import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field

# Assuming ADK Function Tool base class will be available through an import
# from adk.tool_registry import FunctionTool

# Import necessary models from autonoma.models
from autonoma.models.code import CodeFile # Updated: Was models.agent
from autonoma.models.project import Project # ProjectModel
from autonoma.models.task import Task, TaskType # Task model for plan structure

# Placeholder for LLMInterface - replace with actual interface when available
class LLMInterface:
    def __init__(self, api_key: str = "dummy_key", model_name: str = "dummy_model", temperature: float = 0.0): # Added params
        self.api_key = api_key # Not used by this placeholder's generate
        self.model_name = model_name
        self.temperature = temperature

    def generate(self, prompt: str) -> str:
        # This is a placeholder. In a real scenario, this would call the LLM.
        # For now, it might return a dummy JSON string for testing.
        dummy_plan_dict = {
          "agents": [
            {
              "name": "Code Implementer",
              "role": "Agent's specialized role",
              "goal": "The goal of this agent",
              "tasks": [
                {
                  "id": "task_123",
                  "description": "Implement feature X",
                  "task_type": "code_implementation",
                  "status": "not_started",
                  "execution_type": "llm_call",
                  "file_paths": ["src/main.py"],
                  "estimated_complexity": "Medium",
                  "cmd": None,
                  "prompt_llm": "Implement feature X in src/main.py"
                }
              ]
            }
          ]
        }
        return json.dumps(dummy_plan_dict)

# Input Schema
class PlanningToolInput(BaseModel):
    query: str
    code_files: List[CodeFile] = Field(description="List of code files (path and content) relevant to the query.")

# Output Schema
class PlanningToolOutput(BaseModel):
    plan: Project = Field(description="The generated project plan.")

# This would be the base class from ADK, e.g. @FunctionTool.from_defaults(...)
# For now, defining it as a simple class.
class PlanningTool: # Potentially: PlanningTool(FunctionTool):
    def __init__(self, llm_interface: LLMInterface):
        """
        Initialize the PlanningTool.

        Args:
            llm_interface: An interface to the language model for generating plans.
        """
        self.llm_interface = llm_interface

    def _generate_prompt_string(self, query: str, code_files: List[CodeFile]) -> str:
        """
        Generate the prompt string for the language model.
        Adapted from PlannerAgent._generate_prompt.
        """
        codebase_structure = json.dumps(
            {file.path: f"<code content of {file.path}>" for file in code_files},
            indent=2,
        )

        # This prompt is taken directly from autonoma.core.planner.PlannerAgent
        return f"""
        You are an AI assistant specializing in software development and code modification.
        Your task is to create a plan to address a query about modifying a specific codebase.

        Query: {query}

        Codebase structure:
        {codebase_structure}

        Create a plan to address the query. The plan should consist of a series of code modification tasks that can be executed sequentially.
        For each task, specify only the files that are absolutely necessary for that specific modification.

        Provide your response as a JSON object with the following structure:

        {{
          "agents": [
            {{
              "name": "Code Implementer",
              "role": "Agent's specialized role",
              "goal": "The goal of this agent",
              "tasks": [
                {{
                  "id": "unique_task_id",
                  "description": "Short task description",
                  "task_type": "code_implementation or documentation",
                  "status": "not_started",
                  "execution_type": "llm_call or code_execution",
                  "file_paths": ["List of file paths needed for this tasks"],
                  "estimated_complexity": "Low/Medium/High",
                  "cmd": "Command to execute the code if code_execution, or null",
                  "prompt_llm": "The prompt for the LLM if llm_call, or null"
                }},
                ...
              ]
            }}
          ]
        }}

        Ensure that:
        1. Tasks flow logically from one to the next, addressing all aspects of the query.
        2. Each task includes specific instructions for code modification.
        3. Only include file paths that are absolutely necessary for each task.
        4. If a new file needs to be created, include its intended path in the file_paths list.

        Analyze the query and codebase, then provide the JSON output as specified above.

        Don't include a tester agent, as testing will be done in a separate query.
        Don't include analysis tasks only, always refactor something.
        Don't use a file in multiple tasks, be extremely critical on the amount of tasks, the fewer tasks the better.
        Only use a file once over all the tasks.
        """

    def _validate_and_populate_relevant_code(self, project: Project, code_files: List[CodeFile]):
        """
        Validate the project and populate relevant_code for each task.
        Adapted from PlannerAgent._validate_and_extract_code.
        """
        code_map = {file.path: file.content for file in code_files}
        for agent in project.agents:
            for task in agent.tasks:
                if task.file_paths:
                    task.relevant_code = {} # Initialize as dict
                    for path in task.file_paths:
                        if path in code_map:
                            task.relevant_code[path] = code_map[path]
                        else:
                            # Path specified in plan but not found in input code_files
                            # This could be a new file, so initialize with empty content or handle as error
                            task.relevant_code[path] = "" # Assuming new file will have empty content initially

    # This would be the method ADK calls, decorated with @<tool_name>.run
    def execute_planning(self, tool_input: PlanningToolInput) -> PlanningToolOutput:
        """
        Executes the planning process.

        Args:
            tool_input: The input for the planning tool, containing query and code files.

        Returns:
            A PlanningToolOutput object containing the generated plan.
        """
        prompt = self._generate_prompt_string(tool_input.query, tool_input.code_files)

        # Get plan JSON from LLM
        raw_plan_output = self.llm_interface.generate(prompt)

        try:
            plan_dict = json.loads(raw_plan_output)
        except json.JSONDecodeError as e:
            # Handle JSON parsing errors, maybe raise a specific exception or return an error state
            raise ValueError(f"Failed to parse LLM output as JSON: {e}")

        # Parse JSON into ProjectModel (autonoma.models.project.Project)
        # Pydantic will validate the structure based on Project, Agent, and Task models
        try:
            # Type hint for plan_dict, which is the result of json.loads
            plan_dict_typed: Dict[str, Any] = plan_dict
            project_plan = Project(**plan_dict_typed)
        except Exception as e: # Catch Pydantic validation errors or other issues
            raise ValueError(f"Failed to validate plan against Project model: {e}")

        # Populate relevant_code in tasks
        self._validate_and_populate_relevant_code(project_plan, tool_input.code_files)

        return PlanningToolOutput(plan=project_plan)

# Example Usage (for testing purposes, would be removed or in a test file)
if __name__ == "__main__":
    # Dummy LLM interface
    dummy_llm = LLMInterface(api_key="dummy_planning_key") # Updated instantiation

    # Create the tool instance
    planning_tool = PlanningTool(llm_interface=dummy_llm)

    # Example input
    example_code_files = [
        CodeFile(path="src/main.py", content="def hello():\n  print('Hello')"),
        CodeFile(path="utils/helper.py", content="def assist():\n  pass")
    ]
    example_query = "Refactor the hello function in src/main.py to return 'Hello World'"

    tool_input_data = PlanningToolInput(query=example_query, code_files=example_code_files)

    # Execute the tool
    try:
        output = planning_tool.execute_planning(tool_input_data)
        print("Generated Plan:")
        print(output.plan.model_dump_json(indent=2))
    except ValueError as e:
        print(f"Error during planning: {e}")

    # Example with a new file in plan
    # This requires the dummy LLM to actually return a plan that includes a new file.
    # For now, the dummy LLM returns a static plan.
    # A more sophisticated dummy LLM would be needed for this test case.

    print("\\nTest with query for new file (relies on LLM providing such a plan):")
    example_query_new_file = "Create a new file src/app.py with a main function"
    tool_input_new_file = PlanningToolInput(query=example_query_new_file, code_files=example_code_files)
    try:
        output_new_file = planning_tool.execute_planning(tool_input_new_file)
        print("Generated Plan (for new file):")
        print(output_new_file.plan.model_dump_json(indent=2))
    except ValueError as e:
        print(f"Error during planning for new file: {e}")

    # Test case: What if LLM returns a file_path not in code_files?
    # The _validate_and_populate_relevant_code should handle this by setting empty content.
    # This also depends on the dummy LLM.
    # If the dummy LLM in LLMInterface is modified to return a plan like:
    # { "agents": [{ "name": "Code Implementer", "role": "...", "goal": "...", "tasks": [
    #   { "id": "task_new", "description": "Create new_file.py", "task_type": "code_implementation",
    #     "status": "not_started", "execution_type": "llm_call", "file_paths": ["new_file.py"], ...} # type: ignore
    # ]}]}
    # Then the relevant_code for "new_file.py" should be ""

    print("\\nTest with LLM plan for a non-existent file (relies on LLM providing such a plan):")
    # To properly test this, the dummy LLMInterface would need to be configured to return a plan
    # that references a file not in the input `code_files`.
    # For instance, if `tool_input_data` (with src/main.py, utils/helper.py) is used,
    # and the dummy LLM returns a plan asking to modify `src/non_existent.py`.
    # The current dummy LLM always returns a plan for `src/main.py`.
    # This test case highlights the dependency on LLM behavior.
    # A more robust test setup would involve mocking LLMInterface.generate to control its output.

    # Example: if dummy_llm.generate could be made to return this for the next call:
    # json.dumps({ "agents": [{ "name": "Code Implementer", "role": "...", "goal": "...", "tasks": [
    #   { "id": "task_new", "description": "Create new_file.py", "task_type": "code_implementation",
    #     "status": "not_started", "execution_type": "llm_call", "file_paths": ["new_file.py"],
    #     "estimated_complexity": "Low", "prompt_llm": "Create content for new_file.py"}
    # ]}]})
    # Then the following call would demonstrate population of relevant_code for new_file.py
    # tool_input_for_new_file_scenario = PlanningToolInput(query="Create new_file.py", code_files=[])
    # output_for_new_file = planning_tool.execute_planning(tool_input_for_new_file_scenario)
    # print(output_for_new_file.plan.model_dump_json(indent=2))
    # Expected: ... "relevant_code": {"new_file.py": ""} ...
