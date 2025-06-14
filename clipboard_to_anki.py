import subprocess
import re
import sys
import os
from AnkiConnector import AnkiConnector
from openai import OpenAI
from anki_utils import ensure_anki_running

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

    return corrected

def construct_request(prompt, text):
    item = prompt + text
    return send_request([{"role":"user","content":item}])

def clipboard_to_anki():
    try:
        # Try using xclip to get the selected text
        try:
            fact = subprocess.check_output(['xclip', '-selection', 'primary', '-o']).decode('utf-8').strip()
        except FileNotFoundError:
            # If xclip is not found, try using xsel
            try:
                fact = subprocess.check_output(['xsel', '-p']).decode('utf-8').strip()
            except FileNotFoundError:
                notify("Neither xclip nor xsel is installed. Please install one of them.")
                return

        if not fact:
            notify("No text selected.")
            return

        if not (10 < len(fact) < 1000):
            notify(f"Fact length out of range (10-1000 chars). Current length: {len(fact)}")
            return

        # Notify user that processing has started
        notify(f"Processing fact: {fact[:100]}{'...' if len(fact) > 100 else ''}")

        # Use LLM to generate Anki card
        anki_response = construct_request("Make an Anki Flashcard from the following fact. You are free to use your own knowledge to make the card more professional. Label it Front: and Back: .\n\n", fact)
        
        if anki_response.startswith("ERROR:"):
            notify(f"LLM error: {anki_response}")
            return

        front = None
        back = None

        # Parse the LLM response
        if "**Front:**" in anki_response and "**Back:**" in anki_response:
            try:
                main_content = anki_response.split("**Front:**", 1)[1]
                front_text_parts = main_content.split("**Back:**", 1)
                front = front_text_parts[0].strip()
                back_content = front_text_parts[1].strip()
                if "---" in back_content: 
                    back = back_content.split("---", 1)[0].strip()
                elif "###" in back_content: 
                    back = back_content.split("###", 1)[0].strip()
                else: 
                    back = back_content
            except Exception as e:
                notify(f"Error parsing MD Anki response: {e}")
                return
        elif "Front: " in anki_response and "Back: " in anki_response:
            try:
                main_content = anki_response.split("Front: ", 1)[1]
                front_text_parts = main_content.split("Back: ", 1)
                front = front_text_parts[0].strip()
                back_content = front_text_parts[1].strip()
                if "---" in back_content: 
                    back = back_content.split("---", 1)[0].strip()
                elif "###" in back_content: 
                    back = back_content.split("###", 1)[0].strip()
                else: 
                    back = back_content
            except Exception as e:
                notify(f"Error parsing plain Anki response: {e}")
                return
        else:
            notify(f"Could not parse Front/Back from LLM response: {anki_response[:100]}...")
            return

        if front and back:
            # Create Anki card
            deck_name = '...MyDiscoveries2'
            note_type = 'Basic'
            if not ensure_anki_running():
                notify("Could not start or connect to Anki. Please start Anki manually.")
                return
            connector = AnkiConnector(deck_name=deck_name, note_type=note_type, allow_duplicate=False)
            
            if connector.add_card(front, back, ""):
                notify(f"Successfully created Anki card! Front: {front} | Back: {back}")
            else:
                notify(f"Failed to create Anki card. Front: {front} | Back: {back}")
        else:
            notify("Could not extract valid Front/Back from LLM response.")

    except Exception as e:
        notify(f"An error occurred: {e}")

if __name__ == "__main__":
    clipboard_to_anki()