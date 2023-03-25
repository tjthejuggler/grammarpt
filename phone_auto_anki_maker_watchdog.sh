#!/bin/bash

file_to_watch="$HOME/Documents/obsidian_note_vault/noteVault/ankis_to_make.txt"
python_script="$HOME/projects/grammarpt/phone_auto_anki_maker.py"

while true; do
  inotifywait -e modify,attrib,move,close_write,create,delete,delete_self --timeout 10 "$file_to_watch"
  if [ $? -eq 0 ]; then
    python3 "$python_script"
  fi
done
