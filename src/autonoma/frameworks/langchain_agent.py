from __future__ import annotations

import os
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from .base import AbstractAgent


class LangChainAgent(AbstractAgent):
    """Concrete agent implementation using LangChain."""

    def __init__(self, api_key: str | None = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(openai_api_key=api_key, temperature=0)
        self.agent = initialize_agent([], self.llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

    def generate(self, user_prompt: str, system_prompt: str = "") -> str:
        prompt = f"{system_prompt}\n{user_prompt}" if system_prompt else user_prompt
        return self.agent.run(prompt)
