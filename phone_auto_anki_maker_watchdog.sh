#!/bin/bash

file_to_watch="/home/twain/noteVault/tail/ankis_to_make.txt"
python_script="/home/twain/Projects/grammarpt/phone_auto_anki_maker.py"
log_file="/home/twain/Projects/grammarpt/watchdog.log"

echo "Watchdog started at $(date)" >> "$log_file"

while true; do
  # -q makes inotifywait quieter, only outputting event information
  inotify_output=$(inotifywait -q -e modify,attrib,move,close_write,create,delete,delete_self --timeout 10 "$file_to_watch" 2>&1)
  exit_status=$?
  
  if [ $exit_status -eq 0 ]; then
    echo "$(date): Change detected in $file_to_watch. Event: $inotify_output" >> "$log_file"
    echo "$(date): Calling Python script: $python_script" >> "$log_file"
    
    # Environment variables set directly for the command
    # The venv python should handle its own PYTHONPATH.
    # Ensure the script is executed from its directory for relative paths if any.
    # Using full paths for clarity and to avoid PATH issues.
    script_output=$(cd "/home/twain/Projects/grammarpt" && \
                    DISPLAY=:0 XAUTHORITY="/home/twain/.Xauthority" \
                    "/home/twain/Projects/grammarpt/venv/bin/python3" "$python_script" 2>&1)
    script_exit_status=$?
    
    echo "$(date): Python script finished with exit status $script_exit_status." >> "$log_file"
    if [ $script_exit_status -ne 0 ]; then
      echo "$(date): Python script output (if any):" >> "$log_file"
      echo "$script_output" >> "$log_file"
    else
      echo "$(date): Python script executed successfully. Output (if any):" >> "$log_file"
      echo "$script_output" >> "$log_file"
    fi
  elif [ $exit_status -eq 1 ]; then
    # inotifywait error (e.g., file deleted and recreated, or inotify limit)
    echo "$(date): inotifywait error. Exit status: $exit_status. Output: $inotify_output" >> "$log_file"
    # Consider adding a small delay here if this happens frequently
  elif [ $exit_status -eq 2 ]; then
    # Timeout, no event
    # echo "$(date): inotifywait timeout. No event." >> "$log_file" # Can be noisy
    : # Do nothing on timeout
  else
    echo "$(date): inotifywait returned unhandled exit status $exit_status. Output: $inotify_output" >> "$log_file"
  fi
done
