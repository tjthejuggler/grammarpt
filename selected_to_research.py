import subprocess
import os
from datetime import datetime

def notify(text):
    print(f"Notification: {text}")  # Always print for logging
    try:
        if 'DISPLAY' in os.environ:
            msg = "notify-send ' ' '"+text+"'"
            subprocess.run(msg, shell=True, check=False, timeout=5)
        else:
            print("[INFO] DISPLAY not set, skipping notify-send.")
    except Exception as e:
        print(f"[WARN] notify-send command failed: {e}")

def selected_to_research():
    try:
        # Try using xclip to get the selected text
        try:
            selected_text = subprocess.check_output(['xclip', '-selection', 'primary', '-o']).decode('utf-8').strip()
        except FileNotFoundError:
            # If xclip is not found, try using xsel
            try:
                selected_text = subprocess.check_output(['xsel', '-p']).decode('utf-8').strip()
            except FileNotFoundError:
                notify("Neither xclip nor xsel is installed. Please install one of them.")
                return

        if not selected_text:
            notify("No text selected.")
            return

        # Get current date and time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Path to the ToResearch.md file
        research_file = "/home/twain/noteVault/ToResearch.md"
        
        # Read existing content if file exists
        existing_content = ""
        if os.path.exists(research_file):
            with open(research_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # Create new content with timestamp, selected text, empty line, then existing content
        new_content = f"{current_time}\n{selected_text}\n\n{existing_content}"
        
        # Write the new content to the file
        with open(research_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        notify(f"Added to research file: {selected_text[:50]}{'...' if len(selected_text) > 50 else ''}")

    except Exception as e:
        notify(f"An error occurred: {e}")

if __name__ == "__main__":
    selected_to_research()