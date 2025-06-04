import os
from .base import AbstractAgent
from .google_vertex_agent import GoogleVertexAgent
from .langchain_agent import LangChainAgent


class AgentFactory:
    """Factory for creating agent implementations based on configuration."""

    @staticmethod
    def create_agent() -> AbstractAgent:
        framework = os.getenv("AGENT_FRAMEWORK", "langchain").lower()
        if framework == "google_vertex" or framework == "vertex":
            return GoogleVertexAgent()
        return LangChainAgent()
