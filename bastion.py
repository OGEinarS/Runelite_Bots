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
c_attp = "223CAB"
c_strp = "998787"
c_defp = "BD9D3D"
c_tarstol = "006900"
c_bank_b = "FFFFA400"
c_bank_all = "FF911111"


c_eat = "DDFAFF10"
c_prayer = "E195FCFF"
c_idle = "ee72f0"
c_loot = "FFF88DFF"
c_poison = "00af00"

c_bar_hp = "EF8E8E"
c_bar_prayer = "8AFFFC"
c_bar_run = "F0DFA0"
c_bar_boss_hp = "008722"

c_player_outline = "FF743C19"

# Settings
LOG_AMOUNT = 24
MIN_LOG_COUNT = 4
TOTAL_INVENTORY_SPACE = 28
ACTION_DELAY = (0.05, 0.03)

current_state = "BANK_HANDLE"
cape_status = "none"


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


def is_color_near_other_color(primary_color, secondary_color, primary_tolerance=30, secondary_tolerance=30, min_blob_size=10):
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

    rand1 = random.uniform(-.25, .25)
    rand2 = random.uniform(-.25, .25)
    pyautogui.moveTo((x + rand1) / 2, (y + rand2) / 2, duration=random.uniform(*ACTION_DELAY))
    pyautogui.click(clicks=clicks)


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


def find_and_click_close_to(target_hex, proximity_hex=None, tolerance=1, proximity_tolerance=30):
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
        move_and_click(center)
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
        move_and_click((x + w // 2, y + h // 2))
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
                dist = (tx - px) ** 2 + (ty - py) ** 2  # Squared distance
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

    return (active_pixels / calibration) * 100     #Returns: (0-100).


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


# Calibrate
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


def find_distance_to_closest(target_hex, proximity_hex=None, tolerance=1, proximity_tolerance=30):
    screenshot = np.array(pyautogui.screenshot())
    img_bgr = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    target_rgb = hex_to_rgb(target_hex)[::-1]
    target_lower = np.array([max(0, c - tolerance) for c in target_rgb])
    target_upper = np.array([min(255, c + tolerance) for c in target_rgb])
    target_mask = cv2.inRange(img_bgr, target_lower, target_upper)

    target_contours, _ = cv2.findContours(target_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not target_contours:
        return 0, 0, 0

    if not proximity_hex:
        screen_center = (img_bgr.shape[1] // 2, img_bgr.shape[0] // 2)
        closest_dist = float('inf')
        closest_target = None

        for contour in target_contours:
            M = cv2.moments(contour)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                dist = ((cx - screen_center[0]) ** 2 + (cy - screen_center[1]) ** 2) ** 0.5
                if dist < closest_dist:
                    closest_dist = dist
                    closest_target = (cx, cy)

        return closest_dist, closest_target, screen_center

    # Process proximity color
    proximity_rgb = hex_to_rgb(proximity_hex)[::-1]
    prox_lower = np.array([max(0, c - proximity_tolerance) for c in proximity_rgb])
    prox_upper = np.array([min(255, c + proximity_tolerance) for c in proximity_rgb])
    prox_mask = cv2.inRange(img_bgr, prox_lower, prox_upper)

    # Find proximity points
    prox_contours, _ = cv2.findContours(prox_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not prox_contours:
        return 0, 0, 0

    # Calculate centroids for proximity points
    prox_centers = []
    for contour in prox_contours:
        M = cv2.moments(contour)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            prox_centers.append((cx, cy))

    # Find closest target to any proximity point
    min_distance = float('inf')
    best_target = None
    best_prox = None

    for target in target_contours:
        M = cv2.moments(target)
        if M["m00"] > 0:
            tx = int(M["m10"] / M["m00"])
            ty = int(M["m01"] / M["m00"])

            for (px, py) in prox_centers:
                distance = ((tx - px) ** 2 + (ty - py) ** 2) ** 0.5  # Euclidean distance
                if distance < min_distance:
                    min_distance = distance
                    best_target = (tx, ty)
                    best_prox = (px, py)

    return min_distance, best_target, best_prox


def print_player_stats(chisel=0,staminapot=0, bloodrunes=0, housetp=0, dense_e_b=0, dark_e_b=0, dark_essense=0,
                       hp=0, prayer=0, run=0, current_state=0, boss=0, teak=0, string=0, uf_bow=0, f_bow=0,
                       d_leather=0,d_body=0, waterjug=0, grapes=0, unf=0, zamwine=0, attp=0, strp=0, defp=0, tarstol=0):
    print(f"__________________________________________________________________________")

    # only show if count > 0
    inventory_lines = []
    if chisel > 0:
        inventory_lines.append(f"Chisel")

    if d_leather > 0:
        inventory_lines.append(f"d_leather = {d_leather}")

    if attp > 0:
        inventory_lines.append(f"attp = {attp}")

    if strp > 0:
        inventory_lines.append(f"strp = {strp}")

    if defp > 0:
        inventory_lines.append(f"defp = {defp}")

    if tarstol > 0:
        inventory_lines.append(f"tarstol = {tarstol}")

    if unf > 0:
        inventory_lines.append(f"unf = {unf}")

    if zamwine > 0:
        inventory_lines.append(f"zamorack wine = {zamwine}")

    if d_body > 0:
        inventory_lines.append(f"d_body = {d_body}")

    if grapes > 0:
        inventory_lines.append(f"grapes = {grapes}")

    if waterjug > 0:
        inventory_lines.append(f"water jug = {waterjug}")

    if string > 0:
        inventory_lines.append(f"string = {string}")

    if uf_bow > 0:
        inventory_lines.append(f"uf_bow = {uf_bow}")

    if f_bow > 0:
        inventory_lines.append(f"f_bow = {f_bow}")

    if teak > 0:
        inventory_lines.append(f"Teak = {teak}")

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


    if inventory_lines:  # only print inventory if at least one item exists
        print(f"[INVENTORY] " + "     ".join(inventory_lines))

    # other stats
    print(f"[STATS] Player Status: {current_state}")
    print(f"[STATS] "
          f"HP: {min(100, max(0, round(hp, 1)))}    "
          f"PRAYER: {min(100, max(0, round(prayer, 1)))}    "
          f"STAMINA: {min(100, max(0, round(run, 1)))}")
    print(f"[BOSS] Boss HP: {min(100, max(0, round(boss, 1)))}%")


    print(f"__________________________________________________________________________")


def main():
    global current_state, TOTAL_INVENTORY_SPACE, cape_status

    try:
        print("[MAIN] Starter-bot...")
        while True:
            open_application("RuneLite")
            # STATS
            hp = get_progress_bar_percentage(c_bar_hp, calibration=5673)
            prayer = get_progress_bar_percentage(c_bar_prayer, calibration=5673)
            run = get_progress_bar_percentage(c_bar_run, calibration=5673)
            boss = get_progress_bar_percentage(c_bar_boss_hp, calibration=6388.0, tolerance=22)

            # OBJECTS
            #obst1_dist, obst1_pos, player_pos, = find_distance_to_closest(c_obstacle_1,c_player_outline,2,2)
            #obst2_dist, obst2_pos, player_pos = find_distance_to_closest(c_obstacle_2, c_player_outline, 2, 2)
            #darka_dist, darka_pos, player_pos = find_distance_to_closest(c_dark_altar, c_player_outline, 2, 2)
            #blooda_dist, blooda_pos, player_pos = find_distance_to_closest(c_blood_altar, c_player_outline, 2, 2)
            #run1_dist, run1_pos, player_pos, = find_distance_to_closest(c_running_stage_1, c_player_outline, 2, 2)
            #run2_dist, run2_pos, player_pos = find_distance_to_closest(c_running_stage_2, c_player_outline, 2, 2)
            #3denseobj_dist, denseobj_pos, denseobj_pos, = find_distance_to_closest(c_dense_runestone_obj, c_player_outline, 2, 2)
            '''
            print(f"OBST 1 {obst1_dist:}px obstacle pos ={obst1_pos} | playerpos = {player_pos}")
            print(f"OBST 2 {obst2_dist:}px obstacle pos ={obst2_pos} | playerpos = {player_pos}")
            print(f"DARKA {darka_dist:}px obstacle pos ={darka_pos} | playerpos = {player_pos}")
            print(f"BLOODA {blooda_dist:}px obstacle pos ={blooda_pos} | playerpos = {player_pos}")
            print(f"RUN1 {run1_dist:}px obstacle pos ={run1_pos} | playerpos = {player_pos}")
            print(f"RUN2 {run2_dist:}px obstacle pos ={run2_pos} | playerpos = {player_pos}")
            print(f"DENSEOBJ {denseobj_dist:}px obstacle pos ={denseobj_pos} | playerpos = {player_pos}")
            '''
            # INVENTORY
            #staminapot = count_items_full_screen(c_stamina_pot,1,50)
            #chisel = count_items_full_screen(c_chisel_inv, 1, 50)
            #housetp = count_items_full_screen(c_housetp_inv, 1, 50)
            #bloodrunes = count_items_full_screen(c_bloodrunes_inv, 1, 50)
            #dark_essense = count_items_full_screen(c_dark_essense_inv, 1, 50)
            attp = count_items_full_screen(c_attp, 1, 50)
            defp = count_items_full_screen(c_defp, 1, 50)
            strp = count_items_full_screen(c_strp, 1, 50)
            tarstol = count_items_full_screen(c_tarstol, 1, 50)
            #dense_e_b = count_items_full_screen(c_dense_essense_block, 1, 50)
            #dark_e_b = count_items_full_screen(c_dark_essense_block, 1, 50)

            # PRINT
            print_player_stats(hp=hp, prayer=prayer, run=run,
                               current_state=current_state,boss=boss,
                               staminapot=0,
                               attp=attp,
                               defp=defp,
                               strp=strp,
                               tarstol=tarstol)


            if current_state == "MAIN_HANDLE":
                if attp or strp or defp or tarstol > 1:
                    current_state = "CRAFT_HANDLE"


                if attp or strp or defp or tarstol <= 0:
                    current_state = "BANK_HANDLE"


            elif current_state == "CRAFT_HANDLE":
                if attp or strp or defp or tarstol <= 0:
                    current_state = "BANK_HANDLE"


                if IsColourFound(c_idle, tolerance=25):
                    if attp and strp and defp and tarstol > 0:
                        find_and_click_center(c_tarstol, tolerance=1)
                        humanpause(0.5)
                        find_and_click_center(c_attp, tolerance=1)
                        humanpause(1)
                        pyautogui.press("space")


            elif current_state == "BANK_HANDLE":
                if attp and strp and defp and tarstol > 0:
                    current_state = "CRAFT_HANDLE"
                    pyautogui.press("esc")


                if IsColourFound(c_idle, tolerance=25):
                    find_and_click_close_to(c_bank_b, proximity_hex=c_player_outline, tolerance=2, proximity_tolerance=2)
                    humanpause(1)
                    find_and_click_center(c_bank_all, tolerance=1)
                    humanpause(1)
                    find_and_click_center(c_attp, tolerance=1)
                    humanpause(0.25)
                    find_and_click_center(c_defp, tolerance=1)
                    humanpause(0.25)
                    find_and_click_center(c_strp, tolerance=1)
                    humanpause(0.25)
                    find_and_click_center(c_tarstol, tolerance=1)
                    humanpause(0.5)
                    pyautogui.press("esc")

                    #pyautogui._pyautogui_osx._moveTo(pyautogui.position().x,pyautogui.position().y + 4)
                    #pyautogui.click()
                    current_state = "CRAFT_HANDLE"

    except KeyboardInterrupt:
        print("\n[MAIN] Stopping...")


if __name__ == "__main__":
    main()