from subprocess import Popen, PIPE
import os
import openai
import pyautogui
import pyperclip



#to use this, make a custom keyboard shortcut for each language:
#bash -c "python3 /home/lunkwill/projects/grammarpt/main.py"

def get_args():
    import argparse
    parser = argparse.ArgumentParser(description='Translate selected text')
    parser.add_argument('-g', '--grammar', action='store_true', help='automatically fix the grammar of entire textbox')
    parser.add_argument('-i', '--grammaarhighlight', action='store_true', help='fix the grammar of highlighted text')
    parser.add_argument('-c', '--codecondense', action='store_true', help='condense selected code')
    return parser.parse_args()

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

def construct_request(prompt, text):    
    item = prompt+text
    send_request([{"role":"user","content":item}])

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
    args = get_args()
    if args.grammar:
        pyautogui.hotkey('ctrl', 'a')
        selected_text = get_primary_clipboard()
        if len(selected_text) < 1000:
            construct_request("Fix the grammar, only respond with the corrected text.\n\n", selected_text.replace("\n", " ").strip().lstrip())  
            pyautogui.hotkey('ctrl', 'v')
        else:
            notify("Too long for auto grammar fix. Use grammar highlight.")            
            pyautogui.press('right') #press right arrow to clear select all
    if args.grammaarhighlight:
        selected_text = get_primary_clipboard()
        if len(selected_text) < 10000:
            construct_request("Fix the grammar, only respond with the corrected text.\n\n", selected_text.replace("\n", " ").strip().lstrip())
        else:
            notify("Too long for highlight grammar fix. Break it into small parts")
    if args.codecondense:
        selected_text = get_primary_clipboard()
        if len(selected_text) < 5000:
            construct_request("Condense this code, only respond with the condensed code.\n\n", selected_text)  
        else:
            notify("Too long for highlight grammar fix. Break it into small parts")

main()