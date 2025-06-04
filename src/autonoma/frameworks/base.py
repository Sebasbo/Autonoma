from abc import ABC, abstractmethod

class AbstractAgent(ABC):
    """Abstract base class for LLM agent frameworks."""

    @abstractmethod
    def generate(self, user_prompt: str, system_prompt: str = "") -> str:
        """Generate a response using the underlying agent framework."""
        pass
