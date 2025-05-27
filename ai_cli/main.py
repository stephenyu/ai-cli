#!/usr/bin/env python3
"""
AI CLI - Convert natural language questions to terminal commands using OpenAI
"""

import argparse
import os
import subprocess
import sys
import shutil
import getpass
import keyring
from openai import OpenAI
from pydantic import BaseModel

# Default OpenAI model to use
DEFAULT_MODEL = "gpt-4.1-nano-2025-04-14"

# Keyring service name for storing API key
KEYRING_SERVICE = "ai-cli"
KEYRING_USERNAME = "openai-api-key"


class CommandOutput(BaseModel):
    command_line: str


def get_system_info():
    """
    Get system information using uname -a to help the AI target the correct platform.
    """
    try:
        result = subprocess.run(['uname', '-a'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "Unknown system"
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        return "Unknown system"


def copy_to_clipboard(text):
    """
    Copy text to system clipboard using available tools.
    """
    try:
        # Try pbcopy (macOS)
        if shutil.which('pbcopy'):
            subprocess.run(['pbcopy'], input=text, text=True, check=True)
            return True
        # Try xclip (Linux)
        elif shutil.which('xclip'):
            subprocess.run(['xclip', '-selection', 'clipboard'], input=text, text=True, check=True)
            return True
        # Try xsel (Linux alternative)
        elif shutil.which('xsel'):
            subprocess.run(['xsel', '--clipboard', '--input'], input=text, text=True, check=True)
            return True
        # Try clip (Windows/WSL)
        elif shutil.which('clip'):
            subprocess.run(['clip'], input=text, text=True, check=True)
            return True
        else:
            return False
    except subprocess.SubprocessError:
        return False


def get_api_key():
    """
    Get OpenAI API key from keyring first, then fall back to environment variable.
    """
    # Try to get from keyring first
    try:
        api_key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
        if api_key:
            return api_key
    except Exception:
        # Keyring might not be available on some systems
        pass
    
    # Fall back to environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    return None


def store_api_key(api_key):
    """
    Store OpenAI API key securely in the system keyring.
    """
    try:
        keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, api_key)
        return True
    except Exception as e:
        print(f"Error storing API key in keyring: {e}", file=sys.stderr)
        return False


def remove_api_key():
    """
    Remove the stored API key from the keyring.
    """
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
        return True
    except Exception:
        # Key might not exist or keyring not available
        return False


def setup_command():
    """
    Interactive setup to configure the OpenAI API key.
    """
    print("🔧 AI CLI Setup")
    print("=" * 50)
    print()
    
    # Check if key already exists
    existing_key = get_api_key()
    if existing_key:
        print("✅ OpenAI API key is already configured.")
        response = input("Would you like to update it? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Setup cancelled.")
            return
        print()
    
    print("Please enter your OpenAI API key.")
    print("You can find your API key at: https://platform.openai.com/api-keys")
    print()
    
    # Get API key from user (hidden input)
    while True:
        api_key = getpass.getpass("OpenAI API Key: ").strip()
        
        if not api_key:
            print("❌ API key cannot be empty. Please try again.")
            continue
        
        # Basic validation - OpenAI keys start with 'sk-'
        if not api_key.startswith('sk-'):
            print("⚠️  Warning: API key doesn't look like a valid OpenAI key (should start with 'sk-')")
            response = input("Continue anyway? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                continue
        
        break
    
    print()
    print("🔍 Testing API key...")
    
    # Test the API key
    try:
        client = OpenAI(api_key=api_key)
        # Make a simple API call to test the key
        response = client.models.list()
        if response:
            print("✅ API key is valid!")
        else:
            print("❌ API key test failed.")
            return
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        response = input("Store the key anyway? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Setup cancelled.")
            return
    
    print()
    print("💾 Storing API key securely...")
    
    # Store the API key
    if store_api_key(api_key):
        print("✅ API key stored securely in system keyring!")
        print()
        print("🎉 Setup complete! You can now use the 'ai' command.")
        print("Example: ai 'list all python files'")
    else:
        print("❌ Failed to store API key securely.")
        print("You can still use the OPENAI_API_KEY environment variable as a fallback.")


def status_command():
    """
    Show the current configuration status.
    """
    print("🔍 AI CLI Status")
    print("=" * 50)
    print()
    
    # Check keyring storage
    try:
        stored_key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
        if stored_key:
            # Mask the key for security
            masked_key = stored_key[:8] + "..." + stored_key[-4:] if len(stored_key) > 12 else "***"
            print(f"✅ API Key (keyring): {masked_key}")
        else:
            print("❌ No API key found in keyring")
    except Exception:
        print("❌ Keyring not available")
    
    # Check environment variable
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        masked_env_key = env_key[:8] + "..." + env_key[-4:] if len(env_key) > 12 else "***"
        print(f"✅ API Key (env var): {masked_env_key}")
    else:
        print("❌ No OPENAI_API_KEY environment variable")
    
    print()
    
    # Overall status
    final_key = get_api_key()
    if final_key:
        print("✅ AI CLI is ready to use!")
    else:
        print("❌ No API key configured. Run 'ai setup' to get started.")


def reset_command():
    """
    Remove stored API key and reset configuration.
    """
    print("🗑️  AI CLI Reset")
    print("=" * 50)
    print()
    
    existing_key = get_api_key()
    if not existing_key:
        print("❌ No API key is currently configured.")
        return
    
    print("⚠️  This will remove your stored OpenAI API key.")
    response = input("Are you sure? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        if remove_api_key():
            print("✅ API key removed successfully.")
        else:
            print("⚠️  Could not remove API key from keyring (it may not have been stored there).")
        print("Reset complete.")
    else:
        print("Reset cancelled.")


def get_terminal_command(question, client, model=DEFAULT_MODEL):
    """
    Use OpenAI to convert a natural language question into a terminal command.
    """
    # Get system information to help target the correct platform
    system_info = get_system_info()
    
    system_prompt = f"""# Identity

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

    try:
        response = client.responses.parse(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            text_format=CommandOutput,
        )
        
        command = response.output_parsed.command_line.strip()
        return command
    
    except Exception as e:
        print(f"Error calling OpenAI API: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Convert natural language questions to terminal commands using AI",
        prog="ai"
    )
    
    # Add version argument
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="0.2.0"
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup subcommand
    setup_parser = subparsers.add_parser('setup', help='Configure OpenAI API key')
    
    # Status subcommand
    status_parser = subparsers.add_parser('status', help='Show configuration status')
    
    # Reset subcommand
    reset_parser = subparsers.add_parser('reset', help='Remove stored API key')
    
    # Query subcommand (default behavior)
    query_parser = subparsers.add_parser('query', help='Ask a question (default)')
    query_parser.add_argument(
        "question",
        help="The question or description of what you want to do"
    )
    query_parser.add_argument(
        "--copy", "-c",
        action="store_true",
        help="Copy the command to clipboard"
    )
    query_parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"OpenAI model to use (default: {DEFAULT_MODEL})"
    )
    
    # Handle the case where no subcommand is given (treat as query)
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    # If first argument doesn't look like a subcommand, treat it as a query
    if len(sys.argv) > 1 and sys.argv[1] not in ['setup', 'status', 'reset', 'query']:
        # Insert 'query' as the first argument
        sys.argv.insert(1, 'query')
    
    args = parser.parse_args()
    
    # Handle different commands
    if args.command == 'setup':
        setup_command()
        return
    
    if args.command == 'status':
        status_command()
        return
    
    if args.command == 'reset':
        reset_command()
        return
    
    if args.command == 'query':
        # Check for OpenAI API key
        api_key = get_api_key()
        if not api_key:
            print("❌ No OpenAI API key configured.", file=sys.stderr)
            print("Run 'ai setup' to configure your API key, or set the OPENAI_API_KEY environment variable.", file=sys.stderr)
            sys.exit(1)
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Get the terminal command
        command = get_terminal_command(args.question, client, args.model)
        
        if command is None:
            sys.exit(1)
        
        # Handle different output modes
        if args.copy:
            # Copy to clipboard mode
            print(command)
            if copy_to_clipboard(command):
                print("✅ Command copied to clipboard! Paste and press Enter to execute.", file=sys.stderr)
            else:
                print("❌ Could not copy to clipboard. Please copy the command manually.", file=sys.stderr)
        else:
            # Default: just print the command
            print(command)


if __name__ == "__main__":
    main() 