"""File operation utilities for the Autonoma package."""

import os
import json
from typing import Dict, List
from autonoma.models import FinalResult, AgentResult


def store_results(final_result: FinalResult) -> None:
    """
    Store the final results to separate files.

    Args:
        final_result: The FinalResult object containing the results to store.
    """
    os.makedirs(final_result.output_directory, exist_ok=True)

    # Store project details
    with open(f"{final_result.output_directory}/project.json", "w") as f:
        json.dump(final_result.project_result.project.dict(), f, indent=2)

    # Store modified files
    for file_path, content in final_result.project_result.modified_files.items():
        with open(f"{final_result.output_directory}/{file_path}", "w") as f:
            f.write(content)

    # Store new files
    for file_path, content in final_result.project_result.new_files.items():
        with open(f"{final_result.output_directory}/{file_path}", "w") as f:
            f.write(content)

    # Store thought process
    with open(f"{final_result.output_directory}/thought_process.txt", "w") as f:
        f.write("\n".join(final_result.project_result.thought_process))

    print(f"Results stored in the '{final_result.output_directory}' directory")


def get_modified_files(agent_results: List[AgentResult]) -> Dict[str, str]:
    """
    Get all modified files from the agent results.

    Args:
        agent_results: A list of AgentResult objects.

    Returns:
        A dictionary of modified file paths and their contents.
    """
    modified_files = {}
    for agent_result in agent_results:
        for task_result in agent_result.task_results:
            modified_files.update(task_result.modified_files)
    return modified_files


def get_new_files(agent_results: List[AgentResult]) -> Dict[str, str]:
    """
    Get all new files from the agent results.

    Args:
        agent_results: A list of AgentResult objects.

    Returns:
        A dictionary of new file paths and their contents.
    """
    new_files = {}
    for agent_result in agent_results:
        for task_result in agent_result.task_results:
            new_files.update(task_result.new_files)
    return new_files
