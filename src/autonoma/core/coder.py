"""CoderAgent module for the Autonoma package."""

from typing import Optional, Protocol
# Updated model imports to reflect their new locations
from autonoma.models.agent import Agent
from autonoma.models.task import Task
from autonoma.models.code import GeneratedCode


class LLMInterfaceProtocol(Protocol):
    """Protocol for Language Model Interface."""
    def generate(self, user_prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 150) -> str:
        ...


class CoderAgent:
    """
    CoderAgent uses an LLM to generate and modify code based on tasks and test results.
    """

    def __init__(self, llm_interface: LLMInterfaceProtocol):
        """
        Initialize the CoderAgent.

        Args:
            llm_interface: A language model interface conforming to LLMInterfaceProtocol.
        """
        self.llm_interface: LLMInterfaceProtocol = llm_interface

    def generate_code(self, task: Task, agent: Agent) -> GeneratedCode:
        """
        Generates code to fulfill the given task's requirements.

        Args:
            task: The task detailing the code to be generated and relevant existing code.
            agent: The agent profile to guide the LLM's response style.

        Returns:
            A GeneratedCode object parsed from the LLM's JSON response.
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
        response: str = self.llm_interface.generate(user_prompt=user_prompt, system_prompt=system_prompt)
        return GeneratedCode.parse_raw(response)

    def modify_code_based_on_test(
        self, code: GeneratedCode, test: str, test_result: str, task: Task
    ) -> GeneratedCode:
        """
        Modifies existing code based on failing test results.

        Args:
            code: The current GeneratedCode object to be modified.
            test: The source code of the failing test.
            test_result: The output or error message from the failing test.
            task: The original task description, for context.

        Returns:
            A GeneratedCode object with proposed modifications, parsed from the LLM's JSON response.
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

        response: str = self.llm_interface.generate(user_prompt=user_prompt, system_prompt=system_prompt)
        return GeneratedCode.parse_raw(response)
