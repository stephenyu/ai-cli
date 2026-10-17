"""OpenRouter API client for AI CLI.

OpenRouter exposes an OpenAI-compatible chat completions endpoint, so this
reuses the `openai` SDK pointed at OpenRouter's base URL rather than a
separate client library.
"""

from openai import OpenAI

from .base_client import BaseAIClient
from .exceptions import APIKeyInvalidError, OpenRouterAPIError
from .prompts import build_system_prompt

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterClient(BaseAIClient):
    """Handles OpenRouter API interactions."""

    def __init__(self, api_key: str):
        """
        Initialize the OpenRouter client.

        Args:
            api_key: The OpenRouter API key.
        """
        super().__init__(api_key)
        self.client = OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)

    def validate_api_key(self) -> None:
        """
        Validate the API key by making a test call.

        Note: OpenRouter's /models endpoint is public and requires no
        authentication, so it can't be used to validate a key (any key,
        valid or not, gets a 200). /key is OpenRouter's authenticated
        endpoint for key info, so it's used here instead.

        Raises:
            APIKeyInvalidError: If the API key is invalid.
            OpenRouterAPIError: If there's an API error.
        """
        try:
            self.client.get("/key", cast_to=dict)
        except Exception as e:
            if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                raise APIKeyInvalidError(f"Invalid API key: {e}") from e
            else:
                raise OpenRouterAPIError(f"API validation error: {e}", e) from e

    def get_terminal_command(self, question: str, system_info: str, model: str) -> str:
        """
        Use a model routed through OpenRouter to convert a natural language
        question into a terminal command.

        Args:
            question: The user's natural language question.
            system_info: System information for context.
            model: The OpenRouter model slug to use (e.g. "anthropic/claude-3.5-haiku").

        Returns:
            The generated terminal command.

        Raises:
            OpenRouterAPIError: If the API call fails.
        """
        system_prompt = build_system_prompt(system_info)

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ],
            )

            command = response.choices[0].message.content.strip()
            if not command:
                raise OpenRouterAPIError("Empty command returned from API")

            return command

        except OpenRouterAPIError:
            raise
        except Exception as e:
            raise OpenRouterAPIError(f"Error calling OpenRouter API: {e}", e) from e
