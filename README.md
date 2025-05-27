# AI CLI

Convert natural language questions to terminal commands using OpenAI.

## Features

- 🤖 Uses OpenAI's latest models to generate terminal commands
- 🔒 Secure API key storage using system keyring
- 📋 Copy commands to clipboard
- 🖥️ Cross-platform support (macOS, Linux, Windows/WSL)
- ⚡ Fast and simple to use

## Installation

### Via Homebrew (macOS/Linux)

```bash
# Add the tap
brew tap stephenyu/tap

# Install AI CLI
brew install ai-cli
```

Or in one command:
```bash
brew install stephenyu/tap/ai-cli
```

### From source

```bash
git clone https://github.com/stephenyu/ai-cli.git
cd ai-cli
pip install .
```

## Setup

After installation, configure your OpenAI API key:

```bash
ai setup
```

This will:
1. Prompt for your OpenAI API key
2. Test the API key
3. Store it securely in your system keyring

Get your API key from: https://platform.openai.com/api-keys

## Usage

### Basic usage

```bash
ai "list all python files"
# Output: find . -name "*.py" -type f

ai "show disk usage"
# Output: du -sh .

ai "find large files over 100MB"
# Output: find . -size +100M -type f
```

### Copy to clipboard

```bash
ai -c "compress this directory"
# Output: tar -czf archive.tar.gz .
# ✅ Command copied to clipboard! Paste and press Enter to execute.
```

### Other commands

```bash
# Check configuration status
ai status

# Reset/remove stored API key
ai reset

# Use a specific model
ai --model gpt-4 "your question"
```

## Examples

```bash
# File operations
ai "find all files modified in the last 7 days"
ai "count lines of code in python files"
ai "make a directory called backup"

# System monitoring
ai "show running processes"
ai "check memory usage"
ai "show network connections"

# Git operations
ai "add all files to git"
ai "create a new branch called feature"
ai "show git log for last 5 commits"

# Package management
ai "install requests with pip"
ai "update all npm packages"
ai "list installed homebrew packages"
```

## Configuration

The AI CLI stores your OpenAI API key securely using your system's keyring:

- **macOS**: Keychain
- **Linux**: Secret Service API (GNOME Keyring, KDE Wallet, etc.)
- **Windows**: Windows Credential Locker

You can also use the `OPENAI_API_KEY` environment variable as a fallback.

## Requirements

- Python 3.8+
- OpenAI API key

## License

MIT License - see [LICENSE](LICENSE) file for details. 