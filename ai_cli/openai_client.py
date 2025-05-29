"""
OpenAI API client for AI CLI.
"""

from openai import OpenAI
from pydantic import BaseModel
from typing import Optional

from .config import DEFAULT_MODEL
from .exceptions import OpenAIAPIError, APIKeyInvalidError


class CommandOutput(BaseModel):
    """Pydantic model for OpenAI API response."""
    command_line: str


class OpenAIClient:
    """Handles OpenAI API interactions."""
    
    def __init__(self, api_key: str):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: The OpenAI API key.
        """
        self.client = OpenAI(api_key=api_key)
        self.api_key = api_key
    
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
        return f"""# Identity

You are a terminal command expert that converts natural language questions into precise Unix/Linux/macOS terminal commands.

# System Information

Target system: {system_info}

# Instructions

* Only output the terminal command with no additional formatting, explanations, or commentary
* The command should be ready to run directly in a terminal
* If the question is ambiguous, choose the most common/useful interpretation
* Focus on practical, commonly used commands
* If multiple commands are needed, separate them with &&
* Do not include markdown, backticks, or any other formatting

# Examples

<question id="example-1">
ls command sorted by last access
</question>

<command id="example-1">
ls -ltu
</command>

<question id="example-2">
find all python files in current directory
</question>

<command id="example-2">
find . -name "*.py" -type f
</command>

<question id="example-3">
show disk usage of current directory
</question>

<command id="example-3">
du -sh .
</command>

<question id="example-4">
list running processes
</question>

<command id="example-4">
ps aux
</command>

<question id="example-5">
count lines in all python files
</question>

<command id="example-5">
find . -name "*.py" -exec wc -l {{}} + | tail -1
</command>
""" 