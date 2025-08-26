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

bone_count = 0
hide_count = 0

Items_to_drop = [
"cabb.png",
]

def open_application(app_name):
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    workspace.launchApplication_(app_name)

def RandomPosition(x1, y2):
    x = (x1 / 2) + random.randint(-1, 1)
    y = (y2 / 2) + random.randint(-1, 1)
    return x, y

def find_spotted_kebbit():
    x, y = pyautogui.locateCenterOnScreen('spotted_kebbit.png', confidence=0.8)
    return x, y

def find_falcon():
    x, y = pyautogui.locateCenterOnScreen('falcon.png', confidence=0.8)
    return x, y

def find_drop_button():
    x, y = pyautogui.locateCenterOnScreen('drop_button.png', confidence=0.8)
    return x, y


def drop_items():
    pyautogui.keyDown('shift')
    time.sleep(0.5)
    for item_image in Items_to_drop:
        try:
            items = list(pyautogui.locateAllOnScreen(item_image, confidence=0.8))

            if items:
                print(f"{len(items)} {item_image} to drop")

                for item in items:
                    x, y = pyautogui.center(item)
                    rx, ry = RandomPosition(x, y)
                    pyautogui.leftClick(rx, ry)
                    time.sleep(0.035)

        except Exception as e:
            print(f"Error processing {item_image}: {str(e)}")
            continue

    return

open_application("RuneLite")
time.sleep(1)
drop_items()
