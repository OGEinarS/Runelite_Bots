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

def open_application(app_name):
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    workspace.launchApplication_(app_name)

def find_orb():
    try:
        x, y = pyautogui.locateCenterOnScreen('eorb.png', confidence=0.8)
        if x and y:
            return x, y
    except:
        print("orb not found")
        pass
    return None, None

def find_staff():
    try:
        x, y = pyautogui.locateCenterOnScreen('estaff.png', confidence=0.8)
        if x and y:
            return x, y
    except:
        print("staff not found")
        pass
    return None, None

def close_bank():
    try:
        x, y = pyautogui.locateCenterOnScreen('x.png', confidence=0.9)
        if x and y:
            return x, y
    except:
        print("Cannot close the bank!, location not found")
        pass
    return None, None

def deposit_bank():
    try:
        x, y = pyautogui.locateCenterOnScreen('bankall.png', confidence=0.9)
        if x and y:
            return x, y

    except:
        print("Cannot find store all items, location not found")
        pass
    return None, None

def open_bank():
    try:
        x, y = pyautogui.locateCenterOnScreen('greenbox.png', confidence=0.9)
        if x and y:
            return x, y
    except:
        print("Bank location not found, please set greenbox!")
        pass
    return None, None

try:
    while True:
        open_application("RuneLite")
        time.sleep(1)

        x, y = open_bank()
        if x is None:
            time.sleep(1)
            continue

        x = (x / 2) + random.uniform(-1.5, 1.5)
        y = (y / 2) + random.uniform(-1.5, 1.5)
        pyautogui.moveTo(x, y)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(2)

        x, y = deposit_bank()
        if x is None:
            time.sleep(1)
            continue

        x = (x / 2) + random.uniform(-1.5, 1.5)
        y = (y / 2) + random.uniform(-1.5, 1.5)
        pyautogui.moveTo(x, y)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(2)

        x, y = find_orb()
        if x is None:
            time.sleep(1)
            continue
        x = (x / 2) + random.uniform(-1.5, 1.5)
        y = (y / 2) + random.uniform(-1.5, 1.5)
        pyautogui.moveTo(x, y)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(2)

        x, y = find_staff()
        if x is None:
            time.sleep(1)
            continue
        x = (x / 2) + random.uniform(-1.5, 1.5)
        y = (y / 2) + random.uniform(-1.5, 1.5)
        pyautogui.moveTo(x, y)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(2)

        x, y = close_bank()
        if x is None:
            time.sleep(1)
            continue

        x = (x / 2) + random.uniform(-1.5, 1.5)
        y = (y / 2) + random.uniform(-1.5, 1.5)
        pyautogui.moveTo(x, y)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(2)

        x, y = find_staff()
        if x is None:
            time.sleep(1)
            continue
        x = (x / 2) + random.uniform(-1.5, 1.5)
        y = (y / 2) + random.uniform(-1.5, 1.5)
        pyautogui.moveTo(x, y)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(2)

        x, y = find_orb()
        if x is None:
            time.sleep(1)
            continue
        x = (x / 2) + random.uniform(-1.5, 1.5)
        y = (y / 2) + random.uniform(-1.5, 1.5)
        pyautogui.moveTo(x, y)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(2)

        pyautogui.keyDown('space')#SPACE
        time.sleep(14)
        #Vente på å lage
        x, y = open_bank()
        if x is None:
            time.sleep(1)
            continue
        x = (x / 2) + random.uniform(-1.5, 1.5)
        y = (y / 2) + random.uniform(-1.5, 1.5)
        pyautogui.moveTo(x, y)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(2)

        x, y = deposit_bank()
        if x is None:
            time.sleep(1)
            continue

        x = (x / 2) + random.uniform(-1.5, 1.5)
        y = (y / 2) + random.uniform(-1.5, 1.5)
        pyautogui.moveTo(x, y)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(2)



except KeyboardInterrupt:
        print("\nSuspended")
