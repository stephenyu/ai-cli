"""
Configuration constants and settings for AI CLI.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .exceptions import UnknownProviderError

# Default OpenAI model to use
DEFAULT_MODEL = "gpt-4.1-nano-2025-04-14"

# Keyring service name for storing API key. Kept as "openai-api-key" even
# though the active provider may not be OpenAI: the keyring holds whichever
# provider's key is currently active (see ProviderConfigManager for which
# provider that is), and renaming this would strand existing users' stored
# keys on upgrade.
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
    "testing_key": "🔍 Testing API key...",
    "storing_key": "💾 Storing API key securely...",
    "setup_complete": "🎉 Setup complete! You can now use the 'ai' command.",
    "example_usage": "Example: ai 'list all python files'",
    "clipboard_success": "✅ Command copied to clipboard! Paste and press Enter to execute.",
    "clipboard_failed": "❌ Could not copy to clipboard. Please copy the command manually.",
}

# Environment variable names
ENV_API_KEY = "OPENAI_API_KEY"


@dataclass(frozen=True)
class ProviderSpec:
    """Everything provider-specific the CLI needs to know about a provider."""

    name: str
    label: str
    default_model: str
    key_prefix: str
    env_var: str
    key_url: str


PROVIDER_OPENAI = "openai"
PROVIDER_CLAUDE = "claude"
PROVIDER_OPENROUTER = "openrouter"

DEFAULT_PROVIDER = PROVIDER_OPENAI

PROVIDERS = {
    PROVIDER_OPENAI: ProviderSpec(
        name=PROVIDER_OPENAI,
        label="OpenAI",
        default_model=DEFAULT_MODEL,
        key_prefix=OPENAI_KEY_PREFIX,
        env_var=ENV_API_KEY,
        key_url="https://platform.openai.com/api-keys",
    ),
    PROVIDER_CLAUDE: ProviderSpec(
        name=PROVIDER_CLAUDE,
        label="Claude",
        default_model="claude-haiku-4-5-20251001",
        key_prefix="sk-ant-",
        env_var="ANTHROPIC_API_KEY",
        key_url="https://console.anthropic.com/settings/keys",
    ),
    PROVIDER_OPENROUTER: ProviderSpec(
        name=PROVIDER_OPENROUTER,
        label="OpenRouter",
        default_model="anthropic/claude-haiku-4.5",
        key_prefix="sk-or-",
        env_var="OPENROUTER_API_KEY",
        key_url="https://openrouter.ai/keys",
    ),
}

# Non-secret active-provider/active-model state. The API key itself stays
# in the keyring (see KEYRING_SERVICE/KEYRING_USERNAME above) — this file
# only ever holds the provider name and model id.
CONFIG_DIR = Path.home() / ".config" / "ai-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_provider_spec(provider: str) -> ProviderSpec:
    """Look up a provider's spec, raising if the name isn't registered."""
    try:
        return PROVIDERS[provider]
    except KeyError:
        valid = ", ".join(PROVIDERS)
        raise UnknownProviderError(
            f"Unknown AI provider '{provider}'. Valid providers: {valid}"
        ) from None


def get_env_api_key(provider: str = DEFAULT_PROVIDER) -> Optional[str]:
    """Get a provider's API key from its environment variable, if set."""
    return os.getenv(get_provider_spec(provider).env_var)