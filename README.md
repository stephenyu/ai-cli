# AI CLI

Convert natural language questions to terminal commands using OpenAI.

## Features

- 🤖 Uses OpenAI's latest models to generate terminal commands
- 🔒 Secure API key storage using system keyring
- 📋 Copy commands to clipboard
- 🖥️ Cross-platform support (macOS, Linux, Windows/WSL)
- 🔍 Context-aware command generation based on your system's available tools
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