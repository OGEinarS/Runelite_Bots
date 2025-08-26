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
from collections import deque


# Color Definitions
c_i_bones2banana = "FFD98A"
c_i_banana = "FF8080"
c_i_tails = "252BC2"
c_i_bones = "CF1639"

c_g_boulder_main = "FFA8FCFA"
c_g_bones = "21758B"

# Main Definitions and Settings
game_tick = 0.66
c_shadow_veil = "4c0566"
c_eat = "DDFAFF10"
c_prayer = "E195FCFF"
c_idle = "ee72f0"
c_loot = "FFF88DFF"

c_bar_hp = "EF8E8E"
c_bar_prayer = "8AFFFC"
c_bar_run = "F0DFA0"

c_player_outline = "FF743C19"

ACTION_DELAY = (0.05, 0.03)

current_state = "SCAN"


def count_items_full_screen(COLOR_IMPUT, tolerance=1, MIN_AREA=1):
    try:
        screenshot = pyautogui.screenshot()
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        rgb = tuple(int(COLOR_IMPUT[i:i + 2], 16) for i in (0, 2, 4))
        lower = np.array([max(0, c - tolerance) for c in rgb[::-1]])
        upper = np.array([min(255, c + tolerance) for c in rgb[::-1]])

        mask = cv2.inRange(img, lower, upper)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return len([c for c in contours if cv2.contourArea(c) > MIN_AREA])

    except Exception as e:
        print(f"[COUNT] Counting error: {e}")
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

def is_color_near_other_color(primary_color, secondary_color, primary_tolerance=30, secondary_tolerance=30, min_blob_size=10, click=0):
    screenshot = pyautogui.screenshot()
    img = np.array(screenshot)
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    primary_rgb = hex_to_rgb(primary_color)[::-1]  # Convert to BGR
    primary_lower = np.array([max(0, c - primary_tolerance) for c in primary_rgb])
    primary_upper = np.array([min(255, c + primary_tolerance) for c in primary_rgb])
    primary_mask = cv2.inRange(img_bgr, primary_lower, primary_upper)

    primary_contours, _ = cv2.findContours(primary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in primary_contours:
        if cv2.contourArea(contour) > min_blob_size:
            x, y, w, h = cv2.boundingRect(contour)

            roi = img_bgr[y:y + h, x:x + w]

            secondary_rgb = hex_to_rgb(secondary_color)[::-1]
            secondary_lower = np.array([max(0, c - secondary_tolerance) for c in secondary_rgb])
            secondary_upper = np.array([min(255, c + secondary_tolerance) for c in secondary_rgb])
            secondary_mask = cv2.inRange(roi, secondary_lower, secondary_upper)

            if cv2.countNonZero(secondary_mask) > 0:
                center_x = x + w // 2
                center_y = y + h // 2
                if click > 0:
                    move_and_click(center_x,center_y)

                return True, (center_x, center_y)

    return False, None

def humanpause(basetime):
    newtime = basetime + random.uniform(0.0004, 0.0003)
    time.sleep(newtime)

def move_and_click(position, clicks=1, interval=1.0):
    if isinstance(position, np.ndarray):
        x, y = position[0], position[1]
    else:
        x, y = position

    rand1 = random.uniform(-.50, .50)
    rand2 = random.uniform(-.50, .50)
    pyautogui.moveTo((x + rand1) / 2, (y + rand2) / 2, duration=random.uniform(*ACTION_DELAY))
    humanpause(random.uniform(*ACTION_DELAY))
    pyautogui.click(clicks=clicks, interval=interval)

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
            print(f"[CLICK] Colour {hex_color} clicked at: {center_x}, {center_y}")
            return True
    return False

def find_and_click_close_to(target_hex, proximity_hex=None, tolerance=1, proximity_tolerance=30, clicks=1, interval=1.0):
    screenshot = np.array(pyautogui.screenshot())
    img_bgr = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    target_rgb = hex_to_rgb(target_hex)[::-1]  # Convert to BGR
    lower = np.array([max(0, c - tolerance) for c in target_rgb])
    upper = np.array([min(255, c + tolerance) for c in target_rgb])
    target_mask = cv2.inRange(img_bgr, lower, upper)

    contours, _ = cv2.findContours(target_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return False

    if not proximity_hex:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        center = (x + w // 2, y + h // 2)
        move_and_click(center, clicks=clicks, interval=interval)
        print(f"[CLICK] Target colour {target_hex} at {center} largest contour")
        return True

    proximity_rgb = hex_to_rgb(proximity_hex)[::-1]
    prox_lower = np.array([max(0, c - proximity_tolerance) for c in proximity_rgb])
    prox_upper = np.array([min(255, c + proximity_tolerance) for c in proximity_rgb])
    prox_mask = cv2.inRange(img_bgr, prox_lower, prox_upper)

    prox_contours, _ = cv2.findContours(prox_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not prox_contours:
        print(f"[DETECT] No proximity color {proximity_hex} found, using largest target contour")
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        move_and_click((x + w // 2, y + h // 2), clicks=clicks, interval=interval)
        return True

    prox_centroids = []
    for c in prox_contours:
        M = cv2.moments(c)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            prox_centroids.append((cx, cy))

    if not prox_centroids:
        print("[DETECT] Proximity color found but no valid centroids")
        return False

    closest_dist = float('inf')
    best_target = None

    for target in contours:
        M = cv2.moments(target)
        if M["m00"] > 0:
            tx = int(M["m10"] / M["m00"])
            ty = int(M["m01"] / M["m00"])

            for (px, py) in prox_centroids:
                dist = (tx - px) ** 2 + (ty - py) ** 2  # Squared distance (faster)
                if dist < closest_dist:
                    closest_dist = dist
                    best_target = target

    if best_target is not None:
        x, y, w, h = cv2.boundingRect(best_target)
        center = (x + w // 2, y + h // 2)
        rand1 = random.uniform(-.50, .50)
        rand2 = random.uniform(-.50, .50)
        pyautogui.click((center[0] + rand1) / 2, (center[1] + rand2) / 2, clicks=clicks, interval=interval)
        print(f"[CLICK] Target colour {target_hex} at {center} (closest to {proximity_hex})")
        return True

    return False

def get_progress_bar_percentage(active_hex, bg_hex=None, tolerance=10, min_blob_size=10, calibration=1000):
    screenshot = pyautogui.screenshot()
    img = np.array(screenshot)
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    active_rgb = hex_to_rgb(active_hex)[::-1]
    lower = np.array([max(0, c - tolerance) for c in active_rgb])
    upper = np.array([min(255, c + tolerance) for c in active_rgb])

    mask = cv2.inRange(img_bgr, lower, upper)

    if bg_hex:
        bg_rgb = hex_to_rgb(bg_hex)[::-1]
        bg_lower = np.array([max(0, c - tolerance) for c in bg_rgb])
        bg_upper = np.array([min(255, c + tolerance) for c in bg_rgb])
        bg_mask = cv2.inRange(img_bgr, bg_lower, bg_upper)
        mask = cv2.bitwise_and(mask, cv2.bitwise_not(bg_mask))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    active_pixels = 0

    for contour in contours:
        if cv2.contourArea(contour) > min_blob_size:
            active_pixels += cv2.contourArea(contour)

    return (active_pixels / calibration) * 100     #Returns: Percentage (0-100) of the filled progress bar.

def calibrate_total_pixels(active_hex, tolerance=10):
    screenshot = pyautogui.screenshot()
    img = np.array(screenshot)
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    active_rgb = hex_to_rgb(active_hex)[::-1]
    lower = np.array([max(0, c - tolerance) for c in active_rgb])
    upper = np.array([min(255, c + tolerance) for c in active_rgb])
    mask = cv2.inRange(img_bgr, lower, upper)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    active_pixels = sum(cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 10)

    print(f"[CALIBRATE] Total active pixels at 100%: {active_pixels}")
    return active_pixels

# Example: Calibrate
#total_pixels = calibrate_total_pixels("#FF0000")

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
            print(f"[CLICK] Colour {hex_color} clicked at:   {center_x}, {center_y}")
            click_count += 1

    return click_count

def print_player_stats(sarabrew=0, supres=0, hp=0, prayer=0, run=0, cannon_status=0, div_ranging_potion=0, sharks=0):
    print(f"__________________________________________________________________________")

    # only show if count > 0
    inventory_lines = []
    if sarabrew > 0:
        inventory_lines.append(f"Healing = {sarabrew}")
    if supres > 0:
        inventory_lines.append(f"Super Restore = {supres}")
    if div_ranging_potion > 0:
        inventory_lines.append(f"Divine Ranging potion = {div_ranging_potion}")
    if sharks > 0:
        inventory_lines.append(f"Sharks = {sharks}")

    if inventory_lines:  # only print inventory if at least one item exists
        print(f"[INVENTORY] " + "     ".join(inventory_lines))

    # other stats
    print(f"[STATS] Player Status: {current_state}")
    print(f"[STATS] "
          f"HP: {min(100, max(0, round(hp, 1)))}    "
          f"PRAYER: {min(100, max(0, round(prayer, 1)))}    "
          f"STAMINA: {min(100, max(0, round(run, 1)))}")
    print(f"[Cannon] Cannon Status: {cannon_status}")

    print(f"__________________________________________________________________________")

def main():
    global current_state

    try:
        print("[MAIN] Starter-bot...")
        while True:
            open_application("RuneLite")
            # COUNT IVENTORY ITEMS = count_items_full_screen(c_superres_inv,1,50)
            # CHECK IF COLOR IS NEAR ANOTHER =  is_color_near_other_color(c_canon, c_canon_out_ammo, 10,10, 1)
            # GET PERCENTAGE FROM HP BAR = get_progress_bar_percentage(c_bar_prayer,calibration=5673)
            # DEBUG STATS = print_player_stats(sarabrew=sarabrew, supres=supres, hp=hp, prayer=prayer, run=run, current_state=current_state, sharks=sharks)

            bananas = count_items_full_screen(c_i_banana,1,50)
            tails = count_items_full_screen(c_i_tails,1,50)
            bones = count_items_full_screen(c_i_bones, 1, 50)
            print(f"bananas {bananas}, tails {tails}, bones {bones}, state {current_state}")


            if current_state == "SCAN":
                if tails > 0:
                    find_and_click_center(c_i_tails, tolerance=1)
                    continue

                if bananas > 0:
                    current_state = "TRAP_HANDLE"
                    continue

                if bones > 0:
                    find_and_click_center(c_i_bones2banana, tolerance=1)
                    continue

                if bananas < 27:
                    current_state = "COLLECT_BANANAS"
                    continue


            elif current_state == "COLLECT_BANANAS":
                if tails > 0:
                    find_and_click_center(c_i_tails, tolerance=1)
                    continue

                if bananas > 0:
                    find_and_click_center(c_i_banana, tolerance=1)
                    continue

                if bones >= 27:
                    find_and_click_center(c_i_bones2banana, tolerance=1)
                    current_state = "TRAP_HANDLE"
                    continue

                if IsColourFound(c_idle, tolerance=35):
                    find_and_click_close_to(target_hex=c_g_bones, proximity_hex=c_player_outline, tolerance=15, proximity_tolerance=2, clicks=2, interval=0.2)
                    continue

            elif current_state == "TRAP_HANDLE":
                if bones >= 27:
                    find_and_click_center(c_i_bones2banana, tolerance=1)
                    continue

                if bananas > 0 and IsColourFound(c_idle, tolerance=35):
                    find_and_click_center(c_g_boulder_main, tolerance=1)
                    if tails > 0:
                        find_and_click_center(c_i_tails, tolerance=1)
                    continue

                if bananas <= 0:
                    current_state = "COLLECT_BANANAS"
                    continue


    except KeyboardInterrupt:
        print("\n[MAIN] Stopping...")


if __name__ == "__main__":
    main()