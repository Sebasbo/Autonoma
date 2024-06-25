"""Core agent module for the Autonoma package."""

from typing import List, Any
from autonoma.models import (
    Project,
    Agent,
    Task,
    TaskType,
    CodeFile,
    ProjectResult,
    AgentResult,
    TaskResult,
    FinalResult,
    PlanRequest,
)
from .planner import PlannerAgent
from .coder import CoderAgent
from .tester import Tester
from autonoma.utils.file_operations import store_results, get_modified_files, get_new_files
from autonoma.utils.reflection import Reflector


class AutonomaAgent:
    """
    Main agent class for the Autonoma system.

    This class orchestrates the entire process of code modification and analysis.
    """

    def __init__(self, llm_interface: Any):
        """
        Initialize the AutonomaAgent.

        Args:
            llm_interface: An interface to the language model for generating responses.
        """
        self.llm_interface = llm_interface
        self.planner_agent = PlannerAgent(llm_interface)
        self.coder_agent = CoderAgent(llm_interface)
        self.tester = Tester(llm_interface)
        self.reflector = Reflector()

    def process_query(self, query: str, code_base: List[CodeFile]) -> FinalResult:
        """
        Process a query against the given codebase.

        Args:
            query: The query to process.
            code_base: The codebase to process the query against.

        Returns:
            A FinalResult object containing the results of the query processing.
        """
        self.reflector.reflect(f"Processing query: {query}")

        project = self.planner_agent.create_query_plan(
            PlanRequest(query=query, code_base=code_base)
        )
        project_result = self.execute_project(project, code_base)
        final_result = self.compile_results(project_result)
        store_results(final_result)

        return final_result

    def execute_project(self, project: Project, code_base: List[CodeFile]) -> ProjectResult:
        """
        Execute a project against the given codebase.

        Args:
            project: The project to execute.
            code_base: The codebase to execute the project against.

        Returns:
            A ProjectResult object containing the results of the project execution.
        """
        agent_results: List[AgentResult] = []

        for agent in project.agents:
            agent_result = self.execute_agent_tasks(agent, code_base)
            agent_results.append(agent_result)

        modified_files = get_modified_files(agent_results)

        return ProjectResult(
            project=project,
            agent_results=agent_results,
            modified_files=modified_files,
            new_files=get_new_files(agent_results),
            unchanged_files={
                file.path: file.content for file in code_base if file.path not in modified_files
            },
            thought_process=self.reflector.thought_process,
        )

    def execute_agent_tasks(self, agent: Agent, codebase: List[CodeFile]) -> AgentResult:
        """
        Execute the tasks of a single agent.

        Args:
            agent: The agent whose tasks are to be executed.
            codebase: The codebase to execute the tasks against.

        Returns:
            An AgentResult object containing the results of the agent's task executions.
        """
        self.reflector.reflect(f"Executing tasks for agent: {agent.name}")
        task_results: List[TaskResult] = []

        for task in agent.tasks:
            task_result = self.execute_task(task, agent, codebase)
            task_results.append(task_result)

        return AgentResult(agent_name=agent.name, task_results=task_results)

    def execute_task(self, task: Task, agent: Agent, codebase: List[CodeFile]) -> TaskResult:
        """
        Execute a single task.

        Args:
            task: The task to execute.
            agent: The agent executing the task.
            codebase: The codebase to execute the task against.

        Returns:
            A TaskResult object containing the results of the task execution.
        """
        self.reflector.reflect(f"Executing task: {task.description}")
        if task.task_type == TaskType.CODE_IMPLEMENTATION:
            return self.modify_code(task, agent, codebase)
        else:
            return self.execute_llm_task(task)

    def modify_code(self, task: Task, agent: Agent, codebase: List[CodeFile]) -> TaskResult:
        """
        Modify code based on the given task.

        Args:
            task: The task containing code modification instructions.
            agent: The agent executing the task.
            codebase: The codebase to modify.

        Returns:
            A TaskResult object containing the results of the code modification.
        """
        self.reflector.reflect(f"Modifying code in files: {', '.join(task.file_paths)}")
        modified_code = self.coder_agent.generate_code(task, agent)

        max_iterations = 3
        iteration_count = 0

        while iteration_count < max_iterations:
            unsuccessful_tests, successful_tests = self.tester.run_tests(modified_code, codebase)

            if not unsuccessful_tests:
                self.reflector.reflect("All tests passed successfully.")
                break

            self.reflector.reflect(
                f"Iteration {iteration_count + 1}: {len(unsuccessful_tests)} tests failed. Attempting to fix..."
            )

            for test in unsuccessful_tests:
                modified_code = self.coder_agent.modify_code_based_on_test(
                    modified_code, test.test_code, test.message, task
                )

            iteration_count += 1

        if iteration_count == max_iterations:
            self.reflector.reflect("Maximum iterations reached. Some tests are still failing.")

        modified_files = {
            file_change.path: file_change.code for file_change in modified_code.code_changes
        }

        return TaskResult(
            task_id=task.id,
            success=len(unsuccessful_tests) == 0,
            output="Code modification complete"
            if not unsuccessful_tests
            else "Some tests are still failing",
            modified_files=modified_files,
            test_results=successful_tests + unsuccessful_tests,
        )

    def execute_llm_task(self, task: Task) -> TaskResult:
        """
        Execute a task using the language model.

        Args:
            task: The task to be executed by the language model.

        Returns:
            A TaskResult object containing the results of the language model execution.
        """
        self.reflector.reflect(f"Executing LLM task: {task.description}")
        result = self.llm_interface.generate(task.prompt_llm)
        return TaskResult(task_id=task.id, success=True, output=result)

    def compile_results(self, project_result: ProjectResult) -> FinalResult:
        """
        Compile the final results of the project execution.

        Args:
            project_result: The ProjectResult object to compile.

        Returns:
            A FinalResult object containing the compiled results.
        """
        self.reflector.reflect("Compiling final results")
        output_directory = "output"
        return FinalResult(project_result=project_result, output_directory=output_directory)
