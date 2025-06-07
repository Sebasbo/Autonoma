"""Core agent module for the Autonoma package."""

from typing import List, Any
from autonoma.models import (
    Project, # Keep for ProjectResult, though MainSequentialAgent produces a dict
    # Agent, Task, TaskType, PlanRequest - No longer directly used here
    CodeFile,
    ProjectResult,
    # AgentResult, TaskResult - No longer directly used here
    FinalResult,
    ExecutedProject, # For dummy project in ProjectResult
)
# from .planner import PlannerAgent # Removed
# from .coder import CoderAgent # Removed
# from .tester import Tester # Removed

from autonoma.adk_agents.main_sequential_agent import (
    MainSequentialAgent,
    # GlobalLLMInterface,
    # AdkCodeExecutorToolPlaceholder, # No longer used, replaced by AdkBuiltInCodeExecutionTool
    AdkBuiltInCodeExecutionTool # Hypothetical real ADK tool
)
from autonoma.adk_tools.planning_tool import PlanningTool
from autonoma.adk_tools.coding_tool import CodeGenerationTool
from autonoma.adk_tools.testing_tool import TestExecutionTool

from autonoma.utils.file_operations import store_results # get_modified_files, get_new_files are effectively replaced
from autonoma.utils.reflection import Reflector


class AutonomaAgent:
    """
    Main agent class for the Autonoma system.
    This class now orchestrates the MainSequentialAgent (ADK-style).
    """

    def __init__(self, llm_interface: Any): # llm_interface could be GlobalLLMInterface or compatible
        """
        Initialize the AutonomaAgent.

        Args:
            llm_interface: An interface to the language model for generating responses.
                           This should be compatible with what the ADK tools expect.
        """
        self.llm_interface = llm_interface # This might need to be an instance of GlobalLLMInterface

        # Instantiate ADK tools
        # Ensure llm_interface is compatible with what tools expect (e.g. has .generate method)
        planning_tool = PlanningTool(llm_interface=llm_interface)
        code_generation_tool = CodeGenerationTool(llm_interface=llm_interface)
        testing_tool = TestExecutionTool(llm_interface=llm_interface)

        # HYPOTHETICAL: Instantiate the real ADK Code Execution Tool
        # This might require specific configurations or parameters based on the actual ADK library.
        # For now, assume a simple instantiation or use its placeholder if direct instantiation is complex/unknown.
        try:
            # Check if AdkBuiltInCodeExecutionTool is the actual class or still the placeholder from main_sequential_agent
            # This check is a bit indirect; ideally, we'd know if the real one was successfully imported.
            if "AdkBuiltInCodeExecutionTool" in globals() and \
               hasattr(globals()["AdkBuiltInCodeExecutionTool"], 'execute') and \
               not type(globals()["AdkBuiltInCodeExecutionTool"].__init__) == type(type.__init__): # Avoid instantiating if it's just `object`
                 print("AutonomaAgent: Attempting to use 'real' AdkBuiltInCodeExecutionTool.")
                 code_executor_tool = AdkBuiltInCodeExecutionTool() # Or with args if known
            else:
                print("AutonomaAgent: Using placeholder AdkBuiltInCodeExecutionTool due to import fallback.")
                # This placeholder is defined in main_sequential_agent if real import fails
                code_executor_tool = globals().get("AdkBuiltInCodeExecutionTool", AdkCodeExecutorToolPlaceholder)() # Fallback
        except Exception as e:
            print(f"AutonomaAgent: Error instantiating AdkBuiltInCodeExecutionTool, falling back. Error: {e}")
            # Define a local fallback if even the imported placeholder fails (should not happen if main_sequential_agent is robust)
            class LocalFallbackAdkCodeExecutor:
                 def execute(self, script_to_execute: str, files_in_context: Dict[str, str], command_args: Optional[List[str]] = None):
                    print(f"LocalFallbackAdkCodeExecutor.execute for {script_to_execute}")
                    # Must return an object that matches AdkCodeExecutionResult structure used in MainSequentialAgent
                    # This requires AdkCodeExecutionResult to be available here or define a compatible one.
                    # For simplicity, assume AdkCodeExecutionResult is globally available via main_sequential_agent imports.
                    from autonoma.adk_agents.main_sequential_agent import AdkCodeExecutionResult # Ensure available
                    return AdkCodeExecutionResult(success=True, stdout="Local fallback output", stderr="", exit_code=0)
            code_executor_tool = LocalFallbackAdkCodeExecutor()


        # Instantiate MainSequentialAgent
        self.main_adk_agent = MainSequentialAgent(
            llm_interface=llm_interface,
            planning_tool=planning_tool,
            code_generation_tool=code_generation_tool,
            testing_tool=testing_tool,
            code_executor_tool=code_executor_tool # Pass the real or placeholder ADK tool
        )

        self.reflector = Reflector()
        # self.planner_agent = PlannerAgent(llm_interface) # Removed
        # self.coder_agent = CoderAgent(llm_interface) # Removed
        # self.tester = Tester(llm_interface) # Removed


    def process_query(self, query: str, code_base: List[CodeFile]) -> FinalResult:
        """
        Process a query against the given codebase using the MainSequentialAgent.

        Args:
            query: The query to process.
            code_base: The codebase to process the query against.

        Returns:
            A FinalResult object containing the results of the query processing.
        """
        self.reflector.reflect(f"Processing query via MainSequentialAgent: {query}")

        raw_adk_result: Dict = self.main_adk_agent.run(query=query, initial_codebase=code_base)

        # Adapt raw_adk_result (Dict) to ProjectResult model
        final_code_changes_dicts = raw_adk_result.get("final_code_changes", [])
        # Ensure final_code_changes_dicts are actual dicts if they come from Pydantic models
        processed_final_code_changes = []
        for item in final_code_changes_dicts:
            if hasattr(item, 'model_dump'): # Check if it's a Pydantic model
                processed_final_code_changes.append(item.model_dump())
            else: # Assume it's already a dict
                processed_final_code_changes.append(item)

        modified_code_files: List[CodeFile] = [CodeFile(**cf_dict) for cf_dict in processed_final_code_changes]

        initial_paths = {cf.path for cf in code_base}
        modified_paths = {mcf.path for mcf in modified_code_files}

        new_files_list: List[CodeFile] = [mcf for mcf in modified_code_files if mcf.path not in initial_paths]

        actually_modified_files_list: List[CodeFile] = [
            mcf for mcf in modified_code_files if mcf.path in initial_paths and mcf.path in modified_paths
        ]

        unchanged_files_dict: Dict[str, str] = {
            cf.path: cf.content for cf in code_base if cf.path not in modified_paths
        }

        # Ensure paths in actually_modified_files_list are truly modified compared to initial state
        # This step is crucial if final_code_changes from ADK agent might include unchanged files.
        # Assuming final_code_changes ONLY includes changed/new files.

        initial_code_map = {cf.path: cf.content for cf in code_base}
        truly_modified_files_final = []
        for mcf in actually_modified_files_list:
            if mcf.path in initial_code_map and initial_code_map[mcf.path] != mcf.content:
                truly_modified_files_final.append(mcf)
            elif mcf.path not in initial_code_map: # Should be caught by new_files_list but as a safeguard
                 new_files_list.append(mcf)


        dummy_executed_project = ExecutedProject(agents=[])

        project_result_obj = ProjectResult(
            project=dummy_executed_project,
            agent_results=[],
            modified_files=truly_modified_files_final,
            new_files=new_files_list,
            unchanged_files=unchanged_files_dict,
            thought_process=self.reflector.thought_process
        )

        final_result_obj = self.compile_results(project_result_obj)
        # store_results might need to be aware of the new llm_interface if it logs to a file based on that
        store_results(final_result_obj)

        return final_result_obj

    # def execute_project(self, project: Project, code_base: List[CodeFile]) -> ProjectResult:
    #     """
    #     Execute a project against the given codebase.
    #
    #     Args:
    #         project: The project to execute.
    #         code_base: The codebase to execute the project against.
    #
    #     Returns:
    #         A ProjectResult object containing the results of the project execution.
    #     """
    #     agent_results: List[AgentResult] = []
    #
    #     for agent in project.agents:
    #         agent_result = self.execute_agent_tasks(agent, code_base)
    #         agent_results.append(agent_result)
    #
    #     modified_files = get_modified_files(agent_results) # This helper would be problematic now
    #
    #     return ProjectResult(
    #         project=project,
    #         agent_results=agent_results,
    #         modified_files=modified_files,
    #         new_files=get_new_files(agent_results), # This helper would be problematic now
    #         unchanged_files={
    #             file.path: file.content for file in code_base if file.path not in modified_files
    #         },
    #         thought_process=self.reflector.thought_process,
    #     )
    #
    # def execute_agent_tasks(self, agent: Agent, codebase: List[CodeFile]) -> AgentResult:
    #     """
    #     Execute the tasks of a single agent.
    #
    #     Args:
    #         agent: The agent whose tasks are to be executed.
    #         codebase: The codebase to execute the tasks against.
    #
    #     Returns:
    #         An AgentResult object containing the results of the agent's task executions.
    #     """
    #     self.reflector.reflect(f"Executing tasks for agent: {agent.name}")
    #     task_results: List[TaskResult] = []
    #
    #     for task in agent.tasks:
    #         task_result = self.execute_task(task, agent, codebase)
    #         task_results.append(task_result)
    #
    #     return AgentResult(agent_name=agent.name, task_results=task_results)
    #
    # def execute_task(self, task: Task, agent: Agent, codebase: List[CodeFile]) -> TaskResult:
    #     """
    #     Execute a single task.
    #
    #     Args:
    #         task: The task to execute.
    #         agent: The agent executing the task.
    #         codebase: The codebase to execute the task against.
    #
    #     Returns:
    #         A TaskResult object containing the results of the task execution.
    #     """
    #     self.reflector.reflect(f"Executing task: {task.description}")
    #     if task.task_type == TaskType.CODE_IMPLEMENTATION: # TaskType would need to be imported or handled if used
    #         return self.modify_code(task, agent, codebase)
    #     else:
    #         return self.execute_llm_task(task)
    #
    # def modify_code(self, task: Task, agent: Agent, codebase: List[CodeFile]) -> TaskResult:
    #     """
    #     Modify code based on the given task.
    #
    #     Args:
    #         task: The task containing code modification instructions.
    #         agent: The agent executing the task.
    #         codebase: The codebase to modify.
    #
    #     Returns:
    #         A TaskResult object containing the results of the code modification.
    #     """
    #     self.reflector.reflect(f"Modifying code in files: {', '.join(task.file_paths)}")
    #     # modified_code = self.coder_agent.generate_code(task, agent) # Old CoderAgent
    #
    #     max_iterations = 3
    #     iteration_count = 0
    #
    #     # This loop needs to be entirely rethought with ADK tools
    #     # while iteration_count < max_iterations:
    #         # unsuccessful_tests, successful_tests = self.tester.run_tests(modified_code, codebase) # Old Tester
    #
    #         # if not unsuccessful_tests:
    #         #     self.reflector.reflect("All tests passed successfully.")
    #         #     break
    #         #
    #         # self.reflector.reflect(
    #         #     f"Iteration {iteration_count + 1}: {len(unsuccessful_tests)} tests failed. Attempting to fix..."
    #         # )
    #         #
    #         # for test in unsuccessful_tests:
    #         #     modified_code = self.coder_agent.modify_code_based_on_test( # Old CoderAgent
    #         #         modified_code, test.test_code, test.message, task
    #         #     )
    #         #
    #         # iteration_count += 1
    #
    #     # if iteration_count == max_iterations:
    #     #     self.reflector.reflect("Maximum iterations reached. Some tests are still failing.")
    #
    #     # modified_files = {
    #     #     file_change.path: file_change.code for file_change in modified_code.code_changes
    #     # }
    #
    #     return TaskResult( # TaskResult model would need to be imported or adapted
    #         task_id=task.id,
    #         success=True, # Placeholder
    #         output="Code modification process (now via ADK agent) complete for this task.",
    #         modified_files={}, # Placeholder
    #         test_results=[], # Placeholder
    #     )
    #
    # def execute_llm_task(self, task: Task) -> TaskResult: # Task model would need to be imported
    #     """
    #     Execute a task using the language model.
    #
    #     Args:
    #         task: The task to be executed by the language model.
    #
    #     Returns:
    #         A TaskResult object containing the results of the language model execution.
    #     """
    #     self.reflector.reflect(f"Executing LLM task: {task.description}")
    #     # result = self.llm_interface.generate(task.prompt_llm) # Assuming task has prompt_llm
    #     # return TaskResult(task_id=task.id, success=True, output=result)
    #     return TaskResult(task_id=task.id, success=True, output="LLM Task executed (placeholder).")


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
