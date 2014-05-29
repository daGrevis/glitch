import logging
from selenium import webdriver
from os.path import exists


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)


LINK = "http://127.0.0.1:4000/"
FIRST_FILENAME = "screenshot1.png"
SECOND_FILENAME = "screenshot2.png"


def save_screenshot(link, filename):
    browser = webdriver.Firefox()
    browser.get(link)
    browser.save_screenshot(filename)
    browser.quit()

if not exists(FIRST_FILENAME):
    logger.info("No screenshot was found, creating one.")
    save_screenshot(LINK, FIRST_FILENAME)
else:
    logger.info("Screenshot was found, creating a new one for comparison.")
    save_screenshot(LINK, SECOND_FILENAME)
    with open(FIRST_FILENAME) as screenshot1:
        screenshot1_content = screenshot1.read()
    with open(SECOND_FILENAME) as screenshot2:
        screenshot2_content = screenshot2.read()
    if screenshot1_content == screenshot2_content:
        logger.info("Screenshots are identical!")
    else:
        logger.info("Screenshots differ!")
