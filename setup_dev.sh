#!/bin/bash
# Exit immediately if a command exits with a non-zero status,
# if an undefined variable is used, or if any command in a pipeline fails.
set -euo pipefail

# Function to print messages with a timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Starting the development environment setup."

# Check if the virtual environment directory exists; create if it doesn't.
if [ ! -d ".venv" ]; then
    log "Virtual environment not found. Creating .venv..."
    python -m venv .venv
    log "Virtual environment created."
else
    log "Virtual environment '.venv' already exists. Skipping creation."
fi

# Activate the virtual environment.
log "Activating virtual environment..."
# shellcheck disable=SC1091
source .venv/bin/activate
log "Virtual environment activated."

# Upgrade pip to the latest version.
log "Upgrading pip..."
pip install --upgrade pip
log "pip upgraded successfully."

# Install required dependencies.
log "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
log "Dependencies from requirements.txt installed."

log "Installing development dependencies from requirements-dev.txt..."
pip install -r requirements-dev.txt
log "Development dependencies installed."

# Setup pre-commit hooks.
log "Setting up pre-commit hooks..."
pre-commit install
log "Pre-commit hooks set up successfully."

log "Development environment setup complete!"

# Run the Streamlit app.
log "Launching the Streamlit application..."
streamlit run main.py
