#!/bin/bash
# Speech Coach Application Startup Script

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if in correct directory
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found. Please run from speech_coach directory."
    exit 1
fi

# Start the application
echo "Starting Speech Coach Application..."
python main.py
