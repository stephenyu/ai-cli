"""
AI CLI - Convert natural language questions to terminal commands using OpenAI

A modular command-line interface that uses OpenAI's API to generate
terminal commands from natural language descriptions.
"""

from .main import main
from .commands import SetupCommand, StatusCommand, ResetCommand, QueryCommand
from .api_key_manager import APIKeyManager
from .openai_client import OpenAIClient
from .system_utils import SystemUtils
from .config import DEFAULT_MODEL

__version__ = "0.3.0"
__author__ = "Stephen Yu"
__email__ = "" # For Privacy, not needed

__all__ = [
    "main",
    "SetupCommand",
    "StatusCommand", 
    "ResetCommand",
    "QueryCommand",
    "APIKeyManager",
    "OpenAIClient",
    "SystemUtils",
    "DEFAULT_MODEL",
] 