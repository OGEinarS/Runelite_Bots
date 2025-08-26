import AppKit
import pyautogui
import random
import cv2
import pytesseract
import time
import easyocr
import re
from PIL import Image

running = True
Timer = random.uniform(60, 120)

def open_application(app_name):
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    workspace.launchApplication_(app_name)

def find_on_screen():
    x, y = pyautogui.locateCenterOnScreen('prayericon.png', confidence=0.9)
    return x, y

try:
    while True:
        if running:
            open_application("RuneLite")
            x, y = find_on_screen()
            x = (x / 2) + random.randint(-1, 1)
            y = (y / 2) + random.randint(-1, 1)
            time.sleep(1)
            pyautogui.moveTo(x, y, duration=random.uniform(0.1, 0.3))
            pyautogui.click(clicks=2, interval=1.0)
            time.sleep(Timer)

except KeyboardInterrupt:
    print("\nSuspended")