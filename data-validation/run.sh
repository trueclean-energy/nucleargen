#!/bin/bash

# Change to the project root directory
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    # Activate the virtual environment
    source venv/bin/activate
fi

# Go back to the data-validation directory and run the app
cd data-validation
echo "Starting Flask app on http://localhost:5001"
python app.py 