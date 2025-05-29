#!/bin/bash

# Script to generate SHA256 for v0.2.0 release tarball
# This will be needed for the Homebrew formula

VERSION="0.3.0"
URL="https://github.com/stephenyu/ai-cli/archive/v${VERSION}.tar.gz"

echo "Downloading release tarball for v${VERSION}..."
curl -L -o "ai-cli-v${VERSION}.tar.gz" "${URL}"

echo "Generating SHA256..."
SHA256=$(shasum -a 256 "ai-cli-v${VERSION}.tar.gz" | cut -d' ' -f1)

echo ""
echo "SHA256 for v${VERSION}: ${SHA256}"
echo ""
echo "Update your Homebrew formula with:"
echo "  sha256 \"${SHA256}\""
echo ""

# Clean up
rm "ai-cli-v${VERSION}.tar.gz"
