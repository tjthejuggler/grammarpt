#!/bin/bash
# Script to extract JSON from clipboard and run json_to_anki.py with it

# Get clipboard contents (supports xclip and xsel)
if command -v xclip &> /dev/null; then
    CLIP=$(xclip -selection clipboard -o)
elif command -v xsel &> /dev/null; then
    CLIP=$(xsel --clipboard)
else
    echo "xclip or xsel required"
    exit 1
fi

echo "=== Clipboard contents ==="
echo "$CLIP"
echo "=== End clipboard contents ==="

# Write clipboard content to a temp file (let Python handle JSON extraction)
TMPFILE=$(mktemp /tmp/anki_json.XXXXXX.json)
echo "$CLIP" > "$TMPFILE"

# Run the Python app (assumes script is in ~/Projects/grammarpt)
python3 ~/Projects/grammarpt/json_to_anki.py "$TMPFILE"

# Clean up
rm "$TMPFILE"