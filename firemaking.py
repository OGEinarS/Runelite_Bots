import pyautogui
import keyboard
import time
import random

# Configuration
tinderbox_pos = (x1, y1)  # Replace with your tinderbox's inventory position (pixels)
logs_pos = (x2, y2)  # Replace with your logs' inventory position (pixels)
delay_between_actions = 0.5  # Adjust if needed


def click(pos):
    x, y = pos
    pyautogui.moveTo(x, y, duration=random.uniform(0.1, 0.3))
    pyautogui.click()


def firemake():
    print("Starting firemaking bot... (Press 'Q' to stop)")
    while not keyboard.is_pressed('q'):
        # Select tinderbox
        click(tinderbox_pos)
        time.sleep(delay_between_actions)

        # Click logs
        click(logs_pos)
        time.sleep(delay_between_actions + random.uniform(0.1, 0.5))  # Small random delay

    print("Bot stopped.")


if __name__ == "__main__":
    print("Move your mouse over the tinderbox in inventory, then press 'T' to set position.")
    keyboard.wait('t')
    tinderbox_pos = pyautogui.position()
    print(f"Tinderbox position set: {tinderbox_pos}")

    print("Move your mouse over the logs in inventory, then press 'L' to set position.")
    keyboard.wait('l')
    logs_pos = pyautogui.position()
    print(f"Logs position set: {logs_pos}")

    print("Press 'F' to start firemaking. Press 'Q' to stop.")
    keyboard.wait('f')
    firemake()