import subprocess
import os

def notify(text):
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

import clipboard
import requests
import json
from AnkiConnector import AnkiConnector

def notify(text):
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

def generate_qa(fact, llm_api_key):
    """Generates a question and answer from a fact using an LLM."""
    llm_url = "https://api.deepseek.com/v1/chat/completions"
    prompt = f"Make an Anki Flashcard from the following fact. You are free to use your own knowledge to make the card more professional. Label it Front: and Back: .\n\n{fact}"
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150,
        "temperature": 0.7,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": []
    })
    headers = {
        "Authorization": f"Bearer {llm_api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(llm_url, headers=headers, data=payload, timeout=30)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        response_json = response.json()
        # Extract the generated text from the response
        corrected = response_json["choices"][0]["message"]["content"].strip()

        # Split the generated text into question and answer
        if "**Front:**" in corrected and "**Back:**" in corrected:
            try:
                main_content = corrected.split("**Front:**", 1)[1]
                front_text_parts = main_content.split("**Back:**", 1)
                question = front_text_parts[0].strip()
                back_content = front_text_parts[1].strip()
                if "---" in back_content: answer = back_content.split("---", 1)[0].strip()
                elif "###" in back_content: answer = back_content.split("###", 1)[0].strip()
                else: answer = back_content
            except Exception as e:
                print(f"Error parsing MD Anki response: {e}")
                return None, None
        elif "Front: " in corrected and "Back: " in corrected:
            try:
                main_content = corrected.split("Front: ", 1)[1]
                front_text_parts = main_content.split("Back: ", 1)
                question = front_text_parts[0].strip()
                back_content = front_text_parts[1].strip()
                if "---" in back_content: answer = back_content.split("---", 1)[0].strip()
                elif "###" in back_content: answer = back_content.split("###", 1)[0].strip()
                else: answer = back_content
            except Exception as e:
                print(f"Error parsing plain Anki response: {e}")
                return None, None
        else:
            print(f"Could not parse Front/Back from Anki response: {corrected[:100]}")
            return None, None

        return question, answer

    except requests.exceptions.RequestException as e:
        print(f"Error during LLM request: {e}")
        return None, None
    except json.JSONDecodeError:
        print("Failed to decode JSON response from LLM.")
        return None, None
    except KeyError:
        print("KeyError: 'choices' or 'text' not found in LLM response.")
        return None, None

def create_anki_card(question, answer, deck_name="...MyDiscoveries2"):
    """Creates an Anki card with the given question and answer."""
    connector = AnkiConnector(deck_name=deck_name, note_type="Basic", allow_duplicate=False)
    return connector.add_card(question, answer, "")

def main():
    # Read API keys and URLs from files (replace with your actual file paths)
    try:
        with open("/home/twain/Projects/grammarpt/deepseek_api.txt", "r") as f:
            llm_api_key = f.read().strip()
    except FileNotFoundError:
        print("Error: API key files not found.")
        return

    # Get clipboard content
    fact = clipboard.paste()
    if not fact:
        print("Clipboard is empty.")
        return

    # Generate question and answer
    question, answer = generate_qa(fact, llm_api_key)
    if not question or not answer:
        print("Failed to generate question and answer.")
        return

    # Create Anki card
    result = create_anki_card(question, answer)
    if result:
        notify(f"Anki card created successfully!\nQuestion: {question}\nAnswer: {answer}")
    else:
        notify("Failed to create Anki card.")

if __name__ == "__main__":
    main()