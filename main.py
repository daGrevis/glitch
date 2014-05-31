import logging
import json
import os
from os import path

import requests
from selenium import webdriver
from PIL import Image, ImageChops

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

FILENAME_FOR_CONFIGURATION = "Glitchfile"
PATH_TO_SCREENSHOTS_DIRECTORY = "screenshots/"
FILENAME_FOR_SCREENSHOT_BEFORE = "screenshot_before.png"
FILENAME_FOR_SCREENSHOT_AFTER = "screenshot_after.png"
FILENAME_FOR_SCREENSHOT_DIFFERENCE = "screenshot_difference.png"


def save_screenshot(link, filename):
    browser = webdriver.Firefox()
    browser.get(link)
    browser.save_screenshot(filename)
    browser.quit()

try:
    with open(FILENAME_FOR_CONFIGURATION) as configuration:
        configuration_content = configuration.read()
except IOError:
    message = ("Could not open `{}`. Is it there?"
               .format(FILENAME_FOR_CONFIGURATION))
    logger.error(message)
    exit()

try:
    configuration = json.loads(configuration_content)
except ValueError:
    message = ("Could not parse `{}`. Is it valid JSON?"
               .format(FILENAME_FOR_CONFIGURATION))
    logger.error(message)
    exit()

try:
    os.mkdir(PATH_TO_SCREENSHOTS_DIRECTORY)
except OSError:
    pass

for link in configuration["links"]:
    try:
        response = requests.get(link)
    except requests.exceptions.ConnectionError:
        logger.error("Could not open `{}`. Is the server down?".format(link))
        exit()

    if response.status_code != 200:
        message = ("Could not read `{}`. Is is there?"
                   .format(link))
        logger.error(message)
        exit()

    path_to_screenshots_directory = path.join(PATH_TO_SCREENSHOTS_DIRECTORY,
                                              link.replace("/", "-"))

    try:
        os.mkdir(path_to_screenshots_directory)
    except OSError:
        pass

    path_to_screenshot_before = path.join(path_to_screenshots_directory,
                                          FILENAME_FOR_SCREENSHOT_BEFORE)

    if not path.exists(path_to_screenshot_before):
        save_screenshot(link, path_to_screenshot_before)

        logger.info("No screenshot was found, creating one.")
    else:
        logger.info("Screenshot was found, creating a new one for comparison.")

        path_to_screenshot_after = path.join(path_to_screenshots_directory,
                                             FILENAME_FOR_SCREENSHOT_AFTER)
        save_screenshot(link, path_to_screenshot_after)

        screenshot_before = Image.open(path_to_screenshot_before)
        screenshot_after = Image.open(path_to_screenshot_after)

        if screenshot_before.tostring() == screenshot_after.tostring():
            logger.info("Screenshots are identical!")
        else:
            if screenshot_before.size != screenshot_after.size:
                logger.info("Sizes of screenshots are not the same.")
                exit()

            path_to_screenshot_difference = path.join(
                path_to_screenshots_directory,
                FILENAME_FOR_SCREENSHOT_DIFFERENCE)

            difference = ImageChops.difference(screenshot_before,
                                               screenshot_after)
            difference = ImageChops.invert(difference)
            difference.save(path_to_screenshot_difference)

            message = ("Screenshots differ, see `{}`."
                       .format(path_to_screenshot_difference))
            logger.info(message)
            exit()
