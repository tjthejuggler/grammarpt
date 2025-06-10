#!/bin/bash

# Set the path to the script
SCRIPT_PATH="/home/twain/Projects/grammarpt/define_selected.py"

# Set the path to the virtual environment
VENV_PATH="/home/twain/Projects/grammarpt/venv"

# Activate the virtual environment
source "/home/twain/Projects/grammarpt/venv/bin/activate"

# Run the script
/home/twain/Projects/grammarpt/venv/bin/python "$SCRIPT_PATH"

# Deactivate the virtual environment
deactivate