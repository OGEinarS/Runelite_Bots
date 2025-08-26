import AppKit
import cv2
import pyautogui
import random
import time
import math
import numpy as np
import os
from PIL import Image

COLOR_NEXT = "FF00FF00"
COLOR_NEXT_UNAV = "FFF1FF00"
COLOR_MARK_OF_G = "FFFF0000"
COLOR_OTHER = "FFFF00DD"
COLOR_STOP = "FFFF0000"
COLOR_PIE = "FA00FF"

SCREEN_SCAN_INTERVAL = 1.2999
ACTION_DELAY = (0.1, 0.3)

PIE_COOLDOWN = 99999999999991
PIE_LAST = time.time()

def open_application(app_name):
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    workspace.launchApplication_(app_name)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 8:  # Handle ARGB format by stripping alpha
        hex_color = hex_color[2:]
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

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
    pyautogui.moveTo((x + rand1)/2, (y + rand2)/2, duration=random.uniform(*ACTION_DELAY))
    pyautogui.click(clicks=clicks)
    humanpause(0.1)

def eat_pie():
    try:
        open_application("RuneLite")
        x, y = pyautogui.locateCenterOnScreen('pie.png', confidence=0.7)
        if x and y:
            return x, y

    except:
        print("No Pie found")
        pass
    return None, None

def find_and_click_center(hex_color, tolerance=30):
    global BLOB_LOCATION
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
            screen_width, screen_height = pyautogui.size()
            BLOB_LOCATION = calculate_distance_delay(center_x, center_y, screen_width, screen_height)
            print(f"Calculated run time: {BLOB_LOCATION}.")
            return True
    return False


def calculate_distance_delay(target_x, target_y, screen_center_x, screen_center_y):
    distance = math.sqrt((target_x - screen_center_x) ** 2 + (target_y - screen_center_y) ** 2)

    MAX_DISTANCE = math.sqrt(screen_center_x**2 + screen_center_y**2)
    MIN_SLEEP = 7
    MAX_SLEEP = 20

    normalized = min(distance / MAX_DISTANCE, 1.0)
    return MIN_SLEEP + (MAX_SLEEP - MIN_SLEEP) * normalized

#def is_player_on_roof():

#def is_player_on_ground():

def main():
    global PIE_LAST, PIE_COOLDOWN
    try:
        print("Starting agility bot...")
        while True:
            launch_time = time.time()
            open_application("RuneLite")

            if time.time() - PIE_LAST > PIE_COOLDOWN:
                if find_and_click_center(COLOR_PIE, 0.1):
                    print("Pie eaten")
                    humanpause(BLOB_LOCATION)
                    PIE_COOLDOWN = random.uniform(160, 180)
                    PIE_LAST = time.time()
                    continue


            if find_and_click_center(COLOR_NEXT, 0.1):
                print("Clicked obstacle center")
                humanpause(BLOB_LOCATION)
                continue

            elapsed = time.time() - launch_time
            sleep_time = max(0, SCREEN_SCAN_INTERVAL - elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nScript suspended ;-(")

if __name__ == "__main__":
    main()