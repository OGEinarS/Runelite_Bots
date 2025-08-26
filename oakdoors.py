import AppKit
import pyautogui
import random
import cv2
import pytesseract
import time
import easyocr
import re
from PIL import Image
from pynput import mouse

CONFIG = 0.43
Count = 0

def open_application(app_name):
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    workspace.launchApplication_(app_name)

open_application("RuneLite")

def build_door():
    x, y = pyautogui.locateCenterOnScreen('yellowtable.png', confidence=CONFIG)
    pyautogui.click(x/2, y/2)
    time.sleep(0.5)
    print("Table built")
    pyautogui.press('1')
    Count = 1

def remove_door():
    x, y = pyautogui.locateCenterOnScreen('pinktable.png', confidence=CONFIG)
    pyautogui.click(x/2, y/2)
    time.sleep(0.5)
    print("Table built")
    pyautogui.press('1')
    Count = 2

def collect_planks():
    x, y = pyautogui.locateCenterOnScreen('butler.png', confidence=CONFIG)
    pyautogui.click(x/2, y/2)
    time.sleep(0.5)
    print("Table built")
    pyautogui.press('1')
    Count = 0

import pyautogui
import time
from pynput import mouse

# macOS-specific adjustments
pyautogui.PAUSE = 0.1  # Prevents input drops during sleeps

def on_click(x, y, button, pressed):
    if button == mouse.Button.left and pressed:
        time.sleep(0.6)  # Wait 1 second after left-click
        pyautogui.press('1')  # Press '1'
        print("Pressed '1' after click!")

# Set up listener (macOS may prompt for permissions)
listener = mouse.Listener(on_click=on_click)
listener.start()

print("Listening for left-clicks...")
while True:
    time.sleep(0.1)  # Reduce CPU usage


"""try:
    open_application("RuneLite")
    pyautogui.keyDown('1')
    while True:
        if not build_door() and Count == 0:
            time.sleep(0.5)
            pyautogui.press('1')
            time.sleep(3)
            continue
        if not remove_door() and Count == 1:
            time.sleep(0.5)
            pyautogui.press('1')
            time.sleep(3)
            continue
        if not collect_planks() and Count == 2:
            time.sleep(0.5)
            pyautogui.press('1')
            time.sleep(3)


except Exception:
    print("Script suspended")
    pyautogui.keyUp('1')"""