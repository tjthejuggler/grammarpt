import subprocess
import nltk
from nltk.corpus import wordnet
import string
import os

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

def define_selected_word():
    try:
        # Try using xclip to get the selected text
        try:
            selected_word = subprocess.check_output(['xclip', '-selection', 'primary', '-o']).decode('utf-8').strip()
        except FileNotFoundError:
            # If xclip is not found, try using xsel
            try:
                selected_word = subprocess.check_output(['xsel', '-p']).decode('utf-8').strip()
            except FileNotFoundError:
                notify("Neither xclip nor xsel is installed. Please install one of them.")
                return
        
        if not selected_word:
            notify("No text selected.")
            return

        # Remove punctuation from the selected word
        selected_word = selected_word.strip(string.punctuation)

        synsets = wordnet.synsets(selected_word)
        if not synsets:
            notify(f"No definitions found for '{selected_word}' in WordNet.")
            return

        definition_text = f"Definitions of '{selected_word}':"
        for syn in synsets:
            pos = syn.pos() # Part of speech (n, v, a, r, s)
            # Map POS tags to more readable names
            pos_map = {'n': 'Noun', 'v': 'Verb', 'a': 'Adjective', 's': 'Adjective Satellite', 'r': 'Adverb'}
            readable_pos = pos_map.get(pos, pos)
            examples = '; '.join(syn.examples())
            if examples:
                definition_text += f" {readable_pos}: {syn.definition()} (e.g., {examples})"
            else:
                definition_text += f" {readable_pos}: {syn.definition()}"

        notify(definition_text)

    except Exception as e:
        notify(f"An error occurred: {e}")

if __name__ == "__main__":
    define_selected_word()