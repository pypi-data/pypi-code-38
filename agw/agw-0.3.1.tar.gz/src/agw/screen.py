import pyautogui as ag
from pyscreeze import ImageNotFoundException


def locate_image(image, region=None):
    try:
        return ag.locateOnScreen(image, region=region)
    except ImageNotFoundException:
        return None


def image_located(image, region=None, note=None, action=None):

    result = locate_image(image, region=region)

    if result and note:
        print(note)

    if result and action:
        action()

    return result
