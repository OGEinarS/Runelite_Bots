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
color_bank_chest = "FFFFAD00"
color_bh_coal = "FF8080"
color_bh_gold = "FF5BE9"
color_coalbag = "FFD98A"
color_gold_gloves = "FF7373"
color_ice_gloves = "9CFFFD"
color_melting_pot = "FFBD16DF"
color_bar_disp = "FF5A85FF"
color_inv_gold = "A2FFA5"
color_stamina = "FF2816"

lapcount = 0

coal_bag_filled = False

# Innstillinger
MIN_LOG_COUNT = 4
ACTION_DELAY = (0.03, 0.01)
LOG_TOLERANCE = 12
MIN_LOG_AREA = 5

BANK_ALL_IMAGE = os.path.join(Path(__file__).parent.parent, "bankall.png")

# State tracking
current_state = "Scanning"


def count_items_full_screen(COLOR_IMPUT):
    try:
        # Ta skjermbilde og konverter
        screenshot = pyautogui.screenshot()
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Fargegrenser
        rgb = tuple(int(COLOR_IMPUT[i:i + 2], 16) for i in (0, 2, 4))
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

    rand1 = random.uniform(-1.00, 1.00)
    rand2 = random.uniform(-1.00, 1.00)
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

def find(hex_color, tolerance=1):
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
    global current_state, coal_bag_filled, lapcount

    try:
        print("Starter bot...")
        while True:
            print(f"Tilstand: {current_state}")
            open_application("RuneLite")

            inv_gold_bar = count_items_full_screen(color_inv_gold)
            inv_gold_ore = count_items_full_screen(color_bh_gold)
            inv_coal_bag = count_items_full_screen(color_coalbag)
            inv_coal = count_items_full_screen(color_bh_coal)
            inv_ice_gloves = count_items_full_screen(color_ice_gloves)
            inv_gold_gloves = count_items_full_screen(color_gold_gloves)
            inv_stamina = count_items_full_screen(color_stamina)

            print(f"Gold ore: {inv_gold_ore}")
            print(f"Coal ore: {inv_coal}")
            print(f"Coal bag : {inv_coal_bag}")
            print(f"Gold bar : {inv_gold_bar}")
            print(f"Ice Gloves : {inv_ice_gloves}")
            print(f"Gold Gloves: {inv_gold_gloves}")
            print(f"Stamina : {inv_stamina}")
            print(f"Lapcount : {lapcount}")


            if current_state == "Scanning":
                if inv_gold_ore < 1 and inv_gold_bar < 1:
                    current_state = "Handle_bank"
                    humanpause(.33)
                    continue

                if inv_gold_bar >= 1:
                    current_state = "Handle_bank"
                    humanpause(.33)
                    continue

                if inv_gold_ore >= 2:
                    current_state = "Handle_smelting"
                    humanpause(.33)
                    continue

                else:
                    current_state = "Scanning"
                    continue

            elif current_state == "Handle_bank":
                if inv_gold_gloves > 0:
                    if find_and_click_center(color_gold_gloves, tolerance=1):
                        humanpause(0.03)
                        continue

                elif find_and_click_center(color_bank_chest, tolerance=1):
                    humanpause(3)
                    continue

                elif find_and_click_center(color_inv_gold, tolerance=2):
                    humanpause(0.03)
                    continue

                if inv_stamina < 2:
                    if find_and_click_center(color_stamina, tolerance=1):
                        humanpause(0.03)

                    if find_and_click_center(color_bh_gold, tolerance=2):
                        humanpause(0.03)
                        current_state = "Handle_smelting"
                        pyautogui.press("esc")
                    continue
                else:
                    if find_and_click_center(color_bh_gold, tolerance=2):
                        humanpause(0.03)
                        current_state = "Handle_smelting"
                        pyautogui.press("esc")
                        continue


            elif current_state == "Handle_smelting":
                if lapcount >= 12:
                    if find_and_click_center(color_stamina, tolerance=1):
                        lapcount = 0
                        humanpause(0.03)
                        continue

                if find_and_click_center(color_melting_pot, tolerance=1):
                    humanpause(8.5)
                    coal_bag_filled = False
                    current_state = "Handle_gold_bar"
                    continue

            elif current_state == "Handle_gold_bar":
                if find_and_click_center(color_ice_gloves, tolerance=1):
                    continue

                if find_and_click_center(color_bar_disp, tolerance=1):
                    humanpause(3.2)
                    lapcount += 1
                    pyautogui.press("space")
                    humanpause(0.03)
                    if find_and_click_center(color_gold_gloves, tolerance=1):
                        current_state = "Handle_bank"
                        continue


    except KeyboardInterrupt:
        print("\nAvsluttet av bruker.")


if __name__ == "__main__":
    main()