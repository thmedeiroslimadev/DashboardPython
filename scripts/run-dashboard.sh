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

# Check for background parameter
if [[ "$1" == "--background" ]]; then
    echo "Starting the dashboard in background..."
    nohup python3 dashboard.py > ../logs/dashboard.log 2>&1 &
    echo "Dashboard running in background. Logs: dashboard.log"
else
    echo "Starting the dashboard in the terminal..."
    python3 dashboard.py
fi

# Deactivate virtual environment
deactivate
