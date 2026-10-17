"""
OpenAI API client for AI CLI.
"""

from openai import OpenAI
from pydantic import BaseModel
from typing import Optional

from .base_client import BaseAIClient
from .config import DEFAULT_MODEL
from .exceptions import OpenAIAPIError, APIKeyInvalidError
from .prompts import build_system_prompt


class CommandOutput(BaseModel):
    """Pydantic model for OpenAI API response."""
    command_line: str


class OpenAIClient(BaseAIClient):
    """Handles OpenAI API interactions."""

    def __init__(self, api_key: str):
        """
        Initialize the OpenAI client.

        Args:
            api_key: The OpenAI API key.
        """
        super().__init__(api_key)
        self.client = OpenAI(api_key=api_key)
    
    def validate_api_key(self) -> None:
        """
        Validate the API key by making a test call.
        
        Raises:
            APIKeyInvalidError: If the API key is invalid.
            OpenAIAPIError: If there's an API error.
        """
        try:
            response = self.client.models.list()
            if not response:
                raise APIKeyInvalidError("API key validation failed")
        except Exception as e:
            if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                raise APIKeyInvalidError(f"Invalid API key: {e}") from e
            else:
                raise OpenAIAPIError(f"API validation error: {e}", e) from e
    
    def get_terminal_command(self, question: str, system_info: str, model: str = DEFAULT_MODEL) -> str:
        """
        Use OpenAI to convert a natural language question into a terminal command.
        
        Args:
            question: The user's natural language question.
            system_info: System information for context.
            model: The OpenAI model to use.
            
        Returns:
            The generated terminal command.
            
        Raises:
            OpenAIAPIError: If the API call fails.
        """
        system_prompt = self._build_system_prompt(system_info)
        
        try:
            response = self.client.responses.parse(
                model=model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                text_format=CommandOutput,
            )
            
            command = response.output_parsed.command_line.strip()
            if not command:
                raise OpenAIAPIError("Empty command returned from API")
            
            return command
        
        except Exception as e:
            raise OpenAIAPIError(f"Error calling OpenAI API: {e}", e) from e
    
    def _build_system_prompt(self, system_info: str) -> str:
        """
        Build the system prompt for the OpenAI API.

        Args:
            system_info: System information to include in the prompt.

        Returns:
            The formatted system prompt.
        """
        return build_system_prompt(system_info) 