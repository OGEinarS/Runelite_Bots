import AppKit
import cv2
import pyautogui
import random
import time
import math
import numpy as np
from PIL import Image

# Color definitions
COLOR_STAIRS_DOWN = "FF00FF90"
COLOR_BANKGUY = "FFFF8F8F"
COLOR_BANK_EARTHRUNE = "FFB57E4A"
COLOR_BANK_ESSENCE = "FFCFCFCF"
COLOR_INVENTORY_POUCH = "63C1FF"
COLOR_BANK_EXIT = "FFFF8AB6"
COLOR_INVENTORY_ESSENCE = "FF00FF00"
COLOR_ZMI_ALTAR = "FFD400FF"
COLOR_SPELLBOOK = "FF7ACA00"
COLOR_TP_RESET = "FF9F42FF"
COLOR_BANK_ALL = "FFFF0026"
COLOR_INVENTORY_TAB = "FF0013FF"
COLOR_BANK_BINDING = "FF610081"
COLOR_INVENTORY_BINDING = "846DE8"
COLOR_NPC_CONTACT = "FFCDFFB4"
COLOR_PRAYER_ALTAR = "FFD400FF"
COLOR_SPELLBOOK_SWAP = "FF00CAFF"
COLOR_VILEVIGOUR = "FFE8E8E8"
COLOR_BANK_FOOD = "FFFFAD00"

ROUND_COUNT = 2


# Teleport definitions
DEFINE_TP_CASTLEWARS = 2
DEFINE_TP_ARENA = 1
BINDING_NECKLASE_USAGES = 17
COLOSSAL_POUCH_USAGES = 0


# Timing settings
ACTION_DELAY = (0.1, 0.3)

# State tracking
current_state = "START_CLIMBING"
last_state = "START_CLIMBING"


def open_application(app_name):
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    workspace.launchApplication_(app_name)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 8:  # Handle ARGB format by stripping alpha
        hex_color = hex_color[2:]
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def find_hex_color(color_input, tolerance=20):
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
    newtime = basetime + random.uniform(0.05, 0.1)
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


def find_and_click_center(hex_color, tolerance=20):
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
    global current_state, last_state,BINDING_NECKLASE_USAGES, COLOSSAL_POUCH_USAGES, ROUND_COUNT

    try:
        print("Starting Runecrafting bot...")

        while True:
            print(f"Current state: {current_state}")
            open_application("RuneLite")

            if current_state == "START_CLIMBING":
                if find_and_click_center(COLOR_STAIRS_DOWN, tolerance=1):
                    print("Climbing down to altar")
                    humanpause(4.5)
                    last_state = current_state
                    current_state = "BANK"
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "BANK":
                if find_and_click_center(COLOR_BANKGUY, tolerance=1):
                    print("Attempting to open bank")
                    humanpause(2)
                    last_state = current_state
                    current_state = "PAY_WITH_EARTHRUNES"
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "PAY_WITH_EARTHRUNES":
                if find_and_click_center(COLOR_BANK_EARTHRUNE, tolerance=1):
                    print("Paying to bank")
                    humanpause(0.2)
                    last_state = current_state
                    current_state = "BANK_ALL"
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "BANK_ALL":
                if find_and_click_center(COLOR_BANK_ALL, tolerance=1):
                    print("Attempting to bank all")
                    humanpause(0.2)
                    last_state = current_state
                    current_state = "EAT_FISH"
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "EAT_FISH":
                if find_and_click_center(COLOR_BANK_FOOD, tolerance=1):
                    print("Attempting to eat some angler fish")
                    humanpause(0.2)
                    last_state = current_state
                    if find_and_click_center(COLOR_INVENTORY_BINDING, tolerance=1):
                        humanpause(0.2)
                    current_state = "WITHDRAW_ESSENCE"
                    if BINDING_NECKLASE_USAGES <= 0: current_state = "EQUIP_NEW_AMULET"
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "EQUIP_NEW_AMULET":
                if find_and_click_center(COLOR_BANK_ALL, tolerance=1):
                    print("Equiping new amulet")
                    BINDING_NECKLASE_USAGES = 17
                    humanpause(0.2)
                    last_state = current_state
                    current_state = "WITHDRAW_ESSENCE"
                    if find_and_click_center(COLOR_BANK_BINDING, tolerance=1):
                        humanpause(0.2)
                    if find_and_click_center(COLOR_INVENTORY_BINDING, tolerance=1):
                        humanpause(0.2)
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "WITHDRAW_ESSENCE":
                if find_and_click_center(COLOR_BANK_ESSENCE, tolerance=1):
                    print("Withdrawing essence")
                    humanpause(0.2)
                    last_state = current_state
                    current_state = "FILL_POUCH"
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "FILL_POUCH":
                if find_and_click_center(COLOR_INVENTORY_POUCH, tolerance=1):
                    print("Filling pouch")
                    humanpause(0.2)
                    last_state = current_state
                    current_state = "WITHDRAW_EXTRA_ESSENCE"
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "WITHDRAW_EXTRA_ESSENCE":
                if find_and_click_center(COLOR_BANK_ESSENCE, tolerance=1):
                    print("Filling up inventory")
                    humanpause(0.2)
                    last_state = current_state
                    current_state = "FILL_POUCH_AGAIN"
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "FILL_POUCH_AGAIN":
                if find_and_click_center(COLOR_INVENTORY_POUCH, tolerance=1):
                    print("Filling pouch")
                    humanpause(0.2)
                    last_state = current_state
                    current_state = "WITHDRAW_EXTRA_ESSENCE_AGAIN"
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "WITHDRAW_EXTRA_ESSENCE_AGAIN":
                if find_and_click_center(COLOR_BANK_ESSENCE, tolerance=1):
                    print("Filling up inventory")
                    humanpause(0.2)
                    last_state = current_state
                    current_state = "EXIT_BANK"
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "EXIT_BANK":
                if find_and_click_center(COLOR_BANK_EXIT, tolerance=1):
                    print("Exitting bank interface")
                    humanpause(0.2)
                    last_state = current_state
                    current_state = "USE_RUNES_ON_ALTAR"
                    continue
                else:
                    current_state = last_state
                    continue

            if COLOSSAL_POUCH_USAGES <= 0:
                if find_and_click_center(COLOR_SPELLBOOK, tolerance=1):
                    humanpause(0.5)
                if find_and_click_center(COLOR_NPC_CONTACT, tolerance=1):
                    humanpause(0.5)
                if find_and_click_center(COLOR_BANK_EARTHRUNE, tolerance=1):
                    humanpause(4.5)

                pyautogui.press("space")
                humanpause(1)
                pyautogui.press(str(1))
                humanpause(1)
                pyautogui.press("space")
                COLOSSAL_POUCH_USAGES = 8
                if find_and_click_center(COLOR_INVENTORY_TAB, tolerance=1):
                    humanpause(0.2)
                continue

            elif current_state == "USE_RUNES_ON_ALTAR":
                if find_and_click_center(COLOR_ZMI_ALTAR, tolerance=1):
                    print("Running to wards altrar and using runes")
                    humanpause(26)
                    last_state = current_state
                    current_state = "USE_RUNES_ON_ALTAR_AGAIN"
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "USE_RUNES_ON_ALTAR_AGAIN":
                if find_and_click_center(COLOR_ZMI_ALTAR, tolerance=1):
                    print("Running to wards altrar and using runes")
                    humanpause(0.2)
                    last_state = current_state
                    current_state = "EMPTY_POUCH"
                    BINDING_NECKLASE_USAGES -= 1
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "EMPTY_POUCH":
                if find_and_click_center(COLOR_INVENTORY_POUCH, tolerance=1):
                    print("Emptying rune pouch")
                    humanpause(0.2)
                    last_state = current_state
                    current_state = "USE_RUNES_ON_ALTAR_AGAIN2"
                    COLOSSAL_POUCH_USAGES -= 1
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "USE_RUNES_ON_ALTAR_AGAIN2":
                if find_and_click_center(COLOR_ZMI_ALTAR, tolerance=1):
                    print("Making more runes")
                    humanpause(0.2)
                    last_state = current_state
                    current_state = "EMPTY_POUCH_AGAIN"
                    BINDING_NECKLASE_USAGES -= 1
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "EMPTY_POUCH_AGAIN":
                if find_and_click_center(COLOR_INVENTORY_POUCH, tolerance=1):
                    print("Emptying rune pouch")
                    humanpause(0.2)
                    last_state = current_state
                    current_state = "USE_RUNES_ON_ALTAR_AGAIN3"
                    COLOSSAL_POUCH_USAGES -= 1
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "USE_RUNES_ON_ALTAR_AGAIN3":
                if find_and_click_center(COLOR_ZMI_ALTAR, tolerance=1):
                    print("Making more runes")
                    humanpause(0.2)
                    last_state = current_state
                    current_state = "OPEN_SPELLBOOK"
                    BINDING_NECKLASE_USAGES -= 1
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "OPEN_SPELLBOOK":
                if find_and_click_center(COLOR_SPELLBOOK, tolerance=1):
                    print("Opening spellbook")
                    humanpause(0.2)
                    last_state = current_state
                    current_state = "TP_TO_RESET"
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "TP_TO_RESET":
                if find_and_click_center(COLOR_TP_RESET, tolerance=1):
                    print("Opening inventory")
                    humanpause(0.2)
                    last_state = current_state
                    current_state = "OPEN_INVENTORY"
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "OPEN_INVENTORY":
                if find_and_click_center(COLOR_INVENTORY_TAB, tolerance=1):
                    print("Teleporting")
                    humanpause(0.9)
                    last_state = current_state
                    current_state = "GOTO_ALTAR"
                    continue
                else:
                    current_state = last_state
                    continue

            elif current_state == "GOTO_ALTAR":
                if find_and_click_center(COLOR_PRAYER_ALTAR, tolerance=1):
                    print("Praying at altar")
                    humanpause(12)
                    last_state = current_state
                    current_state = "OPEN_SPELLBOOK_PRAYER_RUN"
                    continue
                else:
                    current_state = last_state
                    continue

            if ROUND_COUNT >= 3:

                if current_state == "OPEN_SPELLBOOK_PRAYER_RUN":
                    if find_and_click_center(COLOR_SPELLBOOK, tolerance=1):
                        print("Opening spellbook and restoring run energy")
                        humanpause(0.2)

                        if find_and_click_center(COLOR_SPELLBOOK_SWAP, tolerance=1):
                            humanpause(0.6)
                            pyautogui.press(str(3))
                            humanpause(0.2)

                        if find_and_click_center(COLOR_SPELLBOOK, tolerance=1):
                            humanpause(0.2)

                        if find_and_click_center(COLOR_VILEVIGOUR, tolerance=1):
                            humanpause(0.2)

                        if find_and_click_center(COLOR_INVENTORY_TAB, tolerance=1):
                            humanpause(0.2)

                        last_state = current_state
                        current_state = "START_CLIMBING"
                        ROUND_COUNT = 0
                        continue
                    else:
                        current_state = last_state
                        continue
            else:
                current_state = "START_CLIMBING"
                ROUND_COUNT += 1

            # If we get here, no action was taken this cycle
            print(f"Waiting for {current_state}...")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopped by user.")


if __name__ == "__main__":
    main()