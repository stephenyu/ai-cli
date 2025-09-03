"""
Configuration constants and settings for AI CLI.
"""

import os
from typing import Optional

# Default provider and model
DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-4.1-nano-2025-04-14"

# Provider configurations
PROVIDER_CONFIG = {
    "openai": {
        "default_model": "gpt-4.1-nano-2025-04-14",
        "env_var": "OPENAI_API_KEY",
        "keyring_service": "ai-cli-openai",
        "keyring_username": "api-key",
    }
}

# Legacy keyring settings for backwards compatibility
KEYRING_SERVICE = "ai-cli"
KEYRING_USERNAME = "openai-api-key"

# API key validation
OPENAI_KEY_PREFIX = "sk-"
MIN_API_KEY_LENGTH = 20

# System commands for clipboard
CLIPBOARD_COMMANDS = {
    "pbcopy": ["pbcopy"],  # macOS
    "xclip": ["xclip", "-selection", "clipboard"],  # Linux
    "xsel": ["xsel", "--clipboard", "--input"],  # Linux alternative
    "clip": ["clip"],  # Windows/WSL
}

# User interaction messages
MESSAGES = {
    "setup_header": "🔧 AI CLI Setup",
    "status_header": "🔍 AI CLI Status", 
    "reset_header": "🗑️  AI CLI Reset",
    "separator": "=" * 50,
    "api_key_prompt": "Please enter your OpenAI API key.",
    "api_key_url": "You can find your API key at: https://platform.openai.com/api-keys",
    "testing_key": "🔍 Testing API key...",
    "storing_key": "💾 Storing API key securely...",
    "setup_complete": "🎉 Setup complete! You can now use the 'ai' command.",
    "example_usage": "Example: ai 'list all python files'",
    "clipboard_success": "✅ Command copied to clipboard! Paste and press Enter to execute.",
    "clipboard_failed": "❌ Could not copy to clipboard. Please copy the command manually.",
}

# Environment variable names
ENV_API_KEY = "OPENAI_API_KEY"

def get_env_api_key() -> Optional[str]:
    """Get API key from environment variable."""
    return os.getenv(ENV_API_KEY)


def get_provider_config(provider_name: str) -> dict:
    """
    Get configuration for a specific provider.
    
    Args:
        provider_name: Name of the provider.
        
    Returns:
        Provider configuration dictionary.
        
    Raises:
        KeyError: If provider is not configured.
    """
    if provider_name not in PROVIDER_CONFIG:
        raise KeyError(f"Provider '{provider_name}' not configured")
    return PROVIDER_CONFIG[provider_name]


def get_provider_env_api_key(provider_name: str) -> Optional[str]:
    """
    Get API key from environment variable for specific provider.
    
    Args:
        provider_name: Name of the provider.
        
    Returns:
        API key if found, None otherwise.
    """
    try:
        config = get_provider_config(provider_name)
        return os.getenv(config["env_var"])
    except KeyError:
        return None 