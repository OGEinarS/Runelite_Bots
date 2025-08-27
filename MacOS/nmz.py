import AppKit
import pyautogui
import random
import cv2
import pytesseract
import time
import easyocr
import re
from PIL import Image


def open_application(app_name):
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    workspace.launchApplication_(app_name)

def press_prayer():
    x, y = pyautogui.locateCenterOnScreen('prayericon.png')
    try:
        while True:
            pyautogui.click(x, y, 2, 1, button='left')

            time.sleep(10)

    except KeyboardInterrupt:
        print("Stopped.")

open_application("RuneLite")
time.sleep(1)
press_prayer()

"""""
def extract_hp_and_absorption(text):
    hitpoints = None
    absorption = None
    hitpoints_match = re.search(r"Hitpoints\s*(\d+)", text)
    hitpoints = int(hitpoints_match.group(1)) if hitpoints_match else None

    absorption_match = re.search(r"Absorption:\s*(\d+)", text)
    absorption = int(absorption_match.group(1)) if absorption_match else None

    return {
        "hitpoints": hitpoints,
        "absorption": absorption
    }


def monitor_nmz():
    location = pyautogui.locateOnScreen('nmzinfo.png', confidence=0.7)
    try:
        while True:
            screenshot = pyautogui.screenshot(region=(int(location.left/2),int(location.top/2), 140, 65))
            screenshot.save("nmzdata.png")
            data = pytesseract.image_to_string(screenshot)

            # Print the extracted information
            print(f"Hitpoints: {data['hitpoints']}")
            print(f"Absorption: {data['absorption']}")

            # Check conditions
            if data["hitpoints"] is not None and data["absorption"] is not None:
                # Check if HP is greater than 1
                if data["hitpoints"] > 1:
                    print("HP is greater than 1 eating rockcake")
                    # Add your action here (e.g., click a button, send a notification, etc.)

                # Check if absorption is close to 200 (e.g., within ±10)
                if abs(data["absorption"] - 200) <= 10:
                    print("Absorption is close to 200. drinking absoption")
                    # Add your action here (e.g., click a button, send a notification, etc.)

            time.sleep(5)

    except KeyboardInterrupt:
        print("Monitoring stopped.")


open_application("RuneLite")
time.sleep(1)
monitor_nmz()



def getnmzdata(): #c / Health
    location = pyautogui.locateOnScreen('nmzinfo.png', confidence=0.7)
    if location:
        screenshot = pyautogui.screenshot(region=(int(location.left/2),int(location.top/2), 140, 65))
        screenshot.save("nmzdata.png")
        data = pytesseract.image_to_string(screenshot)
        return data

def open_application(app_name):
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    workspace.launchApplication_(app_name)

def read_hp():
    x, y = pyautogui.locateOnScreen('find_hp.png')
    if x and y:
        screenshot = pyautogui.screenshot(region=(x/2, y/2, 20, 20))
        screenshot.save("hp_screenshot.png")
        hp = pytesseract.image_to_string(screenshot)
        print(hp)
        return hp

def read_abso():
    x, y = pyautogui.locateOnScreen('find_absorb.png')
    if x and y:
        screenshot = pyautogui.screenshot(region=(x/2, y/2, 200, 20))
        screenshot.save("abso_screenshot.png")
        abso = pytesseract.image_to_string(screenshot)
        print(abso)
        return abso


open_application("RuneLite")
time.sleep(2)
read_hp()
read_abso()
"""""
