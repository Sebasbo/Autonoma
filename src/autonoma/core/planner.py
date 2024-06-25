"""PlannerAgent module for the Autonoma package."""

import json
from typing import List, Dict
from autonoma.models import Project, TaskType, CodeFile, PlanRequest


class PlannerAgent:
    """PlannerAgent for creating query plans."""

    def __init__(self, llm_interface):
        """
        Initialize the PlannerAgent.

        Args:
            llm_interface: An interface to the language model for generating plans.
        """
        self.llm_interface = llm_interface

    def create_query_plan(self, plan_request: PlanRequest) -> Project:
        """
        Create a query plan based on the given request.

        Args:
            plan_request: A PlanRequest object containing the query and codebase.

        Returns:
            A Project object containing the created query plan.
        """
        prompt = self._generate_prompt(plan_request)
        plan_dict = json.loads(self.llm_interface.generate(prompt))

        # Create a Project object
        project = Project(**plan_dict)

        # Validate and extract relevant code
        self._validate_and_extract_code(project, plan_request.code_base)

        return project

    def _generate_prompt(self, plan_request: PlanRequest) -> str:
        """
        Generate the prompt for the language model.

        Args:
            plan_request: A PlanRequest object containing the query and codebase.

        Returns:
            A string containing the generated prompt.
        """
        codebase_structure = json.dumps(
            {file.path: f"<code content of {file.path}>" for file in plan_request.code_base},
            indent=2,
        )

        return f"""
        You are an AI assistant specializing in software development and code modification. 
        Your task is to create a plan to address a query about modifying a specific codebase.

        Query: {plan_request.query}

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

    def _validate_and_extract_code(self, project: Project, codebase: List[CodeFile]):
        """
        Validate the project and extract relevant code for each task.

        Args:
            project: The Project object to validate and update.
            codebase: The list of CodeFile objects representing the codebase.
        """
        for agent in project.agents:
            for task in agent.tasks:
                if task.file_paths:
                    task.relevant_code = {
                        path: self._extract_code(codebase, path) for path in task.file_paths
                    }

    @staticmethod
    def _extract_code(codebase: List[CodeFile], path: str) -> str:
        """
        Extract code from the codebase for a given file path.

        Args:
            codebase: The list of CodeFile objects representing the codebase.
            path: The path of the file to extract code from.

        Returns:
            The content of the file if found, None otherwise.
        """
        for file in codebase:
            if file.path == path:
                return file.content
        return None

    def get_modified_files(self, project: Project) -> Dict[str, str]:
        """
        Get all modified files from the project.

        Args:
            project: The Project object to extract modified files from.

        Returns:
            A dictionary of modified file paths and their contents.
        """
        modified_files = {}
        for agent in project.agents:
            for task in agent.tasks:
                if task.task_type == TaskType.CODE_IMPLEMENTATION:
                    for file_path, code in task.relevant_code.items():
                        if code:  # Only include non-empty code
                            modified_files[file_path] = code
        return modified_files
