"""
OpenAI provider implementation for AI CLI.
"""

import sys
import getpass
import keyring
from openai import OpenAI
from typing import Optional, List, Dict

from .base import AIProvider, CommandOutput
from ..exceptions import OpenAIAPIError, APIKeyInvalidError
from ..config import get_provider_config, OPENAI_KEY_PREFIX, MIN_API_KEY_LENGTH


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation."""

    def __init__(self, api_key: str):
        """
        Initialize the OpenAI provider.

        Args:
            api_key: The OpenAI API key.
        """
        super().__init__(api_key)
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

    @classmethod
    def setup_interactive(cls) -> 'OpenAIProvider':
        """
        Interactive setup for OpenAI provider.
        
        Returns:
            Configured OpenAI provider instance.
            
        Raises:
            KeyboardInterrupt: If user cancels setup.
            APIKeyInvalidError: If API key is invalid.
        """
        config = get_provider_config("openai")
        
        print("Please enter your OpenAI API key.")
        print("You can find your API key at: https://platform.openai.com/api-keys")
        print()
        
        while True:
            try:
                api_key = getpass.getpass("OpenAI API Key: ").strip()
                
                if not api_key:
                    print("❌ API key cannot be empty. Please try again.")
                    continue
                
                # Basic validation
                if len(api_key) < MIN_API_KEY_LENGTH:
                    print(f"⚠️  Warning: API key too short (minimum {MIN_API_KEY_LENGTH} characters)")
                    response = input("Continue anyway? (y/N): ").strip().lower()
                    if response not in ['y', 'yes']:
                        continue
                
                if not api_key.startswith(OPENAI_KEY_PREFIX):
                    print(f"⚠️  Warning: API key should start with '{OPENAI_KEY_PREFIX}'")
                    response = input("Continue anyway? (y/N): ").strip().lower()
                    if response not in ['y', 'yes']:
                        continue
                
                # Create instance and test API key
                provider = cls(api_key)
                print()
                print("🔍 Testing API key...")
                try:
                    provider.validate_credentials()
                    print("✅ API key is valid!")
                except (APIKeyInvalidError, OpenAIAPIError) as e:
                    print(f"❌ API key test failed: {e}")
                    response = input("Store the key anyway? (y/N): ").strip().lower()
                    if response not in ['y', 'yes']:
                        print("Setup cancelled.")
                        continue
                
                # Store the API key
                try:
                    keyring.set_password(config["keyring_service"], config["keyring_username"], api_key)
                    print("✅ OpenAI API key stored securely in system keyring!")
                except Exception as e:
                    print(f"⚠️  Could not store API key in keyring: {e}")
                    print(f"You can still use the {config['env_var']} environment variable as a fallback.")
                
                return provider
                
            except KeyboardInterrupt:
                print("\nSetup cancelled.")
                raise

    @classmethod
    def get_provider_display_name(cls) -> str:
        """Get the display name of the provider for user prompts."""
        return "OpenAI"

    def validate_credentials(self) -> None:
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

    def generate_command(
        self, 
        question: str, 
        system_info: str, 
        model: Optional[str] = None, 
        debug: bool = False
    ) -> str:
        """
        Use OpenAI to convert a natural language question into a terminal command.

        Args:
            question: The user's natural language question.
            system_info: System information for context.
            model: The OpenAI model to use.
            debug: Whether to show debug information.

        Returns:
            The generated terminal command.

        Raises:
            OpenAIAPIError: If the API call fails.
        """
        if model is None:
            model = self.get_default_model()

        system_prompt = self._build_system_prompt(system_info)

        # Build the conversation
        conversation = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]

        # Show debug information if requested
        if debug:
            self._print_debug_conversation(conversation, model)

        try:
            response = self.client.responses.parse(
                model=model,
                input=conversation,
                text_format=CommandOutput,
            )

            command = response.output_parsed.command_line.strip()
            if not command:
                raise OpenAIAPIError("Empty command returned from API")

            return command

        except Exception as e:
            raise OpenAIAPIError(f"Error calling OpenAI API: {e}", e) from e

    def get_provider_name(self) -> str:
        """Get the name of the provider."""
        return "OpenAI"

    def get_default_model(self) -> str:
        """Get the default model for OpenAI."""
        # Import here to avoid circular imports
        from ..config import DEFAULT_MODEL
        return DEFAULT_MODEL

    def _print_debug_conversation(self, conversation: List[Dict[str, str]], model: str) -> None:
        """
        Print debug information about the conversation being sent to OpenAI.

        Args:
            conversation: The conversation messages.
            model: The model being used.
        """
        print("🔍 DEBUG: OpenAI API Request", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        print(f"Model: {model}", file=sys.stderr)
        print("-" * 50, file=sys.stderr)

        for i, message in enumerate(conversation, 1):
            role = message["role"].upper()
            content = message["content"]
            print(f"[{i}] {role}:", file=sys.stderr)
            print(content, file=sys.stderr)
            if i < len(conversation):
                print("-" * 30, file=sys.stderr)

        print("=" * 50, file=sys.stderr)
        print("", file=sys.stderr)

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
* The command should be ready to run directly in a terminal on the User's SHELL.
* If the question is ambiguous, choose the most common/useful interpretation
* Focus on practical, commonly used commands.
* Priority is to use built-in commands rather than bespoke code.
* If multiple commands are needed, separate them with &&
* Do not include markdown, backticks, or any other formatting

* The User has NO PACKAGES INSTALLED FOR LANGUAGES I.e. no libraries for Python, Node or Lua are available.  Only the functions available by default.

## Shell Shell Syntax Differences

## Zsh (default on macOS Catalina+)
- Similar to bash but with enhanced features
- Array indexing starts at 1: `array[1]` for first element
- Glob patterns are more powerful: `**` for recursive matching

## Bash
- Array indexing starts at 0: `array[0]` for first element
- Standard POSIX-compliant syntax
- Conditional syntax: `[[ ]]` for advanced conditions, `[ ]` for POSIX
- Command substitution: `$(command)` or backticks

## Fish (Friendly Interactive Shell)
- Significantly different syntax, not POSIX-compatible
- No variable assignments with `$`: use `set var value` instead of `var=value`
- Array indexing starts at 1: `array[1]`
- Conditionals use `if`, `else`, `end` blocks instead of brackets
- Functions defined with `function name` and ended with `end`
- No command substitution with `$()`: use `(command)` instead
- Logical operators: `and`, `or`, `not` instead of `&&`, `||`, `!`

## Key Migration Points
- Moving from bash to zsh is relatively seamless
- Fish requires learning new syntax patterns entirely
- Zsh offers the best of both worlds: bash compatibility with modern enhancements
- Fish prioritises user-friendliness over POSIX compliance

Most scripts written for bash will work in zsh with minimal modifications, whilst fish requires complete rewrites due to its unique approach to shell scripting.

### Step by Step:
1) Work out what SHELL the user is using. This is where the command will be run. The command must run in this SHELL i.e. don't assume the user is using BASH.
2) Work out which languages are available to the user
3) Work out the simplest, most straight-forward answer.  Less dependencies the better.

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

<question id="example-6">
literally show me the colors available in my terminal. I want to see all the shades etc. Use node.  In a table.  Add the corrisponding numbers
</question>

<wrong answer>
node -e 'console.log(require("chalk").keyword("list"))'
</wrong answer>

<reason>
assumed user has chalk installed.  User has no libraries installed. So this will fail
</reason>"""