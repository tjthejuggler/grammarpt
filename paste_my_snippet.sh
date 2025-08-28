#!/bin/bash

# Path to your text file
SNIPPET_FILE="$(dirname "$(realpath "$0")")/my_large_snippet.txt"

# Put the content of the file into the clipboard
xclip -selection clipboard -i < "$SNIPPET_FILE"

# Wait a tiny moment for the clipboard to be ready
sleep 0.1

# Simulate Ctrl+V to paste
xdotool key --clearmodifiers ctrl+v