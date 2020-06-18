import subprocess
import sys
import threading
import os

import imutils
from time import sleep
import cv2
import numpy as np
import pytesseract

from collections import Counter

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

device_width = 0
device_height = 0

playarea_top = 0
playarea_bottom = 0

Blue_Players_Locations = {}
Green_Players_Locations = {}

turn_click_location = []
Blue_Players_inside = {"0": True, "1": True, "2": True, "3": True}
Green_Players_inside = {"0": True, "1": True, "2": True, "3": True}

stop_thread = False

def get_txt_from_img(string_to_check, times = None):
    subprocess.check_output(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"])  # Capture screen

    subprocess.check_output(["adb", "pull", "/sdcard/screen.png", "screen.png"])  # Save captured screen

    subprocess.check_output(["adb", "shell", "rm", "/sdcard/screen.png"])  # Delete captured screen

    # Resize screen to lower resolution
    file_name = 'screen.png'
    image = cv2.imread(file_name)
    resized = imutils.resize(image, width=300)
    cv2.imwrite("pic.jpg", resized)

    # Load image, convert to HSV format, define lower/upper ranges, and perform
    # color segmentation to create a binary mask
    image = cv2.imread('pic.jpg')
    (height, width, depth) = image.shape

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    if string_to_check == "Play as" or string_to_check == "Continue":
        if times == 1:
            lower = np.array([53, 0, 193])
            upper = np.array([179, 255, 255])
        else:
            lower = np.array([0, 0, 123])
            upper = np.array([179, 72, 255])
    elif string_to_check == "Continued":
        lower = np.array([0, 0, 200])
        upper = np.array([175, 15, 255])
    elif string_to_check == "Computer":
        lower = np.array([0, 0, 200])
        upper = np.array([175, 150, 255])
    elif string_to_check == "Login with Amazon":
        lower = np.array([0, 0, 0])
        upper = np.array([26, 160, 239])
    elif string_to_check == "Sale"  or string_to_check == "Play":
        lower = np.array([75, 0, 255])
        upper = np.array([179, 74, 255])
    elif string_to_check == "Congratulations":
        lower = np.array([15, 116, 162])
        upper = np.array([43, 255, 255])
    elif string_to_check == "won" or string_to_check == "Lost":
        lower = np.array([20, 46, 86])
        upper = np.array([72, 255, 255])
    else:
        lower = np.array([0, 0, 200])
        upper = np.array([175, 176, 255])

    mask = cv2.inRange(hsv, lower, upper)

    # Create horizontal kernel and dilate to connect text characters

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    dilate = cv2.dilate(mask, kernel, iterations=1)

    # Find contours and filter using aspect ratio
    # Remove non-text contours by filling in the contour
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)

        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 1)
        cropped = image[y:y + h, x: x + w]

        data = pytesseract.image_to_string(cropped, lang='eng', config='--psm 7')

        if str(string_to_check) == "Continued":
            string_to_check = "Continue"
        if str(string_to_check) == "Continue":
            string_to_check = "Conti"
        if str(string_to_check).lower() in str(data).lower():
            if string_to_check == "Login with Amazon" or string_to_check == "Sale" or string_to_check == "Congratulations" or string_to_check == "won" or string_to_check == "Lost":
                return True
            else:
                return (x, y, height, width)

def is_installed():
    try:
        installed_status = subprocess.check_output(["adb", "shell", "pm", "path", "com.ludo.king"])
    except:
        installed_status = 1

    if installed_status == 1:
        return False
    else:
        return True

def is_first_launch():
    subprocess.check_output(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"])  # Capture screen

    subprocess.check_output(["adb", "pull", "/sdcard/screen.png", "screen.png"])  # Save captured screen

    subprocess.check_output(["adb", "shell", "rm", "/sdcard/screen.png"])  # Delete captured screen

    # Resize screen to lower resolution
    file_name = 'screen.png'
    image = cv2.imread(file_name)
    resized = imutils.resize(image, width=300)
    cv2.imwrite("pic.jpg", resized)

    image = cv2.imread('pic.jpg')
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 200])
    upper = np.array([175, 150, 255])
    mask = cv2.inRange(hsv, lower, upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    dilate = cv2.dilate(mask, kernel, iterations=1)

    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 1)

        cropped = image[y:y + h, x: x + w]
        data = pytesseract.image_to_string(cropped, lang='eng', config='--psm 7')
        if "computer" in str(data).lower():
            return False

    return True

def get_play_area():
    subprocess.check_output(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"])  # Capture screen

    subprocess.check_output(["adb", "pull", "/sdcard/screen.png", "screen.png"])  # Save captured screen

    subprocess.check_output(["adb", "shell", "rm", "/sdcard/screen.png"])  # Delete captured screen

    # Resize screen to lower resolution
    file_name = 'screen.png'
    image = cv2.imread(file_name)
    resized = imutils.resize(image, width=300)
    cv2.imwrite("pic.jpg", resized)

    image = cv2.imread('pic.jpg')
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 162])
    upper = np.array([179, 67, 255])
    mask = cv2.inRange(hsv, lower, upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    dilate = cv2.dilate(mask, kernel, iterations=1)

    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    check = [False, False]
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if y < 50:
            continue
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 1)

        cropped = image[y:y + h, x: x + w]
        data = pytesseract.image_to_string(cropped, lang='eng', config='--psm 7')

        if "you" in data.lower():
            global playarea_bottom
            playarea_bottom = y + h
            check[0] = True
        if "computer" in data.lower():
            global playarea_top
            playarea_top = y - h
            check[1] = True
        if check[0] and check[1]:
            break

def daily_bonus_presence():

    subprocess.check_output(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"])  # Capture screen

    subprocess.check_output(["adb", "pull", "/sdcard/screen.png", "screen.png"])  # Save captured screen

    subprocess.check_output(["adb", "shell", "rm", "/sdcard/screen.png"])  # Delete captured screen

    # Resize screen to lower resolution
    file_name = 'screen.png'
    image = cv2.imread(file_name)
    resized = imutils.resize(image, width=300)
    cv2.imwrite("pic.jpg", resized)

    image = cv2.imread('pic.jpg')
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array([81, 0, 255])
    upper = np.array([179, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    dilate = cv2.dilate(mask, kernel, iterations=1)

    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 1)

        cropped = image[y:y + h, x: x + w]
        data = pytesseract.image_to_string(cropped, lang='eng', config='--psm 7')
        if "reward" in str(data).lower():
            return True

    return False

def is_first_game_launch():
    subprocess.check_output(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"])  # Capture screen

    subprocess.check_output(["adb", "pull", "/sdcard/screen.png", "screen.png"])  # Save captured screen

    subprocess.check_output(["adb", "shell", "rm", "/sdcard/screen.png"])  # Delete captured screen

    # Resize screen to lower resolution
    file_name = 'screen.png'
    image = cv2.imread(file_name)
    resized = imutils.resize(image, width=300)
    cv2.imwrite("pic.jpg", resized)

    image = cv2.imread('pic.jpg')
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 128])
    upper = np.array([179, 18, 255])
    mask = cv2.inRange(hsv, lower, upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    dilate = cv2.dilate(mask, kernel, iterations=1)

    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 1)

        cropped = image[y:y + h, x: x + w]
        data = pytesseract.image_to_string(cropped, lang='eng', config='--psm 7')
        if "roll" in str(data).lower():
            return True

    return False

def detect_color_from_img():
    subprocess.check_output(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"])  # Capture screen

    subprocess.check_output(["adb", "pull", "/sdcard/screen.png", "screen.png"])  # Save captured screen

    subprocess.check_output(["adb", "shell", "rm", "/sdcard/screen.png"])  # Delete captured screen

    # Resize screen to lower resolution
    file_name = 'screen.png'
    image = cv2.imread(file_name)
    resized = imutils.resize(image, width=300)
    cv2.imwrite("pic.jpg", resized)

    # Load image, convert to HSV format, define lower/upper ranges, and perform
    # color segmentation to create a binary mask
    image = cv2.imread('pic.jpg')
    (height, width, depth) = image.shape

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array([52, 200, 235])
    upper = np.array([100, 250, 255])
    mask = cv2.inRange(hsv, lower, upper)

    # Create horizontal kernel and dilate to connect text characters
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    dilate = cv2.dilate(mask, kernel, iterations=1)

    # Find contours and filter using aspect ratio
    # Remove non-text contours by filling in the contour
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 1)
        if w > 10 and h > 10:
            return (x, y, height, width)

def is_add_shown():
    output = subprocess.check_output(["adb", "shell", "dumpsys", "window", "windows"])
    output = str(output).split("\\n")

    found = False
    for line in output:
        if "mCurrentFocus" in line and "ads" in line:
            found = True
            break

    if found:
        return True
    else:
        return False

def get_players_Locations():
    subprocess.check_output(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"])  # Capture screen

    subprocess.check_output(["adb", "pull", "/sdcard/screen.png", "screen.png"])  # Save captured screen

    subprocess.check_output(["adb", "shell", "rm", "/sdcard/screen.png"])  # Delete captured screen

    # Resize screen to lower resolution
    file_name = 'screen.png'
    image = cv2.imread(file_name)
    resized = imutils.resize(image, width=300)
    cv2.imwrite("pic.jpg", resized)

    global Blue_Players_Locations
    Blue_Players_Locations = {}

    global Green_Players_Locations
    Green_Players_Locations = {}

    x1, y1 = 0, 0
    blue_count = 0
    gree_count = 0

    image = cv2.imread('pic.jpg')
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower = np.array([63, 0, 169])
    upper = np.array([179, 25, 241])
    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(image, image, mask=mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilate = cv2.dilate(mask, kernel, iterations=1)

    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if y > int(playarea_bottom) or y < 120:
            continue
        if h < 15 or w < 14:
            continue
        cropped = image[y:y + h, x: x + w]
        hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)
        lower1 = np.array([57, 183, 0])
        upper1 = np.array([255, 255, 255])
        mask = cv2.inRange(hsv, lower1, upper1)
        output = cv2.bitwise_and(cropped, cropped, mask=mask)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilate = cv2.dilate(mask, kernel, iterations=5)

        cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for contour in cnts:
            # get rectangle bounding contour
            [x1, y1, w1, h1] = cv2.boundingRect(contour)
            cropped = image[int(y):int(y) + int(h), int(x): int(x) + int(w)]
            hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)
            lower1 = np.array([96, 106, 0])
            upper1 = np.array([122, 255, 255])
            mask = cv2.inRange(hsv, lower1, upper1)
            output = cv2.bitwise_and(cropped, cropped, mask=mask)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            dilate = cv2.dilate(mask, kernel, iterations=5)

            cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            x = x + (w/2)
            y = y + (h/2)

            if 260 < y < 296 and 122 < x < 177:
                continue

            if len(cnts) == 1:
                Blue_Players_Locations[str(blue_count)] = [x,y]
                blue_count += 1
            elif len(cnts) == 0:
                Green_Players_Locations[str(gree_count)] = [x,y]
                gree_count += 1

            if w > 30:
                x,y = x1, y1

    if x1 != 0 and y1 != 0:
        if len(Blue_Players_Locations) < 4:
            Blue_Players_Locations[str(blue_count)] = [x1,y1]
            blue_count += 1
        elif len(Green_Players_Locations) < 4:
            Green_Players_Locations[str(blue_count)] = [x1,y1]
            gree_count += 1

def get_dice_number():
    number = 0

    subprocess.check_output(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"])  # Capture screen

    subprocess.check_output(["adb", "pull", "/sdcard/screen.png", "screen.png"])  # Save captured screen

    subprocess.check_output(["adb", "shell", "rm", "/sdcard/screen.png"])  # Delete captured screen

    # Resize screen to lower resolution
    file_name = 'screen.png'
    image = cv2.imread(file_name)
    resized = imutils.resize(image, width=300)
    cv2.imwrite("pic.jpg", resized)

    image = cv2.imread('pic.jpg')
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower = np.array([56, 33, 255])
    upper = np.array([101, 120, 255])
    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(image, image, mask=mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    dilate = cv2.dilate(mask, kernel, iterations=1)

    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if y < 475:
            continue
        if h < 5:
            continue
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 2)
        number += 1

    return number

def is_my_turn():

    subprocess.check_output(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"])  # Capture screen

    subprocess.check_output(["adb", "pull", "/sdcard/screen.png", "screen.png"])  # Save captured screen

    subprocess.check_output(["adb", "shell", "rm", "/sdcard/screen.png"])  # Delete captured screen

    # Resize screen to lower resolution
    file_name = 'screen.png'
    image = cv2.imread(file_name)
    resized = imutils.resize(image, width=300)
    cv2.imwrite("pic.jpg", resized)

    image = cv2.imread('pic.jpg')
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)

    lower = np.array([0, 111, 148])
    upper = np.array([54, 146, 241])
    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(image, image, mask=mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    dilate = cv2.dilate(mask, kernel, iterations=1)

    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if y < int(playarea_bottom) or y > 490:
            continue
        if w < 10:
            continue
        if h < 15:
            continue
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 2)
        cropped = image[y - 10:y + h, x: x + w]
        return True

    return False

def am_i_playing():
    subprocess.check_output(["adb", "shell", "screencap", "-p", "/sdcard/screen1.png"])  # Capture screen

    subprocess.check_output(["adb", "pull", "/sdcard/screen1.png", "screen1.png"])  # Save captured screen

    subprocess.check_output(["adb", "shell", "rm", "/sdcard/screen1.png"])  # Delete captured screen

    # Resize screen to lower resolution
    file_name = 'screen1.png'
    image = cv2.imread(file_name)
    resized = imutils.resize(image, width=300)
    cv2.imwrite("pic1.jpg", resized)

    image1 = cv2.imread('pic1.jpg')

    sleep(15)

    subprocess.check_output(["adb", "shell", "screencap", "-p", "/sdcard/screen1.png"])  # Capture screen

    subprocess.check_output(["adb", "pull", "/sdcard/screen1.png", "screen1.png"])  # Save captured screen

    subprocess.check_output(["adb", "shell", "rm", "/sdcard/screen1.png"])  # Delete captured screen

    # Resize screen to lower resolution
    file_name = 'screen1.png'
    image = cv2.imread(file_name)
    resized = imutils.resize(image, width=300)
    cv2.imwrite("pic2.jpg", resized)

    image2 = cv2.imread('pic2.jpg')

    if image1.shape == image2.shape:
        difference = cv2.subtract(image1, image2)
        b, g, r = cv2.split(difference)

        if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
            play_random()
            sys.exit(1)

    if not stop_thread:
        am_i_playing()

def play_random():

    subprocess.check_output(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"])  # Capture screen

    subprocess.check_output(["adb", "pull", "/sdcard/screen.png", "screen.png"])  # Save captured screen

    subprocess.check_output(["adb", "shell", "rm", "/sdcard/screen.png"])  # Delete captured screen

    # Resize screen to lower resolution
    file_name = 'screen.png'
    image = cv2.imread(file_name)
    resized = imutils.resize(image, width=300)
    cv2.imwrite("pic.jpg", resized)

    image = cv2.imread('pic.jpg')
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower = np.array([57, 183, 215])
    upper = np.array([175, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(image, image, mask=mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilate = cv2.dilate(mask, kernel, iterations=1)

    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    times = 0
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if y > int(playarea_bottom) or h < 10 or w > 10 or y < 100:
            continue
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 2)
        click(x,y)
        times += 1

    if times == 0:

        lower = np.array([57, 183, 255])
        upper = np.array([175, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        output = cv2.bitwise_and(image, image, mask=mask)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 8))
        dilate = cv2.dilate(mask, kernel, iterations=1)

        cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            if y > int(playarea_bottom) or h < 10 or w > 10 or y < 100:
                continue
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 2)
            click(x,y)

def click(x, y):

    multiplier = device_height/533

    x = str(int(x) * multiplier)
    y = str(int(y) * multiplier)
    subprocess.check_output(["adb", "shell", "input", "tap", x, y])

def remove_temp_files():

    if os.path.exists("pic.jpg"):
        os.remove("pic.jpg")

    if os.path.exists("pic1.jpg"):
        os.remove("pic1.jpg")

    if os.path.exists("pic2.jpg"):
        os.remove("pic2.jpg")

    if os.path.exists("screen.png"):
        os.remove("screen.png")

    if os.path.exists("screen1.png"):
        os.remove("screen1.png")

def main():

    # Checking device presence
    adb_output = subprocess.check_output(["adb", "devices"])
    output = str(adb_output).split('\\n')
    if ("List of devices attached" in output[0]) and ("device" or "emulator" in output[1]):
        print("Device detected")
    else:
        print("No device detected")
        sys.exit(1)

    # Get Device Resolution
    adb_output = subprocess.check_output(["adb", "shell", "wm", "size"])
    output = str(adb_output).split(':')
    output = str(output[1]).strip()
    output = str(output).split('x')
    global device_width
    device_width = int(output[0])
    global device_height
    device_height = output[1]
    device_height = int(device_height.split('\\')[0])

    if not is_installed():
        # Installing Ludo King
        print("Ludo King is not installed. Installing...")

        adb_output = subprocess.check_output(["adb", "install-multiple", "base.apk", "split_config.arm64_v8a.apk"])
        sleep(15)
        if "Success" in str(adb_output):
            print("Ludo King is installed successfully.")
        else:
            sys.exit(1)
    else:
        print("Ludo King is already installed.")

    # Killing Ludo King
    subprocess.check_output(
        ["adb", "shell", "am", "force-stop", "com.ludo.king"])

    print("Launching Ludo King")

    # Launching Ludo King
    subprocess.check_output(
        ["adb", "shell", "monkey", "-p", "com.ludo.king", "-c", "android.intent.category.LAUNCHER", "1"])

    sleep(20)

    if daily_bonus_presence():
        subprocess.check_output(["adb", "shell", "input", "keyevent", "4"])
        sleep(2)

    if is_first_launch():

        first_launch_app = True

        # Tap on Continue
        try:
            x, y, h, w = get_txt_from_img('Continue')
        except:
            x, y, h, w = get_txt_from_img('Continue', 1)
        x = (x * device_width) / w
        y = (y * device_height) / h
        subprocess.check_output(["adb", "shell", "input", "tap", str(x), str(y)])
        sleep(2)

        if is_first_launch():

            print("Ludo King is launched for first time. Setting default profile.")

            # Tap on Play As Guest
            try:
                x, y, h, w = get_txt_from_img('Play as')
            except:
                x, y, h, w = get_txt_from_img('Play as', 1)
            x = (x * device_width) / w
            y = (y * device_height) / h
            subprocess.check_output(["adb", "shell", "input", "tap", str(x), str(y)])
            sleep(2)

            # Tap on Continue again
            x, y, h, w = get_txt_from_img('Continued')
            x = (x * device_width) / w
            y = (y * device_height) / h
            subprocess.check_output(["adb", "shell", "input", "tap", str(x), str(y)])
            sleep(10)

    # Tap on back for amazon ad
    if get_txt_from_img('Login with Amazon'):
        subprocess.check_output(["adb", "shell", "input", "keyevent", "4"])
        sleep(2)

    if get_txt_from_img("Sale"):
        subprocess.check_output(["adb", "shell", "input", "keyevent", "4"])
        sleep(2)

    if daily_bonus_presence():
        subprocess.check_output(["adb", "shell", "input", "keyevent", "4"])
        sleep(2)

    print("Starting 1 vs 1 with computer")

    # Tap on Computer
    x, y, h, w = get_txt_from_img('Computer')
    x = (x * device_width) / w
    y = (y * device_height) / h
    subprocess.check_output(["adb", "shell", "input", "tap", str(x), str(y)])
    sleep(2)

    # Tap on Next
    x, y, h, w = get_txt_from_img('Next')
    x = (x * device_width) / w
    y = (y * device_height) / h
    subprocess.check_output(["adb", "shell", "input", "tap", str(x), str(y)])
    sleep(2)

    # Tap on Play
    x, y, h, w = get_txt_from_img('Play')
    x = (x * device_width) / w
    y = (y * device_height) / h
    subprocess.check_output(["adb", "shell", "input", "tap", str(x), str(y)])
    sleep(10)

    # Check if ad is shown
    while is_add_shown():
        subprocess.check_output(["adb", "shell", "input", "keyevent", "4"])
        sleep(5)

    sleep(2)
    x, y, h, w = detect_color_from_img()
    x = (x * device_width) / w
    y = (y * device_height) / h

    turn_click_location.append(str(x))
    turn_click_location.append(str(y))

    if is_first_game_launch:
        # Blue turn click
        x, y, h, w = detect_color_from_img()
        x = (x * device_width) / w
        y = (y * device_height) / h
        subprocess.check_output(["adb", "shell", "input", "tap", turn_click_location[0], turn_click_location[1]])
        sleep(12)

    ###########
    # Play Game
    ###########

    checking_thread = threading.Thread(target=am_i_playing)
    checking_thread.start()

    print("Getting possible locations.")
    print("Started playing game.")

    while 1:

        clicked = False
        game_over = False

        get_play_area()

        # Check if ad is shown
        while is_add_shown():
            sleep(2)
            game_over = True
            subprocess.check_output(["adb", "shell", "input", "keyevent", "4"])
            sleep(3)

        # Check if gameplay is completed
        if game_over:
            print("Completed playing game")
            global stop_thread
            stop_thread = True

            # Check if we lost
            if get_txt_from_img("Lost"):
                print("We Lost ...")
                remove_temp_files()
                sys.exit(0)

            # Check if we won
            if get_txt_from_img("won"):
                subprocess.check_output(["adb", "shell", "input", "keyevent", "4"])
                sleep(2)
            if get_txt_from_img("Congratulations"):
                print("We WON !!!!")
                remove_temp_files()
                sys.exit(0)

        subprocess.check_output(["adb", "shell", "input", "tap", turn_click_location[0], turn_click_location[1]])

        sleep(1)
        times = 0
        if get_dice_number() != 6:
            while not is_my_turn() and times > 5:
                sleep(1)
                times += 1

        get_players_Locations()

        for player, value in Blue_Players_Locations.items():
            if 102 >= value[0] >= 10 and int(playarea_top) <= value[1] <= int(playarea_bottom):
                Blue_Players_inside[player] = True
            else:
                Blue_Players_inside[player] = False

        for player, value in Green_Players_Locations.items():
            if 195 <= value[0] <= 284 and 220 >= value[1] >= 133:
                Green_Players_inside[player] = True
            else:
                Green_Players_inside[str(player)] = False

        if len(Blue_Players_Locations) < 1:
            play_random()
            continue

        if get_dice_number() == 6:
            x = Counter(Blue_Players_inside.values())
            if x[True] == 0:
                for blue_player, Bvalue in Blue_Players_Locations.items():
                    for green_player, Gvalue in Green_Players_Locations.items():
                        if Blue_Players_inside[blue_player] == False:
                            if ((Bvalue[0] - Gvalue[0] < 100) and (Bvalue[1] - Gvalue[1] < 10)):
                                player_x = Bvalue[0]
                                green_x = Gvalue[0]
                                if player_x > green_x:
                                    for Lblue_player, LBvalue in Blue_Players_Locations.items():
                                        if Blue_Players_inside[Lblue_player] == False:
                                            if Lblue_player != blue_player:
                                                click(Blue_Players_Locations[Lblue_player][0], Blue_Players_Locations[Lblue_player][1])
                                                clicked = True
                                                break
                                else:
                                    click(player_x, Bvalue[1])
                                    clicked = True
                                    break
                            elif ((Bvalue[1] - Gvalue[1] < 100) and (Bvalue[0] - Gvalue[0] < 10)):
                                player_y = Bvalue[1]
                                green_y = Gvalue[1]
                                if player_y > 265:
                                    if player_y > green_y:
                                        for Lblue_player, LBvalue in Blue_Players_Locations.items():
                                            if Blue_Players_inside[Lblue_player] == False:
                                                if Lblue_player != blue_player:
                                                    click(Blue_Players_Locations[Lblue_player][0], Blue_Players_Locations[Lblue_player][1])
                                                    clicked = True
                                                    break
                                    else:
                                        click(Bvalue[0], player_y)
                                        clicked = True
                                        break
                                else:
                                    click(Bvalue[0], player_y)
                                    clicked = True
                                    break
                for blue_player, Bvalue in Blue_Players_Locations.items():
                    if Blue_Players_inside[blue_player] == False:
                        click(Bvalue[0], Bvalue[1])
                        clicked = True
                        break

            else:
                for blue_player, Bvalue in Blue_Players_Locations.items():
                    for green_player, Gvalue in Green_Players_Locations.items():
                        if Blue_Players_inside[blue_player] == False:
                            if ((Bvalue[0] - Gvalue[0] < 100) and (Bvalue[1] - Gvalue[1] < 10)):
                                player_x = Bvalue[0]
                                green_x = Gvalue[0]
                                if player_x > green_x:
                                    for Lblue_player, LBvalue in Blue_Players_Locations.items():
                                        if Blue_Players_inside[Lblue_player] == False:
                                            if Lblue_player != blue_player:
                                                click(Blue_Players_Locations[Lblue_player][0],
                                                      Blue_Players_Locations[Lblue_player][1])
                                                clicked = True
                                                break
                                else:
                                    click(player_x, Bvalue[1])
                                    clicked = True
                                    break
                            elif ((Bvalue[1] - Gvalue[1] < 100) and (Bvalue[0] - Gvalue[0] < 10)):
                                player_y = Bvalue[1]
                                green_y = Gvalue[1]
                                if player_y > 265:
                                    if player_y > green_y:
                                        for Lblue_player, LBvalue in Blue_Players_Locations.items():
                                            if Blue_Players_inside[Lblue_player] == False:
                                                if Lblue_player != blue_player:
                                                    click(Blue_Players_Locations[Lblue_player][0], Blue_Players_Locations[Lblue_player][1])
                                                    clicked = True
                                                    break
                                    else:
                                        click(Bvalue[0], player_y)
                                        clicked = True
                                        break
                                else:
                                    click(Bvalue[0], player_y)
                                    clicked = True
                                    break
                for blue_player, Bvalue in Blue_Players_Locations.items():
                    if Blue_Players_inside[blue_player] == True:
                        click(Bvalue[0], Bvalue[1])
                        clicked = True

        else:

            for blue_player, Bvalue in Blue_Players_Locations.items():
                for green_player, Gvalue in Green_Players_Locations.items():
                    if Blue_Players_inside[blue_player] == False:
                        if ((Bvalue[0] - Gvalue[0] < 100) and (Bvalue[1] - Gvalue[1] < 10)):
                            player_x = Bvalue[0]
                            green_x = Gvalue[0]
                            if player_x > green_x:
                                click(player_x, Bvalue[1])
                                clicked = True
                            else:
                                for Lblue_player, LBvalue in Blue_Players_Locations.items():
                                    if Blue_Players_inside[Lblue_player] == False:
                                        if Lblue_player != blue_player:
                                            click(Blue_Players_Locations[Lblue_player][0],
                                                  Blue_Players_Locations[Lblue_player][1])
                                            clicked = True
                                            break
                        elif ((Bvalue[1] - Gvalue[1] < 100) and (Bvalue[0] - Gvalue[0] < 10)):
                            player_y = Bvalue[1]
                            green_y = Gvalue[1]
                            if player_y > 265:
                                if player_y > green_y:
                                    click(Bvalue[0], player_y)
                                    clicked = True
                                else:
                                    for Lblue_player, LBvalue in Blue_Players_Locations.items():
                                        if Blue_Players_inside[Lblue_player] == False:
                                            if Lblue_player != blue_player:
                                                click(Blue_Players_Locations[Lblue_player][0], Blue_Players_Locations[Lblue_player][1])
                                                clicked = True
                                                break
                            else:
                                if player_y < green_y:
                                    click(Bvalue[0], player_y)
                                    clicked = True
                                else:
                                    for Lblue_player, LBvalue in Blue_Players_Locations.items():
                                        if Blue_Players_inside[Lblue_player] == False:
                                            if Lblue_player != blue_player:
                                                click(Blue_Players_Locations[Lblue_player][0], Blue_Players_Locations[Lblue_player][1])
                                                clicked = True
                                                break
                    break

            for player, value in Blue_Players_Locations.items():
                if len(Blue_Players_inside) == 4 and len(Blue_Players_Locations) == 4:
                    if Blue_Players_inside[player] == False:
                        click(value[0], value[1])
                        clicked = True
                else:
                    play_random()
                    clicked = True

        if not clicked:
            play_random()

if __name__ == "__main__":
    main()