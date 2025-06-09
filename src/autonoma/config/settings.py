"""
Configuration settings for the Autonoma application.

This module loads environment variables from a .env file (if present)
and defines configuration constants used throughout the application.
"""
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()  # Load variables from .env file into environment

# The API key for accessing the OpenAI API.
# Loaded from the "OPENAI_API_KEY" environment variable.
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

# The default directory where output files (results, logs, etc.) are stored.
OUTPUT_DIR: str = "output"
