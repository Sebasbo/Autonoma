from __future__ import annotations

import os
import vertexai
from vertexai.preview.language_models import ChatModel
from .base import AbstractAgent


class GoogleVertexAgent(AbstractAgent):
    """Concrete agent implementation using Google Vertex AI."""

    def __init__(self, project_id: str | None = None, location: str | None = None):
        project_id = project_id or os.getenv("VERTEX_PROJECT_ID")
        location = location or os.getenv("VERTEX_LOCATION", "us-central1")
        vertexai.init(project=project_id, location=location)
        self.chat_model = ChatModel.from_pretrained("chat-bison")
        self.session = self.chat_model.start_chat()

    def generate(self, user_prompt: str, system_prompt: str = "") -> str:
        message = f"{system_prompt}\n{user_prompt}" if system_prompt else user_prompt
        response = self.session.send_message(message)
        return response.text
