#!/bin/bash

# Set strict error handling
set -euo pipefail

# Function for logging messages with a timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function for error handling
error_handler() {
    local line_number=$1
    local error_code=$2
    log "Error occurred in line ${line_number} with exit code ${error_code}"
    exit "${error_code}"
}

# Set up error trap
trap 'error_handler ${LINENO} $?' ERR

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    log "ERROR: Python3 is not installed. Please install Python3 first."
    exit 1
fi

log "Starting the development environment setup."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    log "Virtual environment not found. Creating '.venv'..."
    if ! python3 -m venv .venv; then
        log "ERROR: Failed to create virtual environment."
        exit 1
    fi
    log "Virtual environment created successfully."
else
    log "Virtual environment '.venv' already exists. Skipping creation."
fi

# Check if virtual environment exists before activation
if [ ! -f ".venv/bin/activate" ]; then
    log "ERROR: Virtual environment activation script not found."
    exit 1
fi

# Activate the virtual environment
log "Activating virtual environment..."
source .venv/bin/activate || {
    log "ERROR: Failed to activate virtual environment."
    exit 1
}
log "Virtual environment activated."

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    log "ERROR: requirements.txt not found."
    exit 1
fi

# Upgrade pip to the latest version
log "Upgrading pip..."
if ! pip install --upgrade pip; then
    log "ERROR: Failed to upgrade pip."
    exit 1
fi
log "pip upgraded successfully."

# Install dependencies
log "Installing dependencies from requirements.txt..."
if ! pip3 install -r requirements.txt; then
    log "ERROR: Failed to install dependencies."
    exit 1
fi
log "Dependencies installed successfully from requirements.txt."

# Check if main.py exists
if [ ! -f "main.py" ]; then
    log "ERROR: main.py not found."
    exit 1
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    log "ERROR: Streamlit is not installed. Please check your requirements.txt."
    exit 1
fi

# Launch the Streamlit application
log "Launching the Streamlit application..."
if ! streamlit run main.py; then
    log "ERROR: Failed to launch Streamlit application."
    exit 1
fi
