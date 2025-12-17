#!/bin/bash

# Setup script for Crypto Backtesting Engine

echo "======================================================================"
echo "Crypto Backtesting Engine - Setup"
echo "======================================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "======================================================================"
echo "Setup Complete!"
echo "======================================================================"
echo ""
echo "To get started:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Verify setup:"
echo "     python verify_setup.py"
echo ""
echo "  3. Run quick demo:"
echo "     python quickstart.py"
echo ""
echo "  4. Or run full application:"
echo "     python main.py"
echo ""
echo "======================================================================"
