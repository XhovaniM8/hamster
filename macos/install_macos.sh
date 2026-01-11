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
PYTHON_CMD=""
for py in python3.12 python3.11 python3; do
    if command -v $py &> /dev/null; then
        PYTHON_CMD=$py
        echo "✓ Found $py"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "Python 3.11 or later not found. Installing..."
    brew install python@3.11
    PYTHON_CMD=python3.11
fi
echo ""

echo "Step 4: Installing Python dependencies..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install PyGObject pycairo watchdog
echo "✓ Python dependencies installed"
echo ""

echo "Step 5: Testing installation..."
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if $PYTHON_CMD "$SCRIPT_DIR/test_macos_port.py"; then
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
echo "  or: $PYTHON_CMD src/hamster-cli.py"
echo ""
echo "For more information, see macos/README_MACOS.md"
echo ""
