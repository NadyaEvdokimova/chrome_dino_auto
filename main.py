import logging
import os
import time
import pyautogui
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from PIL import ImageGrab
from screeninfo import get_monitors
import numpy as np
import cv2

""" A bot program to automatically play the Chrome Dinosaur game at https://elgoog.im/dinosaur-game/ """
monitors = get_monitors()

screen_index = 1
if screen_index < len(monitors):
    monitor = monitors[screen_index]
    left, top, width, height = monitor.x, monitor.y, monitor.width, monitor.height
else:
    raise IndexError(f"Screen index {screen_index} is out of range.")
screenshot = ImageGrab.grab(bbox=(left, top, left + width, top + height))


def check_for_changes(region_to_check):
    # Take two consecutive screenshots
    screenshot1 = np.array(pyautogui.screenshot(region=region_to_check))
    screenshot2 = np.array(pyautogui.screenshot(region=region_to_check))

    # Convert screenshots to grayscale
    gray1 = cv2.cvtColor(screenshot1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(screenshot2, cv2.COLOR_BGR2GRAY)

    # Calculate absolute difference between the two grayscale images
    diff = cv2.absdiff(gray1, gray2)

    # Threshold the difference image to identify significant changes
    _, thresholded = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # Check if there are any non-zero pixels in the thresholded image
    if cv2.countNonZero(thresholded) > 0:
        return True
    else:
        return False

URL = "https://elgoog.im/dinosaur-game/"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(10)


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%H:%M:%S')

GAME_REGION = ()


def main():
    """Runs the entire program"""
    logging.debug('Program Started. Press Ctrl-C to abort at any time.')
    logging.debug('To interrupt mouse movement, move mouse to upper left corner.')
    get_game_region()
    time.sleep(0.5)
    action_chains = ActionChains(driver)
    action_chains.send_keys(Keys.SPACE).perform()
    logging.debug("space is pressed")

    while True:
        if obstacle_detected():
            jump()


def im_path(filename):
    """A shortcut for joining the 'images/'' file path. Returns the filename with 'images/' prepended."""
    return os.path.join('images', filename)


def get_game_region():
    """Obtains the region that the game is on the screen and assigns it to GAME_REGION."""
    global GAME_REGION

    # identify the top-left corner
    logging.debug('Finding game region...')

    screen_width, screen_height = pyautogui.size()

    logging.debug("Screen width:", screen_width)
    logging.debug("Screen height:", screen_height)

    game_screen_region = (0, 0, screen_width, screen_height)
    region = pyautogui.locateOnScreen(im_path('top_right_corner.PNG'), region=game_screen_region)

    if region is None:
        raise Exception('Could not find game on screen. Is the game visible?')

    # calculate the region of the entire game
    game_width = 1300
    game_height = 650

    top_right_x = region[0] + region[2]
    top_right_y = region[1]

    # Calculate the bottom-left corner of the game window
    bottom_left_x = top_right_x - game_width
    bottom_left_y = top_right_y + game_height

    # Define the GAME_REGION tuple (left, top, width, height)
    GAME_REGION = (bottom_left_x, bottom_left_y, game_width, game_height)

    # Log the calculated GAME_REGION
    logging.debug('Game region found: %s' % (GAME_REGION,))


# Function to jump
def jump():
    """Simulate a spacebar press to make the dinosaur jump"""
    pyautogui.press('space')


# Detect Obstacles
def obstacle_detected():
    """Detects if an obstacle is present on the screen"""
    region_to_check = (355, 555 , 50, 67)
    if check_for_changes(region_to_check):
        logging.debug("obstacle is detected")
        return True
    else:
        return False


if __name__ == '__main__':
    main()
