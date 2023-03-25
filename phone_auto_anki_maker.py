#be sure to make sh executable

from subprocess import Popen, PIPE
import os
import openai
import pyautogui
import pyperclip
import subprocess
from AnkiConnector import AnkiConnector
import time
from PIL import Image
import glob

def notify(text):
    print('text')    
    msg = "notify-send ' ' '"+text+"'"
    os.system(msg)

def construct_request(prompt, text):    
    item = prompt+text
    return send_request([{"role":"user","content":item}])

def send_request(request_message):
    api_location = '~/projects/grammarpt/apikey.txt'
    api_location = os.path.expanduser(api_location)
    with open(api_location, 'r') as f:
        api_key = f.read().strip()
    openai.api_key = (api_key)
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=request_message
    )
    corrected = response["choices"][0]["message"]["content"].replace("\n","").strip().lstrip()
    notify(corrected)
    pyperclip.copy(corrected)    
    return corrected  

ankti_to_make_location = '~/Documents/obsidian_note_vault/noteVault/ankis_to_make.txt'
ankti_to_make_location = os.path.expanduser(ankti_to_make_location)


with open(ankti_to_make_location, 'r') as f:
    chunks = f.read().split('\n\n')
    for chunk in chunks:
        if '|' in chunk:
            fact = chunk.split('|')[0]
            if len(fact) < 1000:
                if len(fact) > 10:
                    anki_response = construct_request("Make an Anki Flashcard from the following fact. You are free to use your own knowledge to make the card more professional. Label it Front: and Back: .\n\n", fact) 
                    parts = anki_response.split("Front: ")[1].split("Back: ")
                    front, back = [part.strip() for part in parts]
                    url = chunk.split('|')[1]
                    source = url if url else ""
                    #if source doesn't start with http, add it
                    if source and not source.startswith('http'):
                        source = 'http://'+source
                    deck_name = '...My discoveries'
                    note_type = 'Basic'
                    connector = AnkiConnector(deck_name=deck_name, note_type=note_type, allow_duplicate=False)
                    connector.add_card(front, back, source)
                else:
                    notify("Too short to be a fact.")
            else:
                notify("Too long for highlight grammar fix. Break it into small parts")

#delete all the text in the file
with open(ankti_to_make_location, 'w') as f:
    f.write('')