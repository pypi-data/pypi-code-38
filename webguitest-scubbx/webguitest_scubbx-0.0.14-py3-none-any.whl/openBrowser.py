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
    from selenium import webdriver
    seleniumAvailable = True
except ImportError:
    pass

if seleniumAvailable:
    def openBrowser(url,x,y,debug=False):
        driver = webdriver.Firefox()
        driver.set_window_size(x, y)
        driver.set_window_position(0, 0)
        driver.get(url)
        return driver
elif pyautoguiAvailable:
    def openBrowser(url,x,y,debug=False):
        if debug: print("pyautogui method to open Browser is yet to be implemented")
        return False
else:
    def openBrowser(url,x,y,debug=False):
        if debug: print("you either need 'selenium' or 'pyautogui' installed to use 'openBrowser'")
        return False
