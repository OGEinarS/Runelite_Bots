import AppKit
import os
import cv2
import pyautogui
import random
import time
import numpy as np
from PIL import Image
from PIL import ImageGrab
from pathlib import Path

from MacOS.bloodrunes import float_start_time

# Color definitions
c_bank = "FFFFA400"
c_unf_jew = "FF6B6B"
c_fin_jew = "7AC353"
c_mag_spell = "FFE2A200"
c_mag_sellect = "FF67A8CD"
c_idle = "ff8ffa"

# Innstillinger
MIN_LOG_COUNT = 4
ACTION_DELAY = (0.05, 0.03)
MIN_AREA = 2
TOLERANCE = 12
current_world = -1
delay_time = 5 #random.uniform(5 * 3600, 5.5 * 3600)   5 - 5.5 hours
run_time = time.time()
valid_worlds = [303, 304, 327, 328, 351, 352, 375, 376, 457, 458]
float_start_time = "Nigger"

BANK_ALL_IMAGE = os.path.join(Path(__file__).parent.parent, "bankall.png")

# State tracking
current_state = "START"


def type_in_chat(message):
    pyautogui.press("enter")
    time.sleep(0.2)
    pyautogui.keyDown("shift")
    pyautogui.press(".")
    pyautogui.press(".")
    pyautogui.keyUp("shift")
    pyautogui.write(message, interval=0.1)
    time.sleep(0.3)
    pyautogui.press("enter")


def hop_world():
    global current_world

    available_worlds = [w for w in valid_worlds if w != current_world]
    if not available_worlds:
        available_worlds = valid_worlds
    new_world = random.choice(available_worlds)

    type_in_chat(f"hop {new_world}")
    float_start_time = f"{time.strftime('%H:%M:%S')}"
    print(f"Hopped to world {new_world} at {float_start_time}")

    current_world = new_world
    time.sleep(10)

def count_items_full_screen(COLOR_IMPUT):
    try:
        # Ta skjermbilde og konverter
        screenshot = pyautogui.screenshot()
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Fargegrenser
        rgb = tuple(int(COLOR_IMPUT[i:i + 2], 16) for i in (0, 2, 4))
        lower = np.array([max(0, c - TOLERANCE) for c in rgb[::-1]])
        upper = np.array([min(255, c + TOLERANCE) for c in rgb[::-1]])

        # Lag maske
        mask = cv2.inRange(img, lower, upper)

        # Finn og tell konturer
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return len([c for c in contours if cv2.contourArea(c) > MIN_AREA])

    except Exception as e:
        print(f"Loggtellingsfeil: {e}")
        return 0

def open_application(app_name):
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    workspace.launchApplication_(app_name)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 8:
        hex_color = hex_color[2:]
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def find_hex_color(color_input, tolerance=30):
    find_rgb = hex_to_rgb(color_input)
    screenshot = pyautogui.screenshot()
    img = np.array(screenshot)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    l_bound = np.array([max(0, c - tolerance) for c in find_rgb[::-1]])
    u_bound = np.array([min(255, c + tolerance) for c in find_rgb[::-1]])

    mask = cv2.inRange(img, l_bound, u_bound)
    locations = cv2.findNonZero(mask)
    return locations if locations is not None else []

def IdleNotification(tolerance=30):
    find_rgb = hex_to_rgb(c_idle)
    screenshot = pyautogui.screenshot()
    img = np.array(screenshot)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    l_bound = np.array([max(0, c - tolerance) for c in find_rgb[::-1]])
    u_bound = np.array([min(255, c + tolerance) for c in find_rgb[::-1]])

    mask = cv2.inRange(img, l_bound, u_bound)
    locations = cv2.findNonZero(mask)
    return True if locations is not None else []


def humanpause(basetime):
    newtime = basetime + random.uniform(0.0004, 0.0003)
    time.sleep(newtime)


def move_and_click(position, clicks=1):
    if isinstance(position, np.ndarray):
        x, y = position[0], position[1]
    else:
        x, y = position

    rand1 = random.uniform(-.50, .50)
    rand2 = random.uniform(-.50, .50)
    pyautogui.moveTo((x + rand1) / 2, (y + rand2) / 2, duration=random.uniform(*ACTION_DELAY))
    pyautogui.click(clicks=clicks)
    humanpause(0.003)

def find_and_click_center(hex_color, tolerance=1):
    global current_state

    matches = find_hex_color(hex_color, tolerance)
    if matches is not None and len(matches) > 0:
        contours, _ = cv2.findContours(
            cv2.inRange(
                cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR),
                np.array([max(0, c - tolerance) for c in hex_to_rgb(hex_color)[::-1]]),
                np.array([min(255, c + tolerance) for c in hex_to_rgb(hex_color)[::-1]])
            ),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            center_x = x + w // 2
            center_y = y + h // 2
            move_and_click((center_x, center_y))
            print(f"Klikket på {hex_color} ved ({center_x}, {center_y})")
            return True
    return False


def find_and_drop(hex_color, tolerance=1):
    screenshot = np.array(pyautogui.screenshot())
    screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    target_color = hex_to_rgb(hex_color)[::-1]
    lower_bound = np.array([max(0, c - tolerance) for c in target_color])
    upper_bound = np.array([min(255, c + tolerance) for c in target_color])

    mask = cv2.inRange(screenshot_bgr, lower_bound, upper_bound)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    click_count = 0

    for contour in contours:
        if cv2.contourArea(contour) > 1:
            x, y, w, h = cv2.boundingRect(contour)
            center_x = x + w // 2
            center_y = y + h // 2
            move_and_click((center_x, center_y))
            print(f"Klikket på {hex_color} ved ({center_x}, {center_y})")
            click_count += 1

    return click_count

def main():
    global current_state, run_time, delay_time

    try:
        print("Starter Firemaking-bot...")
        while True:
            print(f"Tilstand: {current_state}")
            open_application("RuneLite")
            jew_unf = count_items_full_screen(c_unf_jew)
            jew_fin = count_items_full_screen(c_fin_jew)
            print(f"Inventar.")
            print(f"unf: {jew_unf}")
            print(f"fin: {jew_fin}")


            if current_state == "START":
                if IdleNotification(tolerance=20):
                    if jew_unf == 0 and jew_fin == 0:
                        find_and_click_center(c_bank, tolerance=1)
                        humanpause(1)
                        find_and_click_center(c_unf_jew, tolerance=1)
                        humanpause(1)
                        pyautogui.press("esc")
                        humanpause(1)
                        pyautogui.press("f1")
                        continue

                    if jew_unf > 0:
                        pyautogui.press("f6")
                        find_and_click_center(c_mag_sellect,tolerance=1)
                        humanpause(1)
                        find_and_click_center(c_unf_jew,tolerance=1)
                        humanpause(1)
                        pyautogui.press("f1")
                        continue

                    if jew_fin > 0:
                        find_and_click_center(c_bank,tolerance=1)
                        humanpause(1)
                        find_and_click_center(c_fin_jew,tolerance=1)
                        humanpause(1)
                        find_and_click_center(c_unf_jew, tolerance=1)
                        humanpause(1)
                        pyautogui.press("esc")
                        humanpause(1)
                        pyautogui.press("f1")
                        continue



    except KeyboardInterrupt:
        print("\nAvsluttet av bruker.")


if __name__ == "__main__":
    main()