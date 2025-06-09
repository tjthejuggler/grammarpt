#!/usr/bin/env python3
#be sure to make sh executable

import os
# Try to set DISPLAY, but don't crash if it's already set or invalid in some contexts
try:
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'
except Exception as e:
    print(f"[WARN] Could not set DISPLAY=:0 : {e}")

from subprocess import Popen, PIPE
# import os # Already imported
import openai
from openai import OpenAI
import subprocess
from AnkiConnector import AnkiConnector
import time
# from PIL import Image # Not currently used, can be removed if not planned
# import glob # Not currently used

# Optional GUI/Clipboard imports
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("[WARN] pyautogui not found or could not be imported. GUI interactions will be skipped.")
except Exception as e: # Catch other errors like X11 connection issues during import
    PYAUTOGUI_AVAILABLE = False
    print(f"[WARN] pyautogui could not be initialized: {e}. GUI interactions will be skipped.")

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    print("[WARN] pyperclip not found or could not be imported. Clipboard operations will be skipped.")
except Exception as e: # Catch other errors like X11/Wayland issues during import
    PYPERCLIP_AVAILABLE = False
    print(f"[WARN] pyperclip could not be initialized: {e}. Clipboard operations will be skipped.")


def notify(text):
    print(f"Notification: {text}") # Always print for logging
    try:
        # Only attempt notify-send if DISPLAY might be available.
        # This is a basic check; XAUTHORITY is also needed.
        if 'DISPLAY' in os.environ:
            msg = "notify-send ' ' '"+text+"'"
            subprocess.run(msg, shell=True, check=False, timeout=5) # Added timeout
        else:
            print("[INFO] DISPLAY not set, skipping notify-send.")
    except Exception as e:
        print(f"[WARN] notify-send command failed: {e}")

def construct_request(prompt, text):
    item = prompt+text
    return send_request([{"role":"user","content":item}])

def send_request(request_message):
    api_location = '~/Projects/grammarpt/deepseek_api.txt'
    api_location = os.path.expanduser(api_location)
    api_key = ""
    try:
        with open(api_location, 'r') as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        notify(f"ERROR: API key file not found at {api_location}")
        return "ERROR: API Key file not found."
    
    if not api_key:
        notify("ERROR: API key is empty.")
        return "ERROR: API Key is empty."

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=request_message,
            stream=False
        )
        corrected = response.choices[0].message.content.replace("\n","").strip().lstrip()
    except Exception as e:
        notify(f"ERROR: LLM API request failed: {e}")
        return f"ERROR: LLM API request failed: {e}"

    notify(f"LLM Response: {corrected}") # For logging what LLM sent before clipboard
    
    if PYPERCLIP_AVAILABLE:
        try:
            pyperclip.copy(corrected)
            print("[INFO] Copied LLM response to clipboard.")
        except Exception as e: # Catches pyperclip.PyperclipException and others
            print(f"[WARN] pyperclip.copy() failed: {e}. Skipping clipboard operation.")
    else:
        print("[INFO] pyperclip not available, skipping clipboard operation.")
    return corrected

ankti_to_make_location = '/home/twain/noteVault/tail/ankis_to_make.txt'

def main_processing():
    global card_creation_failed # Allow modification of global
    card_creation_failed = False 

    if not os.path.exists(ankti_to_make_location):
        notify(f"Input file not found: {ankti_to_make_location}. Nothing to process.")
        return

    if os.path.getsize(ankti_to_make_location) == 0:
        notify(f"Input file is empty: {ankti_to_make_location}. Nothing to process.")
        # No need to clear an already empty file if no cards were processed
        return

    processed_content = False
    with open(ankti_to_make_location, 'r') as f:
        content = f.read().strip()
        if not content:
            notify("Ankis_to_make file contains only whitespace after stripping.")
            return # No content to process
        
        chunks = content.split('\n\n')
        processed_content = True # Mark that we are attempting to process

    for chunk_idx, chunk in enumerate(chunks):
        if not chunk.strip():
            print(f"Skipping empty chunk {chunk_idx + 1}/{len(chunks)}.")
            continue
        
        print(f"Processing chunk {chunk_idx + 1}/{len(chunks)}: '{chunk[:70]}...'")
        fact = ""
        url = ""
        if '|' in chunk:
            parts = chunk.split('|', 1)
            fact = parts[0].strip()
            url = parts[1].strip() if len(parts) > 1 else ""
        else:
            fact = chunk.strip()
            url = ""

        if not (10 < len(fact) < 1000):
            notify(f"Fact length out of range (10-1000 chars) for chunk: '{fact[:70]}...'. Skipping.")
            card_creation_failed = True # Consider this a failure to prevent clearing if other cards succeed
            continue

        anki_response = construct_request("Make an Anki Flashcard from the following fact. You are free to use your own knowledge to make the card more professional. Label it Front: and Back: .\n\n", fact)
        
        if anki_response.startswith("ERROR:"): # Check for errors from send_request
            notify(f"Skipping card creation due to LLM error for fact: {fact[:50]}...")
            card_creation_failed = True
            continue

        front = None
        back = None

        if "**Front:**" in anki_response and "**Back:**" in anki_response:
            try:
                main_content = anki_response.split("**Front:**", 1)[1]
                front_text_parts = main_content.split("**Back:**", 1)
                front = front_text_parts[0].strip()
                back_content = front_text_parts[1].strip()
                if "---" in back_content: back = back_content.split("---", 1)[0].strip()
                elif "###" in back_content: back = back_content.split("###", 1)[0].strip()
                else: back = back_content
            except Exception as e:
                notify(f"Error parsing MD Anki response for fact '{fact[:50]}...': {e}")
                card_creation_failed = True
        elif "Front: " in anki_response and "Back: " in anki_response:
            try:
                main_content = anki_response.split("Front: ", 1)[1]
                front_text_parts = main_content.split("Back: ", 1)
                front = front_text_parts[0].strip()
                back_content = front_text_parts[1].strip()
                if "---" in back_content: back = back_content.split("---", 1)[0].strip()
                elif "###" in back_content: back = back_content.split("###", 1)[0].strip()
                else: back = back_content
            except Exception as e:
                notify(f"Error parsing plain Anki response for fact '{fact[:50]}...': {e}")
                card_creation_failed = True
        
        if front and back:
            source_url = url if url else ""
            if source_url and not source_url.startswith('http://') and not source_url.startswith('https://'):
                source_url = 'http://'+source_url
            
            deck_name = '...MyDiscoveries2'
            note_type = 'Basic'
            print(f"Attempting to add card to Anki. Deck: '{deck_name}', Front: '{front[:50]}...'")
            connector = AnkiConnector(deck_name=deck_name, note_type=note_type, allow_duplicate=False)
            if not connector.add_card(front, back, source_url):
                card_creation_failed = True
                notify(f"Failed to add card via AnkiConnect for fact: {fact[:50]}...")
            else:
                notify(f"Successfully added card for fact: {fact[:50]}...")
        else:
            notify(f"Could not parse Front/Back from Anki response for fact: {fact[:50]}... Response: {anki_response[:100]}")
            card_creation_failed = True

    if processed_content and not card_creation_failed:
        try:
            with open(ankti_to_make_location, 'w') as f:
                f.write('')
            notify("Successfully processed all chunks and cleared anki_to_make.txt")
        except Exception as e:
            notify(f"Error clearing anki_to_make.txt: {e}")
    elif card_creation_failed:
        notify("Card creation failed for one or more cards. anki_to_make.txt was NOT cleared.")
    # If not processed_content, file was empty/not found, so no clearing needed.

if __name__ == "__main__":
    notify("phone_auto_anki_maker.py executed directly.")
    main_processing()
    notify("phone_auto_anki_maker.py direct execution finished.")