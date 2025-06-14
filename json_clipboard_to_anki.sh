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

# Extract JSON array from clipboard (first match, even if surrounded by other text)
JSON=$(echo "$CLIP" | perl -0777 -ne 'print $1 if /(\[.*?\])/s')
if [ -z "$JSON" ]; then
    echo "[DEBUG] First regex failed, trying greedy match..."
    JSON=$(echo "$CLIP" | perl -0777 -ne 'print $1 if /(\[.*\])/s')
fi

if [ -z "$JSON" ]; then
    echo "[DEBUG] Greedy regex also failed."
    echo "No JSON array found in clipboard."
    exit 1
fi

echo "=== Extracted JSON ==="
echo "$JSON"
echo "=== End extracted JSON ==="

# Write to a temp file
TMPFILE=$(mktemp /tmp/anki_json.XXXXXX.json)
echo "$JSON" > "$TMPFILE"

# Run the Python app (assumes script is in ~/Projects/grammarpt)
python3 ~/Projects/grammarpt/json_to_anki.py "$TMPFILE"

# Clean up
rm "$TMPFILE"