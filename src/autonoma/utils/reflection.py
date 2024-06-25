"""Reflection utilities for the Autonoma package."""

from typing import List


class Reflector:
    """A class to handle reflection and thought process logging."""

    def __init__(self):
        self.thought_process: List[str] = []

    def reflect(self, thought: str) -> None:
        """
        Add a thought to the thought process and print it.

        Args:
            thought: The thought to be added and printed.
        """
        self.thought_process.append(thought)
        print(f"Reflection: {thought}")
