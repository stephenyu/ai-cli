#!/usr/bin/env python3
"""
AI CLI - Convert natural language questions to terminal commands using OpenAI

Refactored main module using modular architecture.
"""

import argparse
import sys
from importlib.metadata import version, PackageNotFoundError

from .config import DEFAULT_MODEL, DEFAULT_PROVIDER
from .commands import SetupCommand, StatusCommand, ResetCommand, QueryCommand
from .providers.factory import ProviderFactory


def get_version() -> str:
    """Get the version of the ai-cli package."""
    try:
        return version("ai-cli")
    except PackageNotFoundError:
        return "unknown"


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="Convert natural language questions to terminal commands using AI",
        prog="ai"
    )
    
    # Add version flag
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"ai-cli {get_version()}"
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup subcommand
    setup_parser = subparsers.add_parser('setup', help='Configure AI provider API key')
    setup_parser.add_argument(
        "--provider",
        default=DEFAULT_PROVIDER,
        choices=ProviderFactory.get_available_providers(),
        help=f"AI provider to configure (default: {DEFAULT_PROVIDER})"
    )
    
    # Status subcommand
    subparsers.add_parser('status', help='Show configuration status')
    
    # Reset subcommand
    subparsers.add_parser('reset', help='Remove stored API key')
    
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
        help="Model to use (uses provider default if not specified)"
    )
    query_parser.add_argument(
        "--provider",
        default=DEFAULT_PROVIDER,
        choices=ProviderFactory.get_available_providers(),
        help=f"AI provider to use (default: {DEFAULT_PROVIDER})"
    )
    query_parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Show debug information including the conversation sent to the AI provider"
    )
    
    return parser


def handle_implicit_query(args: list) -> list:
    """
    Handle the case where user provides a question without the 'query' subcommand.
    
    Args:
        args: Command line arguments.
        
    Returns:
        Modified arguments with 'query' inserted if needed.
    """
    if len(args) == 1:
        return args  # Just the program name, let parser handle help
    
    # Don't modify arguments if they contain version flags or help flags
    version_flags = {'-V', '--version', '-h', '--help'}
    if any(arg in version_flags for arg in args[1:]):
        return args
    
    # If first argument doesn't look like a subcommand, treat it as a query
    known_commands = {'setup', 'status', 'reset', 'query'}
    if args[1] not in known_commands:
        # Insert 'query' as the first argument
        return args[:1] + ['query'] + args[1:]
    
    return args


def main():
    """Main entry point for the AI CLI."""
    # Handle implicit query syntax (e.g., `ai "list files"` instead of `ai query "list files"`)
    modified_args = handle_implicit_query(sys.argv)
    
    # Parse arguments
    parser = create_parser()
    
    # Show help if no arguments
    if len(modified_args) == 1:
        parser.print_help()
        sys.exit(1)
    
    # Parse with potentially modified arguments
    args = parser.parse_args(modified_args[1:])
    
    # Route to appropriate command handler
    try:
        if args.command == 'setup':
            SetupCommand().execute(provider=args.provider)
        elif args.command == 'status':
            StatusCommand().execute()
        elif args.command == 'reset':
            ResetCommand().execute()
        elif args.command == 'query':
            QueryCommand().execute(
                question=args.question,
                copy_to_clipboard=args.copy,
                model=args.model,
                debug=args.debug,
                provider=args.provider
            )
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 