import RPi.GPIO as GPIO
from os import popen
from time import sleep
from pibot.lcd import LCD

POWER_OFF_PIN = 21


def background():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(POWER_OFF_PIN, GPIO.IN, GPIO.PUD_UP)

    lcd = LCD(fontsize=20)
    while 1:
        if not GPIO.input(POWER_OFF_PIN):
            time_till_shutoff = 5
            while not GPIO.input(POWER_OFF_PIN):
                message = "   Poweroff in", "   " + str(time_till_shutoff)
                lcd.print(message)
                time_till_shutoff = time_till_shutoff - 1
                sleep(1)
                if time_till_shutoff <= 0:
                    lcd.print("Powering off...")
                    sleep(1)
                    popen("sudo poweroff")
                    break
            lcd.clear()
        sleep(0.5)
