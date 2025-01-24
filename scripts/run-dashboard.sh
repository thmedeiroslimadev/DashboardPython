#!/bin/bash

PROJECT_DIR="/home/quality/DashboardPython"
VENV_DIR="$PROJECT_DIR/venv"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Warning: Running as root. Consider running as a regular user."
fi

# Change to project directory
cd "$PROJECT_DIR" || {
    echo "Error: Could not change to project directory"
    exit 1
}

# Activate virtual environment
source "$VENV_DIR/bin/activate" || {
    echo "Error: Could not activate virtual environment"
    exit 1
}

# Run the dashboard
python3 dashboard.py

# Deactivate virtual environment
deactivate