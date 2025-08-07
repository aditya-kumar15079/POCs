#!/bin/bash

# Absolute path to your project folder
PROJECT_DIR="/home/aditya.kumar2@happiestminds.com/Projects/GBSPOL01/electron-test-runner/Test-Foundry/TestFoundry_Framework"
VENV_DIR="$PROJECT_DIR/venv"
SRC_DIR="$PROJECT_DIR/src"

# Change to project directory first
cd "$PROJECT_DIR" || { echo "Failed to cd to $PROJECT_DIR"; exit 1; }

# Activate virtual environment (absolute path)
source "$VENV_DIR/bin/activate"

# Run python script
python3 "$SRC_DIR/main.py

