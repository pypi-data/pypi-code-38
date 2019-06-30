import RPi.GPIO as GPIO
from pibot import constants as c

from time import sleep


def init_buttons():
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(c.BUTTON_LEFT_PIN, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(c.BUTTON_MID_PIN, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(c.BUTTON_RIGHT_PIN, GPIO.IN, GPIO.PUD_UP)


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
    if button == c.BUTTON_LEFT:
        pin = c.BUTTON_LEFT_PIN
    elif button == c.BUTTON_MID:
        pin = c.BUTTON_MID_PIN
    elif button == c.BUTTON_RIGHT:
        pin = c.BUTTON_RIGHT_PIN
    else:
        pin = button

    if pin is not None:
        if GPIO.input(pin):
            return True
    return False
