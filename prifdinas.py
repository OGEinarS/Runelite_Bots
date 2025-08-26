import AppKit
import os
import cv2
import pyautogui
import random
import time
import numpy as np
from PIL import Image
from PIL import ImageGrab
from collections import deque
from pathlib import Path

# Color definitions
c_portal = "FFFF0060"
c_agility_obstacle = "FF75FF75"
c_mark = "FFFF8585"

obstacles = ["FFFC98FF",
            "FFBD225C",
            "FF9CD7FF",
            "FF846591",
            "FF637D8E",
            "FF6385D2",
            "FF001486",
            "FF9265CD",
            "FFFCAC56",
            "FFAFDFFF",
            "FF9728FF",
            "FF705871",
            "FFFF9FC3"]

c_eat = "DDFAFF10"
c_prayer = "E195FCFF"
c_idle = "ee72f0"
c_loot = "FFF88DFF"

# Innstillinger
ACTION_DELAY = (0.05, 0.03)
LAST_CLICKED_COLOR = deque(maxlen=7)

BANK_ALL_IMAGE = os.path.join(Path(__file__).parent.parent, "bankall.png")

# State tracking
current_state = "START"


def count_items_full_screen(COLOR_IMPUT, tolerance=1, MIN_AREA=1):
    try:
        # Ta skjermbilde og konverter
        screenshot = pyautogui.screenshot()
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Fargegrenser
        rgb = tuple(int(COLOR_IMPUT[i:i + 2], 16) for i in (0, 2, 4))
        lower = np.array([max(0, c - tolerance) for c in rgb[::-1]])
        upper = np.array([min(255, c + tolerance) for c in rgb[::-1]])

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

def IsColourFound(COLOR_INPUT,tolerance=30):
    find_rgb = hex_to_rgb(COLOR_INPUT)
    screenshot = pyautogui.screenshot()
    img = np.array(screenshot)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    l_bound = np.array([max(0, c - tolerance) for c in find_rgb[::-1]])
    u_bound = np.array([min(255, c + tolerance) for c in find_rgb[::-1]])

    mask = cv2.inRange(img, l_bound, u_bound)
    locations = cv2.findNonZero(mask)
    return True if locations is not None else []


def is_color_near_other_color(primary_color, secondary_color, primary_tolerance=30, secondary_tolerance=30, min_blob_size=10):
    # Take screenshot and convert to OpenCV format
    screenshot = pyautogui.screenshot()
    img = np.array(screenshot)
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Process primary color
    primary_rgb = hex_to_rgb(primary_color)[::-1]  # Convert to BGR
    primary_lower = np.array([max(0, c - primary_tolerance) for c in primary_rgb])
    primary_upper = np.array([min(255, c + primary_tolerance) for c in primary_rgb])
    primary_mask = cv2.inRange(img_bgr, primary_lower, primary_upper)

    # Find primary color contours
    primary_contours, _ = cv2.findContours(primary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in primary_contours:
        if cv2.contourArea(contour) > min_blob_size:
            # Get bounding rectangle of primary color
            x, y, w, h = cv2.boundingRect(contour)

            # Crop region of interest
            roi = img_bgr[y:y + h, x:x + w]

            # Process secondary color within ROI
            secondary_rgb = hex_to_rgb(secondary_color)[::-1]
            secondary_lower = np.array([max(0, c - secondary_tolerance) for c in secondary_rgb])
            secondary_upper = np.array([min(255, c + secondary_tolerance) for c in secondary_rgb])
            secondary_mask = cv2.inRange(roi, secondary_lower, secondary_upper)

            # Check if secondary color exists in ROI
            if cv2.countNonZero(secondary_mask) > 0:
                center_x = x + w // 2
                center_y = y + h // 2
                return True, (center_x, center_y)

    return False, None


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


def check_agility_obstacles(tolerance=30):
    global LAST_CLICKED_COLOR

    for color in obstacles:  # Uses your predefined obstacles list
        # Find all locations with this color
        if color in LAST_CLICKED_COLOR:
            continue

        screenshot = np.array(pyautogui.screenshot())
        screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        target_color = hex_to_rgb(color)[::-1]
        lower_bound = np.array([max(0, c - tolerance) for c in target_color])
        upper_bound = np.array([min(255, c + tolerance) for c in target_color])

        mask = cv2.inRange(screenshot_bgr, lower_bound, upper_bound)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) > 1:
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w // 2
                center_y = y + h // 2
                move_and_click((center_x, center_y))
                LAST_CLICKED_COLOR.append(color)
                print(f"Clicked obstacle with color {color} at ({center_x}, {center_y})")
                return True  # Found and clicked an obstacle

    LAST_CLICKED_COLOR.clear()
    return False  # No obstacles found


def main():
    global current_state

    try:
        print("Starter Firemaking-bot...")
        while True:
            print(f"Tilstand: {current_state}")
            open_application("RuneLite")
            mark = count_items_full_screen(c_mark,0,50)
            print(f"Inventar.")
            print(f"Marks of grace: {mark}")

            if current_state == "START":
                if IsColourFound(c_idle, tolerance=10):
                    print("Portal/Mark Found")
                    if IsColourFound(c_portal, tolerance=1):
                        find_and_click_center(c_portal, tolerance=1)
                        continue

                if IsColourFound(c_idle, tolerance=10):
                    print("Character is idle")
                    if check_agility_obstacles(tolerance=1):
                        humanpause(0.33)  # Wait for obstacle completion
                        continue
                else:
                    print("Character is moving")
                    continue

                # Then check for idle state

                # Fallback action
                humanpause(0.33)


    except KeyboardInterrupt:
        print("\nAvsluttet av bruker.")


if __name__ == "__main__":
    main()