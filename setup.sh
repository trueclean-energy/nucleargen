#!/bin/bash

# Script to set up the virtual environment and install dependencies

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "Virtual environment activated and dependencies installed!"
echo "To activate the virtual environment in the future, run: source venv/bin/activate" 