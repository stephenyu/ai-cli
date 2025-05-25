#!/usr/bin/env python3
"""
AI CLI - Convert natural language questions to terminal commands using OpenAI
"""

import argparse
import os
import sys
from openai import OpenAI
from pydantic import BaseModel


class CommandOutput(BaseModel):
    command_line: str


def get_terminal_command(question, client, model="gpt-4o-2024-08-06"):
    """
    Use OpenAI to convert a natural language question into a terminal command.
    """
    system_prompt = """# Identity

You are a terminal command expert that converts natural language questions into precise Unix/Linux/macOS terminal commands.

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
find . -name "*.py" -exec wc -l {} + | tail -1
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
        "--execute", "-e",
        action="store_true",
        help="Execute the command immediately (use with caution!)"
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-2024-08-06",
        help="OpenAI model to use (default: gpt-4o-2024-08-06)"
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
    
    # Print the command
    print(command)
    
    # Optionally execute the command
    if args.execute:
        print(f"\nExecuting: {command}", file=sys.stderr)
        os.system(command)


if __name__ == "__main__":
    main() 