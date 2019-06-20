from zumi.zumi import Zumi
from zumi.util.screen import Screen

import os, re, subprocess, time, signal
from threading import Thread, Timer
from PIL import Image, ImageDraw
import numpy as np
from socket import gethostname
import sys

def __progress(screen, img, start, end):
    while start != end:
        draw = ImageDraw.Draw(img)
        draw.point([(start + 13, 35), (start + 13, 36), (start + 13, 37)])
        screen.draw_image(img.convert('1'))
        start += 1


def __finished_updating(_screen):
    _zumi = Zumi()
    img = _screen.path_to_image('/usr/local/lib/python3.5/dist-packages/zumi/util/images/happy1.ppm')
    time.sleep(.5)
    _screen.draw_text("Firmware updated!", x=10, y=5, image=img.convert('1'), font_size=12, clear=False)

    tempo = 60
    time.sleep(0.5)
    _zumi.play_note(41, tempo)
    _zumi.play_note(43, tempo)
    _zumi.play_note(45, tempo)

def __kill_updater(proc, timeout):
    print("timeout!")
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    timeout["value"] = True

def check_need_to_update(_screen):

    result = os.popen("sudo pip3 search zumidashboard").read()
    version_info = re.findall("INSTALLED[^\n]*", result)[0]

    if '(latest)' in version_info:
        _screen.draw_text_center("Don't need to update")
        time.sleep(1)
        return False
    else:
        current_version = version_info.replace(' ','').split(':')[1]
        print("current version : "+current_version)
        _screen.draw_text_center("Need to update ")
        time.sleep(1)
        return True


def update_version(_screen):
    p = subprocess.Popen('sudo pip3 install zumidashboard --upgrade',
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    img_arr = np.asarray(Image.open('/usr/local/lib/python3.5/dist-packages/zumi/util/images/blankbar.ppm'))
    img = Image.fromarray(img_arr.astype('uint8'))

    _screen.draw_text("Updating Firmware", x=9, y=8, image=img.convert('1'), font_size=12, clear=False)
    img = _screen.screen_image.convert('RGB')

    updater_thread = Thread(target=__progress, args=(_screen,img, 0, 51))
    updater_thread.start()

    try:
        while p.poll() is None:
            line = p.stdout.readline().decode()
            print(line)

            if 'Error' in line:
                _screen.draw_text_center("Error!\nPlease Try Again")
                return

            if 'Collecting' in line:
                updater_thread.join()
                updater_thread = Thread(target=__progress, args=(_screen, img, 51, 88))
                updater_thread.start()

            elif 'Installing collected packages' in line:
                updater_thread.join()
                updater_thread = Thread(target=__progress, args=(_screen, img, 88, 96))
                updater_thread.start()

            elif 'Successfully installed' in line:
                updater_thread.join()
                updater_thread = Thread(target=__progress, args=(_screen, img, 96, 101))
                updater_thread.start()
                version_info = line.split('-')[1]

        print(version_info)
        updater_thread.join()

        time.sleep(1)
        __finished_updating(_screen)
        _screen.draw_text_center("Firmware updated to v" + str(version_info))
    except Exception as e:
        updater_thread.join()
        _screen.draw_text_center("Zumi firmware is already latest")
        print(e)


def update_contents(_screen):
    p = subprocess.Popen('wget -P /home/pi/ –no-check-certificate https://github.com/RobolinkInc/Zumi_Contents/archive/master.tar.gz',
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, preexec_fn=os.setsid)
    time.sleep(1)

    timeout = {"value":False}
    timer = Timer(10, __kill_updater, [p, timeout])
    timer.start()

    img_arr = np.asarray(Image.open('/usr/local/lib/python3.5/dist-packages/zumi/util/images/blankbar.ppm'))
    img = Image.fromarray(img_arr.astype('uint8'))

    _screen.draw_text("Updating Content", x=12, y=8, image=img.convert('1'), font_size=12, clear=False)
    img = _screen.screen_image.convert('RGB')

    error_check = True

    while p.poll() is None:
        error_check = False
        line = p.stdout.readline().decode()
        print(line)

        if "Location: https://codeload.github.com/RobolinkInc/Zumi_Contents/tar.gz/master" in line:
            updater_thread = Thread(target=__progress, args=(_screen, img, 0, 70))
            updater_thread.start()
            timer.cancel()

        elif "Saving to" in line and "master.tar.gz" in line:
            updater_thread.join()
            updater_thread = Thread(target=__progress, args=(_screen, img, 60, 76))
            updater_thread.start()

        elif "ERROR 404" in line or "404 Not Found" in line:
            updater_thread.join()
            _screen.draw_text_center("Error!\nPlease Try Again")
            return

    if timeout["value"] is False:
        if error_check:
            _screen.draw_text_center("Error!\nPlease Try Again")
            return

        updater_thread.join()
        updater_thread = Thread(target=__progress, args=(_screen, img, 76, 101))
        updater_thread.start()

        __post_download_content()

        updater_thread.join()
    else:
        print("timeout error")
        _screen.draw_text_center("Error!\nPlease Try Again")


def __post_download_content():
    subprocess.Popen('sudo rm -r /home/pi/Zumi_Contents/',
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    time.sleep(1)
    subprocess.Popen('tar xvzf /home/pi/master.tar.gz -C /home/pi/',
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    time.sleep(1)
    subprocess.Popen('sudo rm -rf /home/pi/master.tar.* /home/pi/index.*',
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    time.sleep(1)
    subprocess.Popen('sudo mv /home/pi/Zumi_Contents-master /home/pi/Zumi_Contents',
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    time.sleep(1)
    subprocess.Popen('sudo chown -R pi /home/pi/Zumi_Contents',
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)



def restart_threads(_screen):
    Thread(target=restart_app, args=()).start()
    Thread(target=go_to_zumi_dashboard_msg, args=(_screen,)).start()


def restart_app():
    subprocess.run(["sudo python3 /home/pi/Dashboard/dashboard.py"], shell=True)


def go_to_zumi_dashboard_msg(_screen):
    _screen.draw_text_center("Dashboard restarting...")
    for x in range(20):
        time.sleep(1)
    _screen.draw_text_center("Go to \"" + gethostname() + ".local/\" in your browser", font_size=14)


def run():
    screen = Screen(clear=False)
    update_version(screen)
    time.sleep(2)
    update_contents(screen)
    restart_threads(screen)


if __name__ == '__main__':
    run()

