import logging
from os.path import exists

import requests
from selenium import webdriver
from PIL import Image, ImageChops


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)


LINK = "http://127.0.0.1:4000/"
FILENAME_FOR_SCREENSHOT_BEFORE = "screenshot_before.png"
FILENAME_FOR_SCREENSHOT_AFTER = "screenshot_after.png"
FILENAME_FOR_SCREENSHOT_DIFFERENCE = "screenshot_difference.png"


def save_screenshot(link, filename):
    browser = webdriver.Firefox()
    browser.get(link)
    browser.save_screenshot(filename)
    browser.quit()


try:
    requests.get(LINK)
except requests.exceptions.ConnectionError:
    logger.error("Could not open the link! Is the server down?")

    exit()

if not exists(FILENAME_FOR_SCREENSHOT_BEFORE):
    logger.info("No screenshot was found, creating one.")

    save_screenshot(LINK, FILENAME_FOR_SCREENSHOT_BEFORE)
else:
    logger.info("Screenshot was found, creating a new one for comparison.")

    save_screenshot(LINK, FILENAME_FOR_SCREENSHOT_AFTER)
    screenshot_before = Image.open(FILENAME_FOR_SCREENSHOT_BEFORE)
    screenshot_after = Image.open(FILENAME_FOR_SCREENSHOT_AFTER)

    if screenshot_before.tostring() == screenshot_after.tostring():
        logger.info("Screenshots are identical!")
    else:
        difference = ImageChops.difference(screenshot_before, screenshot_after)
        difference = ImageChops.invert(difference)
        difference.save(FILENAME_FOR_SCREENSHOT_DIFFERENCE)

        message = ("Screenshots differ, see `{}`."
                   .format(FILENAME_FOR_SCREENSHOT_DIFFERENCE))
        logger.info(message)
