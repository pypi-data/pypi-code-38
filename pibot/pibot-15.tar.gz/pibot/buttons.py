import RPi.GPIO as GPIO
import constants as c

from time import sleep


def init_buttons():
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(c.BUTTON_LEFT, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(c.BUTTON_MID, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(c.BUTTON_RIGHT, GPIO.IN, GPIO.PUD_UP)


def wait_for_button_press(button):
    while not is_pressed(button):
        sleep(0.001)


def wait_for_button_release(button):
    while is_pressed(button):
        sleep(0.001)


def wait_for_button(button):
    wait_for_button_press(button)
    wait_for_button_release(button)


def is_pressed(button):
    _ = False
    if button == c.BUTTON_LEFT:
        _ = c.BUTTON_LEFT
    elif button == c.BUTTON_MID:
        _ = c.BUTTON_MID
    elif button == c.BUTTON_RIGHT:
        _ = c.BUTTON_RIGHT

    if not _:
        if GPIO.input(_):
            return True
    return False
