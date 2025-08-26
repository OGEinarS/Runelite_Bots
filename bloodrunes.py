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

# Color definitions
c_chisel_inv = "E7CF9C"
c_stamina_pot = "886230"
c_housetp_inv = "3C3CEF"
c_bloodrunes_inv = "FF6B6B"
c_dark_essense_inv = "8855B5"

c_dense_essense_block = "FF8C8C"
c_dark_essense_block = "6FFFCB"

c_obstacle_1 = "FF00CAFF"
c_obstacle_2 = "FFFFFC7A"
c_running_stage_1 = "FFCF97FA"
c_running_stage_2 = "FFEBFFAF"

c_dark_altar = "FFFFAD00"
c_blood_altar = "FF9FFF6D"
c_dense_runestone_obj = "FFFF00B7"

c_eat = "DDFAFF10"
c_prayer = "E195FCFF"
c_idle = "ff8ffa"
c_loot = "FFF88DFF"
c_poison = "00af00"

c_bar_hp = "EF8E8E"
c_bar_prayer = "8AFFFC"
c_bar_run = "F0DFA0"
c_bar_boss_hp = "008722"

c_player_outline = "FF743C19"

# Settings
MIN_LOG_COUNT = 4
TOTAL_INVENTORY_SPACE = 28
ACTION_DELAY = (0.05, 0.03)

valid_worlds = [303, 304, 327, 328, 351, 352, 375, 376, 457, 458]
current_world = -1
delay_time = 5 #random.uniform(5 * 3600, 5.5 * 3600)   5 - 5.5 hours
run_time = time.time()
float_start_time = "Nigger"

current_state = "MAIN_HANDLE"
last_action = "None"

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

def humanpause(basetime):
    newtime = basetime + random.uniform(0.0004, 0.0003)
    time.sleep(newtime)

def move_and_click(position, clicks=1):
    if isinstance(position, np.ndarray):
        x, y = position[0], position[1]
    else:
        x, y = position

    rand1 = random.uniform(-.25, .25)
    rand2 = random.uniform(-.25, .25)
    pyautogui.moveTo((x + rand1) / 2, (y + rand2) / 2, duration=random.uniform(*ACTION_DELAY))
    pyautogui.click(clicks=clicks)

def find(hex_color, tolerance=1):
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
            return ((center_x, center_y))
    return False

def find_and_click_close_to(target_hex, proximity_hex=None, tolerance=1, proximity_tolerance=30):
    screenshot = np.array(pyautogui.screenshot())
    img_bgr = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    target_rgb = hex_to_rgb(target_hex)[::-1]
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
        move_and_click(center)
        print(f"[CLICK] Target colour {target_hex} at {center} largest contour")
        return True

    proximity_rgb = hex_to_rgb(proximity_hex)[::-1]
    prox_lower = np.array([max(0, c - proximity_tolerance) for c in proximity_rgb])
    prox_upper = np.array([min(255, c + proximity_tolerance) for c in proximity_rgb])
    prox_mask = cv2.inRange(img_bgr, prox_lower, prox_upper)

    prox_contours, _ = cv2.findContours(prox_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not prox_contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        move_and_click((x + w // 2, y + h // 2))
        return True

    prox_centroids = []
    for c in prox_contours:
        M = cv2.moments(c)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            prox_centroids.append((cx, cy))

    closest_dist = float('inf')
    best_target = None

    for target in contours:
        M = cv2.moments(target)
        if M["m00"] > 0:
            tx = int(M["m10"] / M["m00"])
            ty = int(M["m01"] / M["m00"])

            for (px, py) in prox_centroids:
                dist = (tx - px) ** 2 + (ty - py) ** 2
                if dist < closest_dist:
                    closest_dist = dist
                    best_target = target

    if best_target is not None:
        x, y, w, h = cv2.boundingRect(best_target)
        center = (x + w // 2, y + h // 2)
        move_and_click(center)
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

    return (active_pixels / calibration) * 100

def print_player_stats(chisel=0,staminapot=0, bloodrunes=0, housetp=0, dense_e_b=0, dark_e_b=0, dark_essense=0,
                       hp=0, prayer=0, run=0, boss=0):
    print(f"__________________________________________________________________________")

    inventory_lines = []
    if chisel > 0:
        inventory_lines.append(f"Chisel")
    if bloodrunes > 0:
        inventory_lines.append(f"Blood runes")
    if housetp > 0:
        inventory_lines.append(f"House teleport tab")
    if dark_essense > 0:
        inventory_lines.append(f"Dark essense")
    if dark_e_b > 0:
        inventory_lines.append(f"Dark essense block = {dark_e_b}")
    if dense_e_b > 0:
        inventory_lines.append(f"Dense essense block = {dense_e_b}")
    if staminapot > 0:
        inventory_lines.append(f"Stamina potion = {staminapot}")

    if inventory_lines:
        print(f"[INVENTORY] " + "     ".join(inventory_lines))

    print(f"[STATS] Player Status: {current_state}     Last Action: {last_action}")
    print(f"[STATS] "
          f"HP: {min(100, max(0, round(hp, 1)))}    "
          f"PRAYER: {min(100, max(0, round(prayer, 1)))}    "
          f"STAMINA: {min(100, max(0, round(run, 1)))}    "
          f"WORLD: {current_world}    WORLD HOP IN: {int((run_time-time.time())+delay_time)}/s")
    print(f"[BOSS] Boss HP: {min(100, max(0, round(boss, 1)))}%")

    print(f"__________________________________________________________________________")
def main():
    global current_state, TOTAL_INVENTORY_SPACE, last_action, run_time, delay_time, float_start_time

    try:
        print("[MAIN] Starter-bot...")
        while True:
            open_application("RuneLite")
            hp = get_progress_bar_percentage(c_bar_hp, calibration=5673)
            prayer = get_progress_bar_percentage(c_bar_prayer, calibration=5673)
            run = get_progress_bar_percentage(c_bar_run, calibration=5673)
            boss = get_progress_bar_percentage(c_bar_boss_hp, calibration=6388, tolerance=22)

            chisel = count_items_full_screen(c_chisel_inv, 1, 75)
            bloodrunes = count_items_full_screen(c_bloodrunes_inv, 1, 75)
            dark_essense = count_items_full_screen(c_dark_essense_inv, 1, 75)
            dense_e_b = count_items_full_screen(c_dense_essense_block, 1, 75)
            dark_e_b = count_items_full_screen(c_dark_essense_block, 1, 75)

            print_player_stats(hp=hp, prayer=prayer, run=run,
                               boss=boss,
                             staminapot=0,
                             chisel=chisel,
                             bloodrunes=bloodrunes,
                             housetp=1,
                             dense_e_b=dense_e_b,
                             dark_e_b=dark_e_b,
                             dark_essense=dark_essense)



            if current_state == "MAIN_HANDLE":
                if dense_e_b >= 26:
                    current_state = "DARK_ALTAR_HANDLE"
                    last_action = "MINING"
                    continue
                if dark_e_b >= 26:
                    current_state = "BLOOD_ALTAR_HANDLE"
                    last_action = "VERNATE"
                    continue
                if dense_e_b < 26 and dark_e_b <= 0:
                    current_state = "MINING_HANDLE"
                    continue

            elif current_state == "MINING_HANDLE":
                if dense_e_b >= 26:
                    current_state = "DARK_ALTAR_HANDLE"
                    continue
                if IsColourFound(c_idle, tolerance=20):

                    if time.time() - run_time > delay_time:
                        hop_world()
                        delay_time = random.uniform(5 * 3600, 5.5 * 3600)
                        run_time = time.time()

                    if find_and_click_close_to(c_dense_runestone_obj,c_player_outline, tolerance=1, proximity_tolerance=1):
                        last_action = "MINING"
                        continue

            elif current_state == "DARK_ALTAR_HANDLE":
                if dark_e_b >= 26:
                    current_state = "BLOOD_ALTAR_HANDLE"
                    continue
                if IsColourFound(c_idle, tolerance=25):
                    if last_action == "MINING":
                        if IsColourFound(c_obstacle_1, tolerance=25):
                            find_and_click_close_to(target_hex=c_obstacle_1, proximity_hex=c_player_outline, tolerance=1,proximity_tolerance=2)
                            last_action = "OBST1"
                            continue
                    if last_action == "OBST1":
                        if IsColourFound(c_dark_altar, tolerance=25):
                            if find_and_click_close_to(c_dark_altar, proximity_hex=c_player_outline, tolerance=1,proximity_tolerance=2):
                                current_state = "BLOOD_ALTAR_HANDLE"
                                last_action = "VERNATE"
                                continue

            elif current_state == "BLOOD_ALTAR_HANDLE":
                if IsColourFound(c_idle, tolerance=25):
                    if last_action == "VERNATE":
                        if IsColourFound(c_running_stage_2, tolerance=20):
                            find_and_click_close_to(c_running_stage_2, proximity_hex=c_player_outline, tolerance=1,proximity_tolerance=2)
                            temp_chisel_pos = find(c_chisel_inv, 2)
                            temp_target_essense = (temp_chisel_pos[0], temp_chisel_pos[1] + (random.uniform(58, 68)))
                            last_action = "CHISEL"
                            for x in range(dark_e_b):
                                move_and_click(temp_chisel_pos, 1)
                                move_and_click(temp_target_essense, 1)

                            t_dark_e_b = count_items_full_screen(c_dark_essense_block, 1, 50)
                            if t_dark_e_b > 0:
                                for x in range(t_dark_e_b):
                                    move_and_click(temp_chisel_pos, 1)
                                    move_and_click(temp_target_essense, 1)

                            continue

                    if last_action == "CHISEL":
                        if IsColourFound(c_blood_altar, tolerance=20):
                            if find_and_click_close_to(c_blood_altar, proximity_hex=c_player_outline, tolerance=1,proximity_tolerance=2):
                                current_state = "RUN_BACK_TO_START"
                                last_action = "BLOODS"
                                continue

            elif current_state == "RUN_BACK_TO_START":

                t_dark_essense = count_items_full_screen(c_dark_essense_inv, 1, 50)
                if t_dark_essense > 0 and last_action == "BLOODS":
                    current_state = "BLOOD_ALTAR_HANDLE"
                    last_action = "CHISEL"
                    continue

                if IsColourFound(c_idle, tolerance=25):
                    if last_action == "BLOODS":
                        if IsColourFound(c_obstacle_2, tolerance=20):
                            if find_and_click_close_to(c_obstacle_2, proximity_hex=c_player_outline, tolerance=1, proximity_tolerance=2):
                                current_state = "MINING_HANDLE"
                                last_action = "OBST2"
                                continue
                    if last_action == "OBST2":
                        current_state = "MINING_HANDLE"
                        continue

    except KeyboardInterrupt:
        print("\n[MAIN] Stopping...")

if __name__ == "__main__":
    main()