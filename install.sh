#!/bin/bash

# AI CLI Installation Script

echo "🤖 Installing AI CLI..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Make the script executable
chmod +x ai_cli.py

# Create a symlink in /usr/local/bin (requires sudo)
echo "🔗 Creating symlink in /usr/local/bin..."
if [ -w "/usr/local/bin" ]; then
    ln -sf "$(pwd)/ai_cli.py" /usr/local/bin/ai
    echo "✅ AI CLI installed successfully!"
else
    echo "⚠️  Creating symlink requires sudo access:"
    sudo ln -sf "$(pwd)/ai_cli.py" /usr/local/bin/ai
    if [ $? -eq 0 ]; then
        echo "✅ AI CLI installed successfully!"
    else
        echo "❌ Failed to create symlink. You can manually add this to your PATH:"
        echo "   export PATH=\"$(pwd):\$PATH\""
    fi
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Set your OpenAI API key:"
echo "   export OPENAI_API_KEY='your-api-key-here'"
echo ""
echo "2. Try it out:"
echo "   ai \"ls command sorted by last access\""
echo ""
echo "💡 Pro tip: Use 'ai --help' to see all available options" 