"""
AI CLI - Convert natural language questions to terminal commands using OpenAI

A modular command-line interface that uses OpenAI's API to generate
terminal commands from natural language descriptions.
"""

from .main import main
from .commands import SetupCommand, StatusCommand, ResetCommand, QueryCommand
from .api_key_manager import APIKeyManager
from .base_client import BaseAIClient
from .claude_client import ClaudeClient
from .client_factory import create_client
from .openai_client import OpenAIClient
from .openrouter_client import OpenRouterClient
from .provider_config import ProviderConfigManager
from .system_utils import SystemUtils
from .config import DEFAULT_MODEL, PROVIDERS

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
    "BaseAIClient",
    "ClaudeClient",
    "create_client",
    "OpenAIClient",
    "OpenRouterClient",
    "ProviderConfigManager",
    "SystemUtils",
    "DEFAULT_MODEL",
    "PROVIDERS",
]