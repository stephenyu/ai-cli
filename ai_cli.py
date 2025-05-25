#!/usr/bin/env python3
"""
AI CLI - Convert natural language questions to terminal commands using OpenAI
"""

import argparse
import os
import subprocess
import sys
import shutil
from openai import OpenAI
from pydantic import BaseModel

# Default OpenAI model to use
DEFAULT_MODEL = "gpt-4.1-nano-2025-04-14"


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
    parser.add_argument(
        "question",
        help="The question or description of what you want to do"
    )
    parser.add_argument(
        "--copy", "-c",
        action="store_true",
        help="Copy the command to clipboard"
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"OpenAI model to use (default: {DEFAULT_MODEL})"
    )
    
    args = parser.parse_args()
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        print("Please set your OpenAI API key:", file=sys.stderr)
        print("export OPENAI_API_KEY='your-api-key-here'", file=sys.stderr)
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