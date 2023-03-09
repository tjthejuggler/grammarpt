from subprocess import Popen, PIPE
import os
import openai
import pyautogui
import time
import pyperclip


#to use this, make a custom keyboard shortcut for each language:
#bash -c "python3 /home/lunkwill/projects/grammarpt/main.py"

#what do the means of the word "securities" be?

#use subrocess and xsel to get the clipboard contents
def get_primary_clipboard():
    p = Popen(['xsel', '-o'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    output = output.decode('utf-8')
    return output

#create an notify message
def notify(text):
    print('text')    
    msg = "notify-send ' ' '"+text+"'"
    os.system(msg)

def get_better_grammar(text):    
    item = "Fix the grammar, only respond with the corrected text.\n\n"+text
    request_message = [{"role":"user","content":item}]
    send_request(request_message)

def send_request(request_message):
    with open('/home/lunkwill/projects/grammarpt/apikey.txt', 'r') as f:
        api_key = f.read().strip()
    openai.api_key = (api_key)
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=request_message
    )
    print(response)
    corrected = response["choices"][0]["message"]["content"].replace("\n","").strip().lstrip()
    print('here', corrected)
    notify(corrected)
    pyperclip.copy(corrected)    

def main():
    pyautogui.hotkey('ctrl', 'a')
    selected_text = get_primary_clipboard()
    get_better_grammar(selected_text.replace("\n", " ").strip().lstrip())  
    pyautogui.hotkey('ctrl', 'v')

    


main()