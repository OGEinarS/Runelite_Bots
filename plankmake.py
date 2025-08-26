import AppKit
import pyautogui
import random
import time
import os
from PIL import Image

# Configuration
IMAGE_PATH_BANKCHEST = "bchest.png"
IMAGE_PATH_BANKDEPOSIT = "depositall.png"
IMAGE_PATH_MLOG = "mlog.png"
IMAGE_PATH_MPLANK = "mplank.png"
IMAGE_PATH_SPELLBOOK = "spellbook.png"
IMAGE_PATH_PLANKMAKE = "spellpm.png"
IMAGE_PATH_BANKCLOSE = "x.png"
IMAGE_PATH_SPELLBOOK_S = "spellbookselected.png"
IMAGE_PATH_PRAYERICON = "prayericon.png"

# Constants
ACTION_DELAY = (0.1, 0.3)  # Random delay range for human-like actions
WAIT_DELAY = 1  # Fixed delay for state changes


def open_application(app_name):
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    workspace.launchApplication_(app_name)


def find_pos_on_screen(image_path, confidence=0.9):
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        return None

    try:
        pos = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        return pos
    except Exception as e:
        print(f"[ERROR] Image search failed for {image_path}: {str(e)}")
        return None


def is_bank_open():
    return find_pos_on_screen(IMAGE_PATH_BANKCLOSE, confidence=0.7) is not None


def open_bank():
    bank = find_pos_on_screen(IMAGE_PATH_BANKCHEST, confidence=0.7)
    if bank:
        move_and_click(bank)
        time.sleep(WAIT_DELAY * 2)  # Extra time for bank to open
        return True
    print("[ERROR] Could not find bank chest")
    return False


def close_bank():
    if is_bank_open():
        xbox = find_pos_on_screen(IMAGE_PATH_BANKCLOSE, confidence=0.7)
        if xbox:
            move_and_click(xbox)
            time.sleep(WAIT_DELAY)
            return True
    return False


def move_and_click(position, clicks=1):
    x, y = position
    rand1 = random.randint(-1, 1)
    rand2 = random.randint(-1, 1)
    pyautogui.moveTo(x+rand1, y+rand2, duration=random.uniform(*ACTION_DELAY))
    pyautogui.click(clicks=clicks)


def get_logs():
    if not is_bank_open() and not open_bank():
        return False

    plank = find_pos_on_screen(IMAGE_PATH_MPLANK, confidence=0.7)
    if plank:
        move_and_click(plank)
        time.sleep(WAIT_DELAY)
        return True
    print("[ERROR] Could not find mahogany logs in bank")
    return False


def deposit_all():
    if not is_bank_open() and not open_bank():
        return False

    deposit = find_pos_on_screen(IMAGE_PATH_BANKDEPOSIT, confidence=0.7)
    if deposit:
        move_and_click(deposit)
        time.sleep(WAIT_DELAY)
        return True
    print("[ERROR] Could not find deposit button")
    return False


def is_spell_book_selected():
    return find_pos_on_screen(IMAGE_PATH_SPELLBOOK_S, confidence=0.7) is not None


def select_spellbook():
    if not is_spell_book_selected():
        spellbook = find_pos_on_screen(IMAGE_PATH_SPELLBOOK, confidence=0.7)
        if spellbook:
            move_and_click(spellbook)
            time.sleep(WAIT_DELAY)
            return True
        print("[ERROR] Could not find spellbook icon")
    return False


def make_planks():
    if is_bank_open() and not close_bank():
        return False

    if not select_spellbook():
        return False

    time.sleep(WAIT_DELAY)
    plankmake = find_pos_on_screen(IMAGE_PATH_PLANKMAKE, confidence=0.7)
    if plankmake:
        move_and_click(plankmake)
        time.sleep(WAIT_DELAY)

        logs = find_pos_on_screen(IMAGE_PATH_MLOG, confidence=0.7)
        if logs:
            move_and_click(logs)
            print("[SUCCESS] Started making planks")
            time.sleep(WAIT_DELAY * 3)  # Wait for spell to complete
            return True
    print("[ERROR] Could not cast plank make spell")
    return False


def check_inventory():
    has_plank = find_pos_on_screen(IMAGE_PATH_MPLANK, confidence=0.7) is not None
    has_logs = find_pos_on_screen(IMAGE_PATH_MLOG, confidence=0.7) is not None

    if has_plank:
        if deposit_all():
            print("[SUCCESS] Deposited planks")

    if has_logs:
        if make_planks():
            print("[SUCCESS] Made planks from logs")

    return has_logs or has_plank

def humanpause(basetime):
    newtime = basetime + random.uniform(0.05, 0.3)
    time.sleep(newtime)

def is_loggedin():
    try:
        if find_pos_on_screen(IMAGE_PATH_PRAYERICON): return True
        else: return False
    except: return False


logs_in_bank = 443, 240
exit_bank = 698, 94
spellbook = 1167, 545
cast_plankmake = 1134, 718
logs_in_inv = 1045, 588
bank_booth = 677, 454
login_button = 597, 338
click_2_play = 597, 420
bank_tab = 455, 133

firstpass = 1
needbankpin = False

human_pause_cooldown = random.randint(3550, 4000)
human_pause_last_time = time.time()

try:
    while True:

        open_application("RuneLite")
        if is_loggedin() == False:
            move_and_click(login_button)
            humanpause(12)
            move_and_click(click_2_play)
            humanpause(5)
            needbankpin = True
            continue
            '''if time.time() - human_pause_last_time > human_pause_cooldown:
            human_pause_cooldown = random.randint(3550, 4000)
            human_pause_last_time = time.time()
            humanpause(random.randint(300, 600))'''
        if firstpass == True:
            move_and_click(bank_booth)
            humanpause(1)

        if needbankpin == False and firstpass is not False: needbankpin = True

        if needbankpin == True:
            pyautogui.press(str(8))
            humanpause(0.3)
            pyautogui.press(str(3))
            humanpause(0.3)
            pyautogui.press(str(1))
            humanpause(0.3)
            pyautogui.press(str(5))
            humanpause(0.3)
            needbankpin = False
            firstpass = 1

        if firstpass == 1:
            move_and_click(bank_tab)
            humanpause(1)
            move_and_click(logs_in_inv)
            humanpause(1)
            firstpass = 2

        move_and_click(logs_in_bank)
        humanpause(1)
        move_and_click(exit_bank)
        humanpause(1)

        if firstpass == 2:
            move_and_click(spellbook)
            humanpause(1)
            firstpass = False

        move_and_click(cast_plankmake)
        humanpause(1)
        move_and_click(logs_in_inv)
        humanpause(90)
        move_and_click(bank_booth)
        humanpause(1)
        move_and_click(logs_in_inv)

except KeyboardInterrupt:
        print("\nStopped by user.")