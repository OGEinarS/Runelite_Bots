import AppKit
import cv2
import pyautogui
import random
import time
import math
import numpy as np
from PIL import Image

# Color definitions
COLOR_HOUSE_TP = "FF8700"
COLOR_EARTH_RUNE = "FF0000"
COLOR_ESSENCE = "FFB57E4A"
COLOR_JEWELRY = "#ffff00"
COLOR_BANK = "#ffff00"
COLOR_RUNEP1 = "00FF90"
COLOR_RUNEP2 = "00FF90"
COLOR_CLOSE_BANK = "FFFA00FF"
COLOR_SPELLBOOK = "FF00FAFF"
COLOR_IMBUE = "FF9AFFC7"
COLOR_INVENTORY = "FFFF8F8F"
COLOR_BINDING_BANK = "FFE59BDE"
COLOR_BINDING_INV = "846DE8"
COLOR_NPC_CONTACT = "#FF972E9D"
COLOR_DARK_MAGE = "#FFAE9560"

# Teleport definitions
DEFINE_TP_CASTLEWARS = 2
DEFINE_TP_ARENA = 1

# Timing settings
ACTION_DELAY = (0.1, 0.3)

# State tracking
current_state = "BANKING"
BINDING_NECKLASE_USAGES = 0 # ADJUST BF START
COLOSSAL_POUCH_USAGES = 0 # ADJUST BF START


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
    global current_state, BINDING_NECKLASE_USAGES, COLOSSAL_POUCH_USAGES

    try:
        print("Starting Runecrafting bot...")

        while True:
            print(f"Current state: {current_state}")
            open_application("RuneLite")

            if current_state == "BANKING":
                if find_and_click_center(COLOR_BANK, tolerance=1):
                    print("Opening bank")
                    humanpause(4)
                    current_state = "WITHDRAW_ESSENCE"

                    if BINDING_NECKLASE_USAGES <= 0: # EQUIP NEW NECKLASE
                        BINDING_NECKLASE_USAGES = 17
                        if find_and_click_center(COLOR_BINDING_BANK, tolerance=1):humanpause(1)
                        if find_and_click_center(COLOR_BINDING_INV, tolerance=1): humanpause(1)
                    continue
                else:
                    pass

            elif current_state == "WITHDRAW_ESSENCE":
                if find_and_click_center(COLOR_ESSENCE, tolerance=1):
                    print("Withdrawing essence")
                    humanpause(0.5)
                    current_state = "LOAD_POUCH1"
                    continue
                else:
                    pass

            elif current_state == "LOAD_POUCH1":
                if find_and_click_center(COLOR_RUNEP1, tolerance=1):
                    print("Loading pouch 1")
                    COLOSSAL_POUCH_USAGES -= 1
                    humanpause(0.5)
                    current_state = "WITHDRAW_EXTRA_ESSENCE"
                    continue
                else:
                    pass

            elif current_state == "WITHDRAW_EXTRA_ESSENCE":
                if find_and_click_center(COLOR_ESSENCE, tolerance=1):
                    print("Withdrawing essence")
                    humanpause(0.5)
                    current_state = "CLOSE_BANK"
                    continue
                else:
                    pass

            elif current_state == "CLOSE_BANK":
                if find_and_click_center(COLOR_CLOSE_BANK, tolerance=1):
                    print("Closing bank")
                    humanpause(0.5)
                    current_state = "TELEPORT_HOME"
                    continue
                else:
                    pass

            if COLOSSAL_POUCH_USAGES <= 0:
                if find_and_click_center(COLOR_SPELLBOOK, tolerance=1): humanpause(1)
                if find_and_click_center(COLOR_NPC_CONTACT, tolerance=1): humanpause(3)
                if find_and_click_center(COLOR_DARK_MAGE, tolerance=1): humanpause(5)
                pyautogui.press("space")
                humanpause(2)
                pyautogui.press(str(1))
                humanpause(2)
                pyautogui.press("space")
                COLOSSAL_POUCH_USAGES = 10
                if find_and_click_center(COLOR_INVENTORY, tolerance=1): humanpause(3)

            elif current_state == "TELEPORT_HOME":
                if find_and_click_center(COLOR_HOUSE_TP, tolerance=1):
                    print("Teleporting home")
                    humanpause(5)
                    current_state = "USE_JEWELRY"
                    continue
                else:
                    pass

            elif current_state == "USE_JEWELRY":
                if find_and_click_center(COLOR_JEWELRY, tolerance=1):
                    print("Using jewelry box")
                    humanpause(3)
                    pyautogui.press(str(DEFINE_TP_ARENA))
                    print("Teleporting to Arena")
                    humanpause(3)
                    current_state = "ENTER_ALTAR"
                    continue
                else:
                    pass

            elif current_state == "ENTER_ALTAR":
                if find_and_click_center(COLOR_JEWELRY, tolerance=1):
                    print("Entering altar")
                    humanpause(10)
                    current_state = "OPEN_SPELLBOOK"
                    continue
                else:
                    pass

            elif current_state == "OPEN_SPELLBOOK":
                if find_and_click_center(COLOR_SPELLBOOK, tolerance=1):
                    print("Opening spellbook")
                    humanpause(0.2)
                    current_state = "CAST_IMBUE"
                    continue
                else:
                    pass

            elif current_state == "CAST_IMBUE":
                if find_and_click_center(COLOR_IMBUE, tolerance=1):
                    print("Casting magic imbue")
                    humanpause(0.2)
                    current_state = "OPEN_INVENTORY"
                    continue
                else:
                    pass

            elif current_state == "OPEN_INVENTORY":
                if find_and_click_center(COLOR_INVENTORY, tolerance=1):
                    print("Entering inventrory")
                    humanpause(0.2)
                    current_state = "CRAFT_RUNES_EARTH"
                    continue
                else:
                    pass

            elif current_state == "CRAFT_RUNES_EARTH":
                if find_and_click_center(COLOR_EARTH_RUNE, tolerance=1):
                    print("Crafting runes")
                    humanpause(0.2)
                    current_state = "CRAFT_RUNES_ALTAR"
                    continue
                else:
                    pass

            elif current_state == "CRAFT_RUNES_ALTAR":
                if find_and_click_center(COLOR_JEWELRY, tolerance=1):
                    print("Crafting runes")
                    BINDING_NECKLASE_USAGES -= 1
                    humanpause(2.5)
                    current_state = "EMPTY_POUCH1"
                    continue
                else:
                    pass

            elif current_state == "EMPTY_POUCH1":
                if find_and_click_center(COLOR_RUNEP1, tolerance=1):
                    print("Emptying pouch 1")
                    humanpause(0.2)
                    current_state = "OPEN_SPELLBOOK2"
                    continue
                else:
                    pass

            elif current_state == "OPEN_SPELLBOOK2":
                if find_and_click_center(COLOR_SPELLBOOK, tolerance=1):
                    print("Opening spellbook")
                    humanpause(0.2)
                    current_state = "CAST_IMBUE2"
                    continue
                else:
                    pass

            elif current_state == "CAST_IMBUE2":
                if find_and_click_center(COLOR_IMBUE, tolerance=1):
                    print("Casting magic imbue")
                    humanpause(0.2)
                    current_state = "OPEN_INVENTORY2"
                    continue
                else:
                    pass

            elif current_state == "OPEN_INVENTORY2":
                if find_and_click_center(COLOR_INVENTORY, tolerance=1):
                    print("Entering inventrory")
                    humanpause(0.2)
                    current_state = "CRAFT_RUNES_EARTH2"
                    continue
                else:
                    pass

            elif current_state == "CRAFT_RUNES_EARTH2":
                if find_and_click_center(COLOR_EARTH_RUNE, tolerance=1):
                    print("Crafting runes")
                    humanpause(0.5)
                    current_state = "CRAFT_RUNES_ALTAR2"
                    continue
                else:
                    pass

            elif current_state == "CRAFT_RUNES_ALTAR2":
                if find_and_click_center(COLOR_JEWELRY, tolerance=1):
                    print("Crafting runes")
                    BINDING_NECKLASE_USAGES -= 1
                    humanpause(1.5)
                    current_state = "TELEPORT_HOME_2"
                    continue
                else:
                    pass

            elif current_state == "TELEPORT_HOME_2":
                if find_and_click_center(COLOR_HOUSE_TP, tolerance=1):
                    print("Teleporting home again")
                    humanpause(5)
                    current_state = "USE_JEWELRY_CW"
                    continue
                else:
                    pass

            elif current_state == "USE_JEWELRY_CW":
                if find_and_click_center(COLOR_JEWELRY, tolerance=1):
                    print("Using jewelry box for Castle Wars")
                    humanpause(5)
                    pyautogui.press(str(DEFINE_TP_CASTLEWARS))
                    print("Teleporting to Castle Wars")
                    humanpause(5)
                    current_state = "BANKING"  # Loop back to start
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