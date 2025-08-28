#!/bin/bash
# AI Tutor JSON to Anki - Shell Script Wrapper
# Usage: ./ai_tutor_json_to_anki.sh <json_file> [deck_name]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/ai_tutor_json_to_anki.py"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <json_file> [deck_name]"
    echo "Example: $0 my_cards.json"
    echo "Example: $0 my_cards.json MyCustomDeck"
    exit 1
fi

# Check if JSON file exists
if [ ! -f "$1" ]; then
    echo "Error: JSON file '$1' not found."
    exit 1
fi

# Run the Python script
python3 "$PYTHON_SCRIPT" "$@"