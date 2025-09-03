"""
Ollama provider implementation for AI CLI.
"""

import json
import sys
import getpass
import keyring
from typing import Optional, Dict, Any

try:
    import requests
except ImportError:
    requests = None

from .base import AIProvider, CommandOutput
from ..exceptions import APIKeyInvalidError
from ..config import get_provider_config
from ..config_manager import ConfigManager


class OllamaAPIError(Exception):
    """Exception raised when Ollama API calls fail."""
    
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error


class OllamaProvider(AIProvider):
    """Ollama provider implementation."""

    def __init__(self, config: Dict[str, str]):
        """
        Initialize the Ollama provider.

        Args:
            config: Dictionary containing 'url' and 'model' keys.
        """
        super().__init__(config)
        self.config = config
        self.url = config.get('url')
        self.model = config.get('model')

    @classmethod
    def setup_interactive(cls) -> 'OllamaProvider':
        """
        Interactive setup for Ollama provider.
        
        Returns:
            Configured Ollama provider instance.
            
        Raises:
            KeyboardInterrupt: If user cancels setup.
            APIKeyInvalidError: If configuration is invalid.
        """
        config = get_provider_config("ollama")
        config_manager = ConfigManager()
        
        print("Setting up Ollama provider.")
        print()
        
        # Get existing config from file to use as defaults
        existing_config = config_manager.get_provider_config("ollama")
        
        # Get API URL - use config file value if available, otherwise system default
        default_url = existing_config.get("url", config["default_url"])
        url_input = input(f"Ollama API URL (default: {default_url}): ").strip()
        url = url_input if url_input else default_url
        
        # Get model name - use config file value if available, otherwise system default  
        default_model = existing_config.get("model", config["default_model"])
        model_input = input(f"Model to use (default: {default_model}): ").strip()
        model = model_input if model_input else default_model
        
        # Create configuration
        ollama_config = {
            'url': url,
            'model': model
        }
        
        # Create instance and test configuration
        provider = cls(ollama_config)
        print()
        print("🔍 Testing Ollama configuration...")
        try:
            provider.validate_credentials()
            print("✅ Ollama configuration is valid!")
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            response = input("Store the configuration anyway? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("Setup cancelled.")
                raise KeyboardInterrupt()
        
        # Store the configuration in the config file only (no sensitive data)
        try:
            config_manager.set_provider_config("ollama", ollama_config)
            print("✅ Ollama configuration stored in configuration file!")
        except Exception as e:
            print(f"⚠️  Could not store configuration in file: {e}")
            print(f"You can still use the {config['env_var']} environment variable as a fallback.")
        
        return provider

    @classmethod
    def get_provider_display_name(cls) -> str:
        """Get the display name of the provider for user prompts."""
        return "Ollama"

    def validate_credentials(self) -> None:
        """
        Validate the configuration by making a test call.

        Raises:
            APIKeyInvalidError: If the configuration is invalid.
            OllamaAPIError: If there's an API error.
        """
        if requests is None:
            raise OllamaAPIError("requests library is required for Ollama provider. Run: pip install requests")
        
        if not self.url:
            raise APIKeyInvalidError("Ollama API URL is required")
        if not self.model:
            raise APIKeyInvalidError("Ollama model is required")

        try:
            # Test with a simple prompt
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": "test",
                    "stream": False
                },
                timeout=10
            )
            
            if response.status_code == 404 and "model" in response.text.lower():
                raise APIKeyInvalidError(f"Model '{self.model}' not found. Make sure it's installed in Ollama.")
            elif response.status_code != 200:
                raise OllamaAPIError(f"Ollama API returned status {response.status_code}: {response.text}")
            
            # Check if response contains expected structure
            try:
                data = response.json()
                if "response" not in data:
                    raise OllamaAPIError("Invalid response format from Ollama API")
            except json.JSONDecodeError:
                raise OllamaAPIError("Invalid JSON response from Ollama API")
                
        except requests.exceptions.ConnectionError:
            raise APIKeyInvalidError(f"Could not connect to Ollama at {self.url}. Is Ollama running?")
        except requests.exceptions.Timeout:
            raise OllamaAPIError("Request to Ollama timed out")
        except Exception as e:
            if isinstance(e, (APIKeyInvalidError, OllamaAPIError)):
                raise
            raise OllamaAPIError(f"Error validating Ollama configuration: {e}")

    def generate_command(
        self, 
        question: str, 
        system_info: str, 
        model: Optional[str] = None, 
        debug: bool = False
    ) -> str:
        """
        Use Ollama to convert a natural language question into a terminal command.

        Args:
            question: The user's natural language question.
            system_info: System information for context.
            model: The model to use (overrides configured model).
            debug: Whether to show debug information.

        Returns:
            The generated terminal command.

        Raises:
            OllamaAPIError: If the API call fails.
        """
        model_to_use = model if model else self.model
        
        system_prompt = self._build_system_prompt(system_info)
        full_prompt = f"{system_prompt}\n\nUser question: {question}\n\nTerminal command:"

        # Show debug information if requested
        if debug:
            self._print_debug_info(full_prompt, model_to_use)

        if requests is None:
            raise OllamaAPIError("requests library is required for Ollama provider. Run: pip install requests")

        try:
            response = requests.post(
                self.url,
                json={
                    "model": model_to_use,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code != 200:
                raise OllamaAPIError(f"Ollama API returned status {response.status_code}: {response.text}")
            
            data = response.json()
            command = data.get("response", "").strip()
            
            if not command:
                raise OllamaAPIError("Empty command returned from Ollama API")

            return command

        except requests.exceptions.ConnectionError:
            raise OllamaAPIError(f"Could not connect to Ollama at {self.url}. Is Ollama running?")
        except requests.exceptions.Timeout:
            raise OllamaAPIError("Request to Ollama timed out")
        except Exception as e:
            if isinstance(e, OllamaAPIError):
                raise
            raise OllamaAPIError(f"Error calling Ollama API: {e}")

    def get_provider_name(self) -> str:
        """Get the name of the provider."""
        return "Ollama"

    def get_default_model(self) -> str:
        """Get the default model for Ollama."""
        return self.config.get('model', 'llama2')

    def _print_debug_info(self, prompt: str, model: str) -> None:
        """
        Print debug information about the request being sent to Ollama.

        Args:
            prompt: The prompt being sent.
            model: The model being used.
        """
        print("🔍 DEBUG: Ollama API Request", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        print(f"URL: {self.url}", file=sys.stderr)
        print(f"Model: {model}", file=sys.stderr)
        print("-" * 50, file=sys.stderr)
        print("Prompt:", file=sys.stderr)
        print(prompt, file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        print("", file=sys.stderr)

    def _build_system_prompt(self, system_info: str) -> str:
        """
        Build the system prompt for Ollama.

        Args:
            system_info: System information to include in the prompt.

        Returns:
            The formatted system prompt.
        """
        return f"""You are a terminal command expert that converts natural language questions into precise Unix/Linux/macOS terminal commands.

System Information: {system_info}

Instructions:
- Only output the terminal command with no additional formatting, explanations, or commentary
- The command should be ready to run directly in a terminal
- If the question is ambiguous, choose the most common/useful interpretation
- Focus on practical, commonly used commands
- Priority is to use built-in commands rather than external tools
- If multiple commands are needed, separate them with &&
- Do not include markdown, backticks, or any other formatting
- The user has NO PACKAGES INSTALLED FOR LANGUAGES. Only default functions are available.

Examples:
- "list all python files" → find . -name "*.py" -type f
- "show disk usage" → du -sh .
- "count lines in all python files" → find . -name "*.py" -exec wc -l {{}} + | tail -1"""