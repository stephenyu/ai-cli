# AI CLI

Convert natural language questions to terminal commands using AI providers (OpenAI, Ollama).

## Features

- 🤖 **Multiple AI Providers** - Support for OpenAI and Ollama (local LLM)
- 🔒 **Secure Storage** - API keys stored securely using system keyring
- 📋 **Clipboard Integration** - Copy commands to clipboard with `-c` flag
- 🖥️ **Cross-Platform** - Works on macOS, Linux, Windows/WSL
- 🔍 **Context-Aware** - Command generation based on your system's available tools
- 🐛 **Debug Mode** - See the full conversation sent to the AI provider
- ⚡ **Fast & Simple** - Quick setup and intuitive usage
- 🔧 **Provider Selection** - Choose your preferred AI provider during setup or per query

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

## Development

If you're developing or contributing to the AI CLI, you have several options to run the application:

### Option 1: Run as a module (recommended for development)

```bash
# Install dependencies
pip install -r requirements.txt

# Run directly from source
python -m ai_cli.main "your question here"
python -m ai_cli.main setup
python -m ai_cli.main status
```

**Note:** The `-m` flag is required because the codebase uses relative imports. Running `python ai_cli/main.py` directly will fail with import errors.

### Option 2: Development installation

```bash
# Install in editable/development mode
pip install -e .

# Now you can use the 'ai' command normally
ai "your question here"
ai setup
ai status
```

This is the cleanest approach as it eliminates runtime warnings and matches the production usage.

### Running tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=ai_cli
```

## Setup

After installation, configure your AI provider:

```bash
ai setup
```

This will:
1. Let you choose between OpenAI and Ollama providers
2. Prompt for your API key or configuration
3. Test the connection
4. Store credentials securely in your system keyring

### Provider-Specific Setup

**OpenAI:**
- Get your API key from: https://platform.openai.com/api-keys
- Setup will prompt for API key and test connectivity

**Ollama:**
- Install Ollama locally: https://ollama.ai/
- Ensure Ollama is running: `ollama serve`
- Setup will configure connection to local Ollama instance

You can also specify the provider during setup:
```bash
ai setup --provider openai
ai setup --provider ollama
```

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

### Advanced options

```bash
# Check configuration status
ai status

# Reset/remove stored API key
ai reset

# Use a specific model
ai --model gpt-4o "your question"

# Use a different provider
ai --provider ollama "your question"

# Debug mode (show full conversation)
ai --debug "your question"

# Combine options
ai --provider openai --model gpt-4o --copy --debug "compress this directory"
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

## Releases (For Developers)

### Automated Release Process

Use the provided release script for a streamlined release process:

```bash
# Create a new release (e.g., version 0.4.0)
./release.sh 0.4.0
```

This script will:
1. ✅ Validate version format and check for uncommitted changes
2. 🔄 Update version in `pyproject.toml` and `generate_release_sha.sh`
3. 🏗️ Build the package and run tests
4. 📝 Commit version changes
5. 🏷️ Create and push an annotated Git tag
6. 📋 Generate a release notes template
7. 💡 Provide next steps for GitHub release creation

**Prerequisites:**
- Clean working directory (no uncommitted changes)
- Python development dependencies installed
- Push access to the repository

### Manual Release Process

If you prefer to create releases manually:

```bash
# Create an annotated tag (recommended for releases)
git tag -a v0.4.0 -m "Release version 0.4.0"

# Or create a lightweight tag
git tag v0.4.0

# Push the tag to GitHub
git push origin v0.4.0

# Push all tags
git push --tags
```

### GitHub Release Creation

After creating and pushing a tag:

1. Go to [GitHub Releases](https://github.com/stephenyu/ai-cli/releases/new)
2. Select your tag (e.g., `v0.4.0`)
3. Fill in the release title and description
4. Publish the release

### Homebrew Formula Update

After creating a GitHub release, update the Homebrew formula:

```bash
# Generate SHA256 for the new release
./generate_release_sha.sh

# Update your Homebrew tap repository with the new version and SHA
```

### Release Checklist

- [ ] All tests pass (`pytest`)
- [ ] Version updated in `pyproject.toml`
- [ ] Version updated in `generate_release_sha.sh`
- [ ] Tag created and pushed
- [ ] GitHub release published
- [ ] Homebrew formula updated
- [ ] Release notes documented

## How It Works

AI CLI provides context-aware command generation by automatically gathering information about your system:

- **Operating System**: Detects your OS and kernel version using `uname -a`
- **Shell Environment**: Identifies your current shell from `$SHELL` variable
- **Available Tools**: Checks for common development tools and their versions:
  - **Node.js**: Detects `node` command and version
  - **Python**: Finds `python3` or `python` command and version
  - **Lua**: Checks for `lua` command and version

This context helps the AI generate more accurate commands. For example:
- Uses `python3` instead of `python` if only Python 3 is available
- Suggests Node.js commands only when Node.js is installed
- Provides shell-specific syntax when needed

## Configuration

The AI CLI stores your provider credentials securely using your system's keyring:

- **macOS**: Keychain
- **Linux**: Secret Service API (GNOME Keyring, KDE Wallet, etc.)
- **Windows**: Windows Credential Locker

### Environment Variables

You can also use environment variables as fallbacks:

- **OpenAI**: `OPENAI_API_KEY` - Your OpenAI API key
- **Ollama**: `OLLAMA_CONFIG` - JSON configuration for Ollama (optional)

### Provider Configuration

**OpenAI:**
- Requires API key from https://platform.openai.com/api-keys
- Default model: `gpt-4.1-nano-2025-04-14`
- Supports all OpenAI chat models

**Ollama:**
- Requires local Ollama installation
- Default URL: `http://localhost:11434/api/generate`
- Default model: `llama2`
- Supports any model available in your Ollama instance

## Requirements

- Python 3.8+
- **For OpenAI**: API key from https://platform.openai.com/api-keys
- **For Ollama**: Local Ollama installation (https://ollama.ai/)

## License

MIT License - see [LICENSE](LICENSE) file for details. 