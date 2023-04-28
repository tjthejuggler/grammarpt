import pyautogui
import time

# Wait for the user to switch to the desired window or application
time.sleep(5)

# Simulate the Ctrl+A keyboard shortcut
pyautogui.hotkey('ctrl', 'a')

# Simulate the paste command
#pyautogui.hotkey('ctrl', 'v')