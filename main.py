from subprocess import Popen, PIPE
import os
#import openai
import subprocess
from AnkiConnector import AnkiConnector
import time
from PIL import Image
import glob
import pyautogui
import pyperclip
from groq import AsyncGroq as Groq

#to use this, make a custom keyboard shortcut for each language:
#bash -c "python3 /home/[USERNAME]/Projects/grammarpt/main.py -[ARGUMENT]"

def get_args():
    import argparse
    parser = argparse.ArgumentParser(description='Translate selected text')
    parser.add_argument('-o', '--obsidian_inbox', action='store_true', help='append to obsidian inbox')
    parser.add_argument('-g', '--grammar', action='store_true', help='automatically fix the grammar of entire textbox')
    parser.add_argument('-i', '--grammaarhighlight', action='store_true', help='fix the grammar of highlighted text')
    parser.add_argument('-c', '--codecondense', action='store_true', help='condense selected code')
    parser.add_argument('-f', '--create_function', action='store_true', help='creates a function from selected code')
    parser.add_argument('-a', '--makeanki', action='store_true', help='make an anki card from selected text')
    parser.add_argument('-m', '--makeankiimage', action='store_true', help='make an anki card from selected text and last screenshotted image')
    return parser.parse_args()

def get_active_window():
    output = subprocess.check_output(['xdotool', 'getactivewindow'])
    window_id = output.strip()
    output = subprocess.check_output(['xprop', '-id', window_id, 'WM_CLASS'])
    class_name = output.decode('utf-8').split('"')[1]
    return (str(window_id), str(class_name))

def get_firefox_url():
    window_id, window_class = get_active_window()
    print(window_class + window_id)
    if window_class == 'Navigator':
        subprocess.call(['xdotool', 'key', '--window', window_id, 'ctrl+l'])
        subprocess.call(['xdotool', 'key', '--window', window_id, 'ctrl+c'])
        subprocess.call(['xdotool', 'key', '--window', window_id, 'Escape'])
        subprocess.call(['xdotool', 'key', '--window', window_id, 'Left'])
        subprocess.call(['xdotool', 'click', '1'])
        output = subprocess.check_output(['xclip', '-out', '-selection', 'clipboard'])
        url = output.strip().decode('utf-8')
        return url
    else:
        return None

def get_primary_clipboard():
    p = Popen(['xsel', '-o'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    output = output.decode('utf-8')
    return output

def notify(text):
    print('text')    
    msg = "notify-send ' ' '"+text+"'"
    os.system(msg)

async def construct_request(prompt, text):
    item = prompt+text
    return await send_request([{"role":"user","content":item}])

def send_openai_request(request_message):
    api_location = '~/Projects/grammarpt/apikey.txt'
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

async def send_request(request_message):
    api_location = '~/Projects/grammarpt/groq_apikey.txt'
    api_location = os.path.expanduser(api_location)
    with open(api_location, 'r') as f:
        api_key = f.read().strip()
    
    client = Groq(api_key=api_key)
    
    response = await client.chat.completions.create(
        messages=request_message,
        model="deepseek-r1-distill-llama-70b"
    )                   
    
    corrected = response.choices[0].message.content.replace("\n","").strip().lstrip()
    notify(corrected)
    pyperclip.copy(corrected)
    print(corrected)
    return corrected

async def coding_assistant(notification, prompt):
    selected_text = get_primary_clipboard()
    if len(selected_text) < 5000:
        notify(notification)
        # Determine the indentation of the first line in the selected text
        first_line = selected_text.split('\n')[0]
        indentation = first_line[:len(first_line) - len(first_line.lstrip())]
        pre_text = '\n'.join([line[:len(line) - len(line.lstrip())] + '#' + line.lstrip() for line in selected_text.split('\n')]) + '\n'
        await construct_request(prompt+"\n\n", selected_text)
        current_clipboard = pyperclip.paste()
        # Indent the lines in current_clipboard with the same indentation as the original selected text
        current_clipboard_indented = '\n'.join([indentation + line for line in current_clipboard.split('\n')])
        pyperclip.copy(pre_text + current_clipboard_indented)
        pyautogui.hotkey('ctrl', 'v')
    else:
        notify("Too long for highlight grammar fix. Break it into small parts")

async def coding_assistant_new(notification, prompt):
    selected_text = get_primary_clipboard()
    if len(selected_text) < 5000:
        notify(notification)
        # Determine the indentation of the first line in the selected text
        first_line = selected_text.split('\n')[0]
        indentation = first_line[:len(first_line) - len(first_line.lstrip())]
        pre_text = '\n'.join([line[:len(line) - len(line.lstrip())] + '#' + line.lstrip() for line in selected_text.split('\n')]) + '\n'
        await construct_request(prompt+"\n\n", selected_text)
        current_clipboard = pyperclip.paste()
        # Indent the lines in current_clipboard with the same indentation as the original selected text
        current_clipboard_indented = '\n'.join([indentation + line for line in current_clipboard.split('\n')])
        pyperclip.copy(pre_text + replace_spaces(current_clipboard_indented))
        pyautogui.hotkey('ctrl', 'v')
    else:
        notify("Too long for highlight grammar fix. Break it into small parts")



import re

def replace_spaces(text):
    return re.sub(r'( {4})+', lambda m: '\n' + m.group(0), text)

async def main():
    args = get_args()
    if args.obsidian_inbox:
        notify("Appended to obsidian inbox")
        selected_text = get_primary_clipboard()
        inbox_dir = "~/Documents/obsidian_note_vault/noteVault/Inbox.md"
        inbox_dir = os.path.expanduser(inbox_dir)
        with open(inbox_dir, 'r') as file:
            original_content = file.read()
        new_content = selected_text + os.linesep + os.linesep + original_content
        with open(inbox_dir, 'w') as file:
            file.write(new_content)
    if args.grammar:
        pyautogui.hotkey('ctrl', 'a')
        selected_text = get_primary_clipboard()
        if len(selected_text) < 1000:
            await construct_request("Fix the grammar, only respond with the corrected text.\n\n", selected_text.replace("\n", " ").strip().lstrip())
            pyautogui.hotkey('ctrl', 'v')
        else:
            notify("Too long for auto grammar fix. Use grammar highlight.")
            pyautogui.press('right') #press right arrow to clear select all
    if args.grammaarhighlight:
        selected_text = get_primary_clipboard()
        if len(selected_text) < 10000:
            await construct_request("Fix the grammar, only respond with the corrected text.\n\n", selected_text.replace("\n", " ").strip().lstrip())
        else:
            notify("Too long for highlight grammar fix. Break it into small parts")
    if args.codecondense:
        await coding_assistant("Condensing code...", "Condense this code, only respond with the condensed code.")
    if args.create_function:
        await coding_assistant_new("Creating function...", "Create a function for this code, only respond with the function, exclude imports.")
    if args.makeanki:
        #selected_text = get_primary_clipboard()
        selected_text = "dogs are usually bigger than cats"
        if len(selected_text) < 1000:
            notify("Making Anki card...")
            anki_response = await construct_request("Make an Anki Flashcard from the following fact. You are free to use your own knowledge to make the card more professional. Label it Front: and Back: .\n\n", selected_text)
            parts = anki_response.split("Front: ")[1].split("Back: ")
            front, back = [part.strip() for part in parts]
            url = get_firefox_url()
            source = url if url else ""
            source = '' if 'Front: ' in source else source
            deck_name = '...MyDiscoveries'
            note_type = 'Basic'
            connector = AnkiConnector(deck_name=deck_name, note_type=note_type, allow_duplicate=False)
            connector.add_card(front, back, source)
        else:
            notify("Too long for highlight grammar fix. Break it into small parts")
    if args.makeankiimage:
        image_dir = '~/Pictures/Screenshots'
        image_dir = os.path.expanduser(image_dir)
        image_files = glob.glob(os.path.join(image_dir, '*.png'))
        image_files.sort(key=os.path.getctime, reverse=True)
        most_recent_image = image_files[0]
        image = Image.open(most_recent_image)
        image = image.convert('RGB')
        new_file_name = os.path.splitext(most_recent_image)[0].replace(' ', '_') + '.jpg'
        image.save(new_file_name, 'JPEG')
        selected_text = get_primary_clipboard()
        if len(selected_text) < 1000:
            notify("Making Anki card with an image...")
            anki_response = await construct_request("Make an Anki Flashcard from the following fact. You are free to use your own knowledge to make the card more professional. Label it Front: and Back: .\n\n", selected_text)
            parts = anki_response.split("Front: ")[1].split("Back: ")
            front, back = [part.strip() for part in parts]
            url = get_firefox_url()
            source = url if url else ""
            source = '' if 'Front: ' in source else source
            deck_name = '...MyDiscoveries'
            note_type = 'Basic'
            connector = AnkiConnector(deck_name=deck_name, note_type=note_type, allow_duplicate=False, back_image=new_file_name)
            connector.add_card(front, back, source)
        else:
            notify("Too long for highlight grammar fix. Break it into small parts")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())




