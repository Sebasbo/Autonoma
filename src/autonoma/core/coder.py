"""CoderAgent module for the Autonoma package."""

from typing import Any
from autonoma.models import Agent, Task, GeneratedCode


class CoderAgent:
    """
    CoderAgent for generating and modifying code.
    """

    def __init__(self, llm_interface: Any):
        """
        Initialize the CoderAgent.

        Args:
            llm_interface: An interface to the language model for generating responses.
        """
        self.llm_interface = llm_interface

    def generate_code(self, task: Task, agent: Agent) -> GeneratedCode:
        """
        Generate code based on the given task and existing code.

        Args:
            task: The task containing code modification instructions.
            agent: The agent requesting the code generation.

        Returns:
            A GeneratedCode object containing the generated code changes.
        """
        user_prompt = f"""
        Write Python code to accomplish the following task:
        {task.description}
        Return only the code, without any explanations.
        Use JSON return format:
        {{
            "code_changes": [
                {{"code": "code without explanations", "path": "path of the code"}}
            ]
        }}
        Changes need to be made on the following code:
        {task.relevant_code}
        """

        system_prompt = f"""
        Act as the following agent:
        {agent.json()}
        """
        response = self.llm_interface.generate(user_prompt=user_prompt, system_prompt=system_prompt)
        return GeneratedCode.parse_raw(response)

    def modify_code_based_on_test(
        self, code: GeneratedCode, test: str, test_result: str, task: Task
    ) -> GeneratedCode:
        """
        Modify code based on test results.

        Args:
            code: The current code represented as a GeneratedCode object.
            test: The test code that failed.
            test_result: The result of the failed test.
            task: The original task containing the description.

        Returns:
            A GeneratedCode object containing the modified code changes.
        """
        user_prompt = f"""
        Modify the following Python code to pass the given test:

        Current code:
        {code.json()}

        Test code:
        {test}

        Test result:
        {test_result}

        Task Description:
        {task.description}

        Analyze the test result and modify the code to make it pass the test.
        Return only the modified code, without any explanations.
        Use JSON return format:
        {{
            "code_changes": [
                {{"code": "modified code without explanations", "path": "path to the code"}}
            ]
        }}
        """

        system_prompt = """
        You are an expert Python developer tasked with modifying code to pass tests.
        Focus on making minimal necessary changes to fix the failing tests.
        Ensure your modifications maintain the overall structure and intent of the original code.
        If the test is already passing, return the original code unchanged.
        Ensure you mock all the imports.
        """

        response = self.llm_interface.generate(user_prompt=user_prompt, system_prompt=system_prompt)
        return GeneratedCode.parse_raw(response)
