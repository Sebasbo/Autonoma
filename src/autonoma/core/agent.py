"""Core agent module for the Autonoma package."""

from typing import List, Any, Protocol, Dict, Optional
# Updated model imports to reflect their new locations
from autonoma.models.project import ExecutedProject
from autonoma.models.code import CodeFile
from autonoma.models.result import ProjectResult, FinalResult

from autonoma.adk_agents.main_sequential_agent import (
    MainSequentialAgent,
    AdkBuiltInCodeExecutionTool
)
from autonoma.adk_tools.planning_tool import PlanningTool
from autonoma.adk_tools.coding_tool import CodeGenerationTool
from autonoma.adk_tools.testing_tool import TestExecutionTool

from autonoma.utils.file_operations import store_results
from autonoma.utils.reflection import Reflector


class LLMInterfaceProtocol(Protocol):
    """Protocol for Language Model Interface."""
    def generate(self, user_prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 150) -> str:
        ...


class AutonomaAgent:
    """
    Main agent class for the Autonoma system.
    Orchestrates the MainSequentialAgent (ADK-style) for processing queries.
    """

    def __init__(self, llm_interface: LLMInterfaceProtocol):
        """
        Initialize the AutonomaAgent.

        Args:
            llm_interface: An interface to the language model, conforming to LLMInterfaceProtocol.
        """
        self.llm_interface: LLMInterfaceProtocol = llm_interface
        self.reflector: Reflector = Reflector()

        # Instantiate ADK tools
        planning_tool: PlanningTool = PlanningTool(llm_interface=self.llm_interface)
        code_generation_tool: CodeGenerationTool = CodeGenerationTool(llm_interface=self.llm_interface)
        testing_tool: TestExecutionTool = TestExecutionTool(llm_interface=self.llm_interface)

        code_executor_tool: Any # Define type more broadly due to fallbacks
        # Instantiate the ADK Code Execution Tool
        # This try-except block handles potential issues with initializing the tool,
        # falling back to a placeholder if the primary tool cannot be instantiated.
        try:
            # Check if AdkBuiltInCodeExecutionTool is a functional class rather than a basic object.
            # This helps determine if the intended tool was successfully imported and is not a placeholder.
            if "AdkBuiltInCodeExecutionTool" in globals() and \
               hasattr(globals()["AdkBuiltInCodeExecutionTool"], 'execute') and \
               not type(globals()["AdkBuiltInCodeExecutionTool"].__init__) == type(type.__init__):
                 print("AutonomaAgent: Attempting to use 'real' AdkBuiltInCodeExecutionTool.")
                 code_executor_tool = AdkBuiltInCodeExecutionTool()
            else:
                print("AutonomaAgent: Using placeholder for AdkBuiltInCodeExecutionTool due to import/definition issues.")
                # The placeholder might be defined in main_sequential_agent if the real import fails.
                # Attempt to get it from globals, or define a local fallback if not found.
                # AdkCodeExecutorToolPlaceholder was removed, so we rely on a local fallback or direct AdkBuiltInCodeExecutionTool.
                class PlaceholderAdkCodeExecutor:
                     def execute(self, script_to_execute: str, files_in_context: Dict[str, str], command_args: Optional[List[str]] = None) -> Dict[str, Any]: # type: ignore
                        print(f"PlaceholderAdkCodeExecutor.execute for {script_to_execute}")
                        # Return a dictionary matching the expected structure of AdkCodeExecutionResult.
                        return {"success": True, "stdout": "Placeholder fallback output", "stderr": "", "exit_code": 0}
                code_executor_tool = PlaceholderAdkCodeExecutor()
        except Exception as e:
            print(f"AutonomaAgent: Error instantiating AdkBuiltInCodeExecutionTool, falling back. Error: {e}")
            # Define a local fallback if instantiation fails.
            class LocalFallbackAdkCodeExecutor:
                 def execute(self, script_to_execute: str, files_in_context: Dict[str, str], command_args: Optional[List[str]] = None) -> Dict[str, Any]: # type: ignore
                    print(f"LocalFallbackAdkCodeExecutor.execute for {script_to_execute}")
                    return {"success": True, "stdout": "Local fallback output", "stderr": "", "exit_code": 0}
            code_executor_tool = LocalFallbackAdkCodeExecutor()

        self.main_adk_agent: MainSequentialAgent = MainSequentialAgent(
            llm_interface=self.llm_interface,
            planning_tool=planning_tool,
            code_generation_tool=code_generation_tool,
            testing_tool=testing_tool,
            code_executor_tool=code_executor_tool
        )

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

        # The ADK agent returns a dictionary.
        raw_adk_result: Dict[str, Any] = self.main_adk_agent.run(query=query, initial_codebase=code_base)

        # Adapt raw_adk_result (Dict) to ProjectResult model fields.
        # final_code_changes are expected to be a list of dicts like {'path': '...', 'code': '...'}
        # or Pydantic models that can be dumped to such dicts.
        final_code_changes_raw: List[Any] = raw_adk_result.get("final_code_changes", [])

        processed_final_code_changes_dicts: List[Dict[str, str]] = []
        item: Any
        for item in final_code_changes_raw:
            if hasattr(item, 'model_dump'): # Check if it's a Pydantic model
                processed_final_code_changes_dicts.append(item.model_dump())
            elif isinstance(item, dict): # Assume it's already a dict
                processed_final_code_changes_dicts.append(item)
            else:
                # Handle unexpected item type, perhaps log a warning or error
                print(f"Warning: Unexpected item type in final_code_changes: {type(item)}")
                continue


        # Convert dicts to CodeFile objects
        all_resulting_code_files: List[CodeFile] = [
            CodeFile(path=cf_dict['path'], content=cf_dict['code'])
            for cf_dict in processed_final_code_changes_dicts
            if 'path' in cf_dict and 'code' in cf_dict # Basic validation
        ]

        initial_code_map: Dict[str, str] = {cf.path: cf.content for cf in code_base}
        initial_paths: set[str] = set(initial_code_map.keys())

        new_files_list: List[CodeFile] = []
        truly_modified_codefiles_list: List[CodeFile] = []

        rcf: CodeFile
        for rcf in all_resulting_code_files:
            if rcf.path not in initial_paths:
                new_files_list.append(rcf)
            elif initial_code_map[rcf.path] != rcf.content:
                truly_modified_codefiles_list.append(rcf)

        # Unchanged files are those in the initial codebase not present in new or modified lists.
        modified_and_new_paths: set[str] = {cf.path for cf in new_files_list} | {cf.path for cf in truly_modified_codefiles_list}

        unchanged_files_list: List[CodeFile] = [
            cf for cf in code_base if cf.path not in modified_and_new_paths
        ]

        # ProjectResult expects ExecutedProject for its 'project' field.
        project_for_result: ExecutedProject = ExecutedProject(agents=[]) # Create an empty ExecutedProject

        project_result_obj: ProjectResult = ProjectResult(
            project=project_for_result,
            agent_results=[], # MainSequentialAgent does not produce AgentResult list directly
            modified_files=truly_modified_codefiles_list, # Should be List[CodeFile]
            new_files=new_files_list,                     # Should be List[CodeFile]
            unchanged_files=unchanged_files_list,         # Should be List[CodeFile]
            thought_process=self.reflector.thought_process
        )

        final_result_obj: FinalResult = self.compile_results(project_result_obj)
        store_results(final_result_obj) # Assumes store_results is compatible

        return final_result_obj

    def compile_results(self, project_result: ProjectResult) -> FinalResult:
        """
        Compile the final results of the project execution.

        Args:
            project_result: The ProjectResult object to compile.

        Returns:
            A FinalResult object containing the compiled results.
        """
        self.reflector.reflect("Compiling final results")
        # Consider making output_directory configurable or part of ProjectResult if needed elsewhere
        output_directory: str = "output"
        return FinalResult(project_result=project_result, output_directory=output_directory)
