#!/bin/bash
# Installation script for Hamster Time Tracker on macOS

set -e  # Exit on error

echo "============================================"
echo "Hamster Time Tracker - macOS Installation"
echo "============================================"
echo ""

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "Error: This script is for macOS only"
    exit 1
fi

echo "Step 1: Checking Homebrew..."
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Please install from https://brew.sh"
    exit 1
fi
echo "✓ Homebrew is installed"
echo ""

echo "Step 2: Installing system dependencies..."
echo "This may take a few minutes..."
brew install gtk+3 adwaita-icon-theme
echo "✓ GTK3 and Adwaita icons installed"
echo ""

echo "Step 3: Checking Python..."
if ! command -v python3.11 &> /dev/null; then
    echo "Python 3.11 not found. Installing..."
    brew install python@3.11
fi
echo "✓ Python 3.11 is available"
echo ""

echo "Step 4: Installing Python dependencies..."
pip3 install PyGObject pycairo watchdog
echo "✓ Python dependencies installed"
echo ""

echo "Step 5: Testing installation..."
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if python3.11 "$SCRIPT_DIR/test_macos_port.py"; then
    echo "✓ All tests passed!"
else
    echo "⚠ Some tests failed. The app may still work, but please check the output above."
fi
echo ""

echo "============================================"
echo "Installation complete!"
echo "============================================"
echo ""
echo "To run Hamster Time Tracker:"
echo "  ./macos/hamster"
echo "  or: python3.11 src/hamster-cli.py"
echo ""
echo "For more information, see macos/README_MACOS.md"
echo ""
