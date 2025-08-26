import AppKit
import pyautogui
import random
import cv2
import pytesseract
import time
import easyocr
import math
import re
from PIL import Image

ARROW_DURATION = random.uniform(0.2, 0.5)
CAMERA_COOLDOWN = random.randint(300, 600)
last_camera_movement = time.time()
overload_cooldown = 0 #random.randint(305, 310)
last_overload_time = time.time()
last_prayer_time = time.time()
prayer_cooldown = 2.5
last_absorption_time = time.time()
absorption_cooldown = 5
#skip_absorption = False
#skip_overload = False


def open_application(app_name):
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    workspace.launchApplication_(app_name)

def find_on_screen():
    try:
        x, y = pyautogui.locateCenterOnScreen('prayericon.png', confidence=0.9)
        if x and y:
            return x, y

    except Exception as e:
        #print("[Prayer] Prayer icon not found, trying again")
        return None, None

def human_camera_movement():
    duration = random.uniform(0.5, 2.5)
    steps = int(duration * 30)
    for i in range(steps):
        progress = i / steps
        factor_curve = math.sin(progress * math.pi)
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(50, 150)
        x_o = (radius * math.cos(angle) * factor_curve) / 2
        y_o = (radius * math.sin(angle) * factor_curve * 6) / 2

        x, y = pyautogui.position()
        pyautogui.moveTo(x + x_o, y + y_o, duration=duration / steps, tween=pyautogui.easeOutQuad)

        if random.random() < 0.1:
            time.sleep(random.uniform(0.05, 0.2))


def camera_movement():
    directions = []
    for _ in range(random.randint(2, 4)):  # 2-4 direction changes
        directions.extend(random.sample(['left', 'right', 'up', 'down'], random.randint(1, 2)))

    for direction in directions:
        pyautogui.keyDown(direction)
        time.sleep(ARROW_DURATION * random.uniform(0.8, 1.2))
        pyautogui.keyUp(direction)
        if random.random() < 0.3:
            time.sleep(random.uniform(0.1, 0.3))

    if random.random() < 0.7:
        pyautogui.press(random.choice(['left', 'right']), presses=1, interval=0.1)

def find_overload():
    try:
        open_application("RuneLite")
        x, y = pyautogui.locateCenterOnScreen('overload.png', confidence=0.68)
        if x and y:
            return x, y

    except:
        #print("[Overload] not found.")
        #skip_overload = True
        pass
    return None, None

def find_absorption():
    try:
        open_application("RuneLite")
        x, y = pyautogui.locateCenterOnScreen('absorption.png', confidence=0.7)
        if x and y:
            return x, y

    except:
        #print("[Absorption] not found.")
        #skip_absorption = True
        pass
    return None, None

def is_key_pressed(key):
    try:
        return pyautogui.keyIsDown(key)
    except:
        return False

try:
    while True:

        if time.time() - last_prayer_time > prayer_cooldown:
            open_application("RuneLite")
            time.sleep(1)
            x, y = find_on_screen()
            if x is None:
                time.sleep(2)
                continue
            x = (x / 2) + random.randint(-1, 1)
            y = (y / 2) + random.randint(-1, 1)
            pyautogui.moveTo(x, y, duration=random.uniform(0.1, 0.3))
            pyautogui.click()
            time.sleep(random.uniform(0.4, 0.8))
            pyautogui.click()
            prayer_cooldown = random.uniform(47, 56)
            last_prayer_time = time.time()
            print(f"[Prayer] Clicked: ({x}, {y}). Next click: {prayer_cooldown:.1f} seconds.")

            if time.time() - last_absorption_time > absorption_cooldown:
                x, y = find_absorption()
                if x is None:
                    time.sleep(2)
                    continue

                x = (x / 2) + random.randint(-1, 1)
                y = (y / 2) + random.randint(-1, 1)
                time.sleep(random.uniform(0.4, 0.5))
                pyautogui.moveTo(x, y, duration=random.uniform(0.1, 0.3))
                pyautogui.click()
                last_absorption_time = time.time()
                absorption_cooldown = random.uniform(15, 30)
                print(f"[Absorption] Clicked: ({x}, {y}). 1 dosages used. Next absorption at {absorption_cooldown}.")

        if time.time() - last_camera_movement > CAMERA_COOLDOWN:
            open_application("RuneLite")
            camera_movement()
            last_camera_movement = time.time()
            CAMERA_COOLDOWN = random.randint(300, 600)
            print(f"[Camera] moved. Next interaction: {CAMERA_COOLDOWN} seconds.")

        if time.time() - last_overload_time > overload_cooldown:
            open_application("RuneLite")
            x, y = find_overload()
            if x is None:
                time.sleep(2)
                continue

            x = (x / 2) + random.randint(-1, 1)
            y = (y / 2) + random.randint(-1, 1)
            pyautogui.moveTo(x, y, duration=random.uniform(0.1, 0.3))
            pyautogui.click()
            last_overload_time = time.time()
            overload_cooldown = random.randint(305, 310)
            print(f"[Overload] Clicked: ({x}, {y}). Overload consumed. Next usage in: {overload_cooldown} seconds. ")




except KeyboardInterrupt:
    print("\n[Loop] Script suspended :(")