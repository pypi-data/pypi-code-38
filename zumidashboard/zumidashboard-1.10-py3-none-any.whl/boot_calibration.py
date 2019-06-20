'''
#Testing calibration code
import smbus #for I2C communication
#import RPi.GPIO as GPIO #for the Pin Input reading
from PIL import Image
'''
from threading import Thread
import time
from zumi.zumi import Zumi
from zumi.util.screen import Screen
from zumi.personality import Personality
import zumidashboard.scripts as scripts
import os
import subprocess

def _start_threading(*args):
    for thread in args:
        thread.start()
    time.sleep(1)
    for thread in args:
        thread.join()


def _average(lst):
    sum_value = 0
    for data in lst:
        sum_value += data
    avg = sum_value / len(lst)
    return avg


class Post:
    def __init__(self, zumi, screen, personality):
        self.zumi = zumi  # you must first create the Zumi object
        self.screen = screen  # second goes the eyes "OLED Screen"
        self.personality = personality

    # countdown
    def calibrate_countdown(self):
        for i in range(5, -1, -1):
            self.screen.draw_text_center("Place me on\na flat surface\n%i" % i)
            # self.screen.draw_text("Place me ona flat surface          %i" % i, x=18, y=14, font_size=16)
            time.sleep(.7)

    def countdown_sound(self):
        tempo = 50
        time.sleep(0.2)
        for i in range(6):
            self.zumi.play_note(50, tempo)
            time.sleep(1)

    def countdown_sequence(self):
        screen_thread = Thread(target=self.calibrate_countdown)
        sound_thread = Thread(target=self.countdown_sound)
        _start_threading(sound_thread, screen_thread)

    # calibration

    def cal(self):
        screen_thread = Thread(target=self.screen.calibrating)
        sound_thread = Thread(target=self.personality.sound.calibrating)
        _start_threading(screen_thread, sound_thread)

    def calibration_sequence(self):
        self.countdown_sequence()

        self.cal()

        acc_x = []
        acc_y = []
        acc_z = []

        # Check data
        for i in range(0, 20):
            acc_x.append(self.zumi.mpu.read_MPU_data(0))
            acc_y.append(self.zumi.mpu.read_MPU_data(1))
            acc_z.append(self.zumi.mpu.read_MPU_data(2))
            time.sleep(0.05)
        print(_average(acc_x))
        print(_average(acc_y))
        print(_average(acc_z))
        if _average(acc_x) < .07 and _average(acc_y) < .07 and _average(acc_z) < 1.3:
            return True
        else:
            return False

    # ---------------WAKE UP SEQUENCE -----------------
    def wake_up_sequence(self):
        # Calibrate
        while not self.calibration_sequence():
            self.calibration_fail_sequence()
        self.calibration_success_sequence()

        self.personality.look_around()

    def calibration_fail_sequence(self):
        self.personality.sound.uh_oh2()
        self.screen.draw_text_center("Oops!\nTrying again")
        time.sleep(3)

    def calibration_success_sequence(self):
        screen_thread = Thread(target=self.screen.calibrated)
        sound_thread = Thread(target=self.personality.sound.calibrated)
        _start_threading(sound_thread, screen_thread)


def run():
    zumi = Zumi()
    screen = Screen()
    personality = Personality(zumi, screen)
    if os.path.isfile('/home/pi/recalibrate'):
        subprocess.Popen(['sudo', 'rm', 'rf', '/home/pi/recalibrate'])
        obj = Post(zumi, screen, personality)
        obj.wake_up_sequence()

    else:
        personality.look_around()
    time.sleep(1)
    personality.start()
    while not scripts.is_device_connected():
        time.sleep(.2)
    personality.found_me()


if __name__ == '__main__':
    run()
