# AI CLI - Terminal Command Generator

🤖 Convert natural language questions into precise terminal commands using OpenAI's latest API.

## ✨ What It Does

Transform questions like this:
- `"ls command sorted by last access"` → `ls -ltu`
- `"find all python files recursively"` → `find . -name "*.py" -type f`
- `"compress this directory"` → `tar -czf archive.tar.gz .`

## 🚀 Quick Installation

### 1. Get the Code
```bash
# Clone this repository
git clone https://github.com/your-username/ai-quick-cli.git
cd ai-quick-cli

# Or download and extract if you don't have git
```

### 2. Get Your OpenAI API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy it for the next step

### 3. Install Everything
```bash
# Run the automatic installer
chmod +x install.sh
./install.sh

# Set your OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
```

### 4. Test It Out
```bash
ai "list files sorted by size"
# Should output something like: ls -lhS
```

## 🎯 Usage Examples

### Basic Commands
```bash
# File operations
ai "list hidden files"                    # ls -la
ai "find large files over 100MB"          # find . -size +100M -type f
ai "count files in directory"             # find . -maxdepth 1 -type f | wc -l

# Process management  
ai "show running processes"                # ps aux
ai "kill all python processes"            # pkill python
ai "show memory usage"                     # free -h

# System information
ai "show disk space"                       # df -h
ai "check system uptime"                   # uptime
ai "show network connections"              # netstat -tuln

# Text processing
ai "count lines in all python files"      # find . -name "*.py" -exec wc -l {} +
ai "search for TODO in all files"         # grep -r "TODO" .
ai "replace tabs with spaces in file"     # sed 's/\t/    /g' filename
```

### Advanced Features
```bash
# Execute immediately (be careful!)
ai "show current directory size" --execute

# Use different AI model
ai "compress directory" --model gpt-4

# Get help
ai --help
```

## 📋 Prerequisites

- **Python 3.7+** (check with `python3 --version`)
- **OpenAI API Key** (with credits)
- **Internet connection**

## 🔧 Manual Installation

If the automatic installer doesn't work:

### 1. Install Python Dependencies
```bash
pip3 install openai pydantic
# or
pip3 install -r requirements.txt
```

### 2. Make Script Executable
```bash
chmod +x ai_cli.py
```

### 3. Add to Your PATH (choose one)

**Option A: Global installation**
```bash
sudo ln -sf $(pwd)/ai_cli.py /usr/local/bin/ai
```

**Option B: Add to your shell profile**
```bash
# For bash users
echo 'export PATH="'$(pwd)':$PATH"' >> ~/.bashrc
source ~/.bashrc

# For zsh users  
echo 'export PATH="'$(pwd)':$PATH"' >> ~/.zshrc
source ~/.zshrc

# For fish users
echo 'set -gx PATH '$(pwd)' $PATH' >> ~/.config/fish/config.fish
```

### 4. Set Your API Key Permanently
```bash
# For bash/zsh
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# For fish
echo 'set -gx OPENAI_API_KEY "your-api-key-here"' >> ~/.config/fish/config.fish
```

## ⚙️ Configuration

### Command Options
```bash
ai "your question"                    # Basic usage
ai "your question" --execute          # Run command immediately
ai "your question" --model gpt-4      # Use specific model
ai --help                            # Show help
```

### Environment Variables
- `OPENAI_API_KEY` - Your OpenAI API key (required)

### Supported Models
- `gpt-4o-2024-08-06` (default, recommended)
- `gpt-4`
- `gpt-3.5-turbo`

## 🛡️ Safety & Best Practices

### ⚠️ Important Safety Tips
1. **Always review commands before executing**
2. **Never use `--execute` with destructive commands without checking first**
3. **Start with simple, safe commands to test**
4. **Keep your API key secure and never commit it to version control**

### 💡 Pro Tips
- **Be specific**: "list python files by size descending" vs "list files"
- **Use quotes**: Wrap your entire question in quotes
- **Test first**: Run without `--execute` to see the command
- **Learn patterns**: Notice how the AI interprets different phrasings

## 🐛 Troubleshooting

### Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| `OPENAI_API_KEY not set` | Set the environment variable: `export OPENAI_API_KEY='your-key'` |
| `Command not found: ai` | Make sure script is in PATH or use `./ai_cli.py` |
| `Permission denied` | Run `chmod +x ai_cli.py` |
| `API Error: 401` | Check your API key is valid and has credits |
| `API Error: 429` | You've hit rate limits, wait a moment |
| `No module named 'openai'` | Install dependencies: `pip3 install -r requirements.txt` |

### Getting Help
```bash
# Check if Python is installed
python3 --version

# Check if dependencies are installed  
python3 -c "import openai, pydantic; print('Dependencies OK')"

# Test API key
python3 -c "import os; print('API key set:', bool(os.getenv('OPENAI_API_KEY')))"

# Test the script directly
./ai_cli.py "list files"
```

## 🎯 Use Cases

- **Learning**: Discover new terminal commands
- **Productivity**: Quickly get complex one-liners
- **System Administration**: Generate monitoring and maintenance commands
- **Development**: File operations, git commands, build scripts
- **Data Processing**: Text manipulation, file analysis

## 📊 Example Outputs

```bash
$ ai "show top 5 largest files"
find . -type f -exec ls -lh {} + | sort -k5 -hr | head -5

$ ai "kill process using port 8080"  
lsof -ti:8080 | xargs kill -9

$ ai "compress all log files older than 7 days"
find . -name "*.log" -mtime +7 -exec gzip {} \;

$ ai "show git commits from last week"
git log --since="1 week ago" --oneline
```

## 🤝 Contributing

Found a bug or want to add a feature?
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use and modify!

## 🙏 Credits

- Built with [OpenAI's API](https://openai.com/api/)
- Uses structured output with [Pydantic](https://pydantic.dev/)
- Inspired by the need for faster command discovery 