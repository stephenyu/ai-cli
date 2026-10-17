"""Factory for creating the right AI provider client."""

from .base_client import BaseAIClient
from .claude_client import ClaudeClient
from .config import PROVIDER_CLAUDE, PROVIDER_OPENAI, PROVIDER_OPENROUTER
from .exceptions import UnknownProviderError
from .openai_client import OpenAIClient
from .openrouter_client import OpenRouterClient

_CLIENT_CLASSES = {
    PROVIDER_OPENAI: OpenAIClient,
    PROVIDER_CLAUDE: ClaudeClient,
    PROVIDER_OPENROUTER: OpenRouterClient,
}


def create_client(provider: str, api_key: str) -> BaseAIClient:
    """
    Construct the client for the given provider.

    Args:
        provider: The provider name (see ai_cli.config.PROVIDERS).
        api_key: The API key to use for that provider.

    Returns:
        A BaseAIClient implementation for the provider.

    Raises:
        UnknownProviderError: If the provider name isn't registered.
    """
    try:
        client_cls = _CLIENT_CLASSES[provider]
    except KeyError:
        valid = ", ".join(_CLIENT_CLASSES)
        raise UnknownProviderError(
            f"Unknown AI provider '{provider}'. Valid providers: {valid}"
        ) from None
    return client_cls(api_key)
