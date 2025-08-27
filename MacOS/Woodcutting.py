import AppKit
import pyautogui
import random
import cv2
import pytesseract
import time
import easyocr
import re
from PIL import Image

def open_application(app_name):
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    workspace.launchApplication_(app_name)

def find_tree():
    tree_images = ['tree1.png', 'tree2.png', 'tree3.png']
    while True:
        for tree_img in tree_images:
            try:
                x, y = pyautogui.locateCenterOnScreen(tree_img, confidence=0.8)
                pyautogui.click(x, y)
                print(f"Clicked {tree_img} at ({x}, {y})")
                return True  # Exit after first  find
            except pyautogui.ImageNotFoundException:
                continue  # Try next image

        print("No trees found. Retrying...")
        time.sleep(1)

def find_inventory_region():
   try:
       inventory_icon = pyautogui.locateOnScreen('inventory.png', confidence=0.8)
       if inventory_icon:
           left, top, width, height = inventory_icon  # Returns (x, y, w, h)
           print(f"Inventory found at: {left}, {top} (Size: {width}x{height})")
           return (left, top, width, height)
   except:
       pass
   return None

def is_inventory_full():
    return True