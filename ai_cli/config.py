"""
Configuration constants and settings for AI CLI.
"""

import os
from typing import Optional

# Default OpenAI model to use
DEFAULT_MODEL = "gpt-4.1-nano-2025-04-14"

# Keyring service name for storing API key
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