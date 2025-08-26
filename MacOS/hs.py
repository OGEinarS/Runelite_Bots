import AppKit
import os
import cv2
import pyautogui
import random
import time
import numpy as np
from PIL import Image
from pathlib import Path

# Color definitions
COLOR_LOGS = "5A85FF"  # Farge på selve loggene
COLOR_FIRE = "FF0026FF"
COLOR_BANK = "FFFFAD00"
COLOR_BANK_ALL = "FFFF3131"

# Innstillinger
MIN_LOG_COUNT = 4
ACTION_DELAY = (0.03, 0.01)
LOG_TOLERANCE = 12
MIN_LOG_AREA = 5

BANK_ALL_IMAGE = os.path.join(Path(__file__).parent.parent, "bankall.png")

# State tracking
current_state = "START"


def count_logs_full_screen():
    try:
        # Ta skjermbilde og konverter
        screenshot = pyautogui.screenshot()
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Fargegrenser
        rgb = tuple(int(COLOR_LOGS[i:i + 2], 16) for i in (0, 2, 4))
        lower = np.array([max(0, c - LOG_TOLERANCE) for c in rgb[::-1]])
        upper = np.array([min(255, c + LOG_TOLERANCE) for c in rgb[::-1]])

        # Lag maske
        mask = cv2.inRange(img, lower, upper)

        # Finn og tell konturer
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return len([c for c in contours if cv2.contourArea(c) > MIN_LOG_AREA])

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


def humanpause(basetime):
    newtime = basetime + random.uniform(0.0004, 0.0003)
    time.sleep(newtime)


def move_and_click(position, clicks=1):
    if isinstance(position, np.ndarray):
        x, y = position[0], position[1]
    else:
        x, y = position

    rand1 = random.uniform(-8.00, 8.00)
    rand2 = random.uniform(-7.00, 9.00)
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

'''
def find_and_click_bank_all():
     location = pyautogui.locateCenterOnScreen(BANK_ALL_IMAGE, confidence=confidence)
     if location:
              x, y = location
              move_and_click((x, y))
              print(f"Clicked bank all at {x},{y} (confidence: {confidence})")
              return True
      except pyautogui.ImageNotFoundException:
          continue

        print("Bank all button not found")
        return False

    except Exception as e:
        print(f"Banking error: {str(e)}")
        return False    '''

def main():
    global current_state

    try:
        print("Starter Firemaking-bot...")
        while True:
            print(f"Tilstand: {current_state}")
            open_application("RuneLite")

            # Tell logger over hele skjermen
            log_count = count_logs_full_screen()
            print(f"Logger i inventar: {log_count}")


            if current_state == "START":
                if log_count < MIN_LOG_COUNT:
                    print("Tom for logger - går til bank")
                    current_state = "BANK"
                    continue

                if find_and_click_center(COLOR_FIRE, tolerance=5):
                    humanpause(1.5)
                    pyautogui.press("space")
                    humanpause(10 )
                    continue
                else:
                    pyautogui.press("esc")
                    current_state = "START"
                    continue

            elif current_state == "BANK":
                if find_and_click_center(COLOR_BANK, tolerance=1):
                    humanpause(0.75)

                if find_and_click_center(COLOR_BANK_ALL, tolerance=1):
                    humanpause(0.75)

                if find_and_click_center(COLOR_LOGS, tolerance=5):
                    humanpause(0.75)
                    pyautogui.press("esc")
                    humanpause(0.75)
                    current_state = "START"
                    continue

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nAvsluttet av bruker.")


if __name__ == "__main__":
    main()