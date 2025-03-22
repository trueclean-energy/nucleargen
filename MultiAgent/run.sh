#!/bin/bash

# Set environment variables
export GOOGLE_API_KEY="AIzaSyA6CAdYzTjFaRMRCxY57NqcgPhD0eSyLek"
export GEMINI_API_KEY="AIzaSyA6CAdYzTjFaRMRCxY57NqcgPhD0eSyLek"

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Start the application
echo "Starting MultiAgent demo at http://localhost:8000"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 