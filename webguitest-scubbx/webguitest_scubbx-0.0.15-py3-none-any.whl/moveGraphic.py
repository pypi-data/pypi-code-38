#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
pyautoguiAvailable = False
seleniumAvailable = False

try:
    import pyautogui
    pyautoguiAvailable = True
except ImportError:
    pass

try:
    import selenium
    seleniumAvailable = True
except ImportError:
    pass

if pyautoguiAvailable:
    def moveGraphic(imagepath,dx=500,dy=500,delay=10,confidence=1,waitbetweentries=1,debug=False):
        elemToClick = None
        numTries = 1
        if debug: print("    (0): locating {} ...".format(imagepath))
        while (elemToClick is None) and (numTries < delay):
            try:
                elemToClick = pyautogui.locateOnScreen(imagepath,confidence)
            except Exception as exp:
                if isinstance(exp, pyautogui.pyscreeze.ImageNotFoundException):
                    if debug: print("    ({}): locating {} ...".format(numTries,imagepath))
                else:
                    if debug: print(exp)
                    break
            finally:
                numTries += 1
                time.sleep(waitbetweentries)
        if elemToClick is None:
            if debug: print("    (x): could not locate image {}".format(imagepath))
            return False
        time.sleep(1)
        clickCenter = pyautogui.center(elemToClick)
        pyautogui.moveTo(clickCenter.x, clickCenter.y)
        pyautogui.drag(dx, dy , 1, button='left')
        if debug: print("    (✓): moved {}".format(elemToClick))
        time.sleep(1)
        return True
else:
    def moveGraphic(imagepath,delay=10,confidence=1,waitbetweentries=1,debug=False):
        if debug: print("ERROR: no module 'pyautogui' - 'moveGraphic()' is not available")
        if debug: print("       maybe you missed to also install the 'Xlib' library on which pyautogui depends on")
        return False
