# AI CLI

Convert natural language questions to terminal commands using AI.

## Features

- 🤖 Uses OpenAI, Claude, or OpenRouter to generate terminal commands — pick one provider at setup time
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

After installation, configure an AI provider:

```bash
ai setup
```

This will:
1. Ask which provider to use — OpenAI, Claude, or OpenRouter
2. Prompt for that provider's API key
3. Test the key against the live API
4. Optionally let you override the default model
5. Store the key securely in your system keyring

Only one provider is active at a time. Running `ai setup` again switches to
whichever provider you pick, overwriting the previous key.

Get an API key from:
- OpenAI: https://platform.openai.com/api-keys
- Claude (Anthropic): https://console.anthropic.com/settings/keys
- OpenRouter: https://openrouter.ai/keys

### Non-interactive setup

For scripting, pass the provider, key, and (optionally) model as flags:

```bash
ai setup --provider claude --api-key sk-ant-... --model claude-haiku-4-5-20251001
ai setup --provider openrouter --api-key sk-or-... --model anthropic/claude-3.5-haiku
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

### Other commands

```bash
# Check configuration status (active provider, model, and whether a key is set)
ai status

# Reset/remove the stored API key and provider/model config
ai reset

# Override the model for a single query (default: the active provider's configured model)
ai "your question" --model gpt-4
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

## Configuration

The AI CLI stores your API key securely using your system's keyring:

- **macOS**: Keychain
- **Linux**: Secret Service API (GNOME Keyring, KDE Wallet, etc.)
- **Windows**: Windows Credential Locker

Which provider and model are active is recorded separately, in
`~/.config/ai-cli/config.json` (no secrets live there — just the provider
name and model id).

You can also skip `ai setup` entirely and set the matching environment
variable for your provider as a fallback (used only when no key is stored
in the keyring):

- OpenAI: `OPENAI_API_KEY`
- Claude: `ANTHROPIC_API_KEY`
- OpenRouter: `OPENROUTER_API_KEY`

## Requirements

- Python 3.8+
- An API key for one of: OpenAI, Claude (Anthropic), or OpenRouter

## License

MIT License - see [LICENSE](LICENSE) file for details. 