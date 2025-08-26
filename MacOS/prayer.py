import AppKit
import cv2
import pyautogui
import random
import time
import math
import numpy as np
from PIL import Image

# Color definitions
COLOR_NOTE_GUY = "FF00CAFF"
COLOR_NOTE_INVENTORY = "FF00B7"
COLOR_BROWSE_TELEPORTS = "FFFFFF00"
COLOR_ALTAR = "FFFFAD00"
COLOR_BONES_INVENTORY = "886DFF"
COLOR_TELEPORT_HOUSE = "FFFF0000"

# Teleport definitions
DEFINE_TP_CASTLEWARS = 2
DEFINE_TP_ARENA = 1


# Timing settings
ACTION_DELAY = (0.1, 0.3)

# State tracking
current_state = "START"


def open_application(app_name):
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    workspace.launchApplication_(app_name)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 8:  # Handle ARGB format by stripping alpha
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
    newtime = basetime + random.uniform(0.05, 0.3)
    time.sleep(newtime)


def move_and_click(position, clicks=1):
    if isinstance(position, np.ndarray):
        x, y = position[0], position[1]
    else:
        x, y = position

    rand1 = random.randint(-3, 3)
    rand2 = random.randint(-3, 3)
    pyautogui.moveTo((x + rand1) / 2, (y + rand2) / 2, duration=random.uniform(*ACTION_DELAY))
    pyautogui.click(clicks=clicks)
    humanpause(0.1)


def find_and_click_center(hex_color, tolerance=30):
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
            print(f"Clicked {hex_color} at ({center_x}, {center_y})")
            return True
    return False


def main():
    global current_state, BINDING_NECKLASE_USAGES, COLOSSAL_POUCH_USAGES, ROUND_COUNT

    try:
        print("Starting Runecrafting bot...")

        while True:
            print(f"Current state: {current_state}")
            open_application("RuneLite")

            if current_state == "START":
                print("Using bones on the noted guy.")

                if find_and_click_center(COLOR_NOTE_INVENTORY, tolerance=1):
                    humanpause(0.4)
                if find_and_click_center(COLOR_NOTE_GUY, tolerance=1):
                    humanpause(2)
                    pyautogui.press(str(3))
                    current_state = "TELEPORT"
                    continue
                else:
                    pass

            elif current_state == "TELEPORT":
                print("Attempting to teleport to house")
                if find_and_click_center(COLOR_BROWSE_TELEPORTS, tolerance=1):
                    humanpause(5)
                    current_state = "USE_BONES_ON_ALTAR"
                    continue
                else:
                    pass

            elif current_state == "USE_BONES_ON_ALTAR":
                print("Attempting to use bones on altar.")
                if find_and_click_center(COLOR_BONES_INVENTORY, tolerance=1):
                    humanpause(0.5)

                if find_and_click_center(COLOR_ALTAR, tolerance=1):
                    humanpause(64)

                    current_state = "TELEPORT_OUT"
                    continue
                else:
                    pass

            elif current_state == "TELEPORT_OUT":
                print("Attempting to teleport out")
                if find_and_click_center(COLOR_TELEPORT_HOUSE, tolerance=1):
                    humanpause(3)
                    current_state = "RUN_TO_BONES_GUY"
                    continue
                else:
                    pass

            elif current_state == "RUN_TO_BONES_GUY":
                print("Attempting to run")
                if find_and_click_center(COLOR_NOTE_GUY, tolerance=1):
                    humanpause(2.5)
                    current_state = "START"
                    continue
                else:
                    pass

            # If we get here, no action was taken this cycle
            print(f"Waiting for {current_state}...")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopped by user.")


if __name__ == "__main__":
    main()