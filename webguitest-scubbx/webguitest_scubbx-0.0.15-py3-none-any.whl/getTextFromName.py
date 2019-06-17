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

if seleniumAvailable:
    def getTextFromName(driver,elementName,delay=10,debug=False):
        numTries = 1
        elemToExtract = None
        if debug: print("    (0): locating {} ...".format(elementName))
        while (elemToExtract is None) and (numTries < delay):
            try:
                elemToExtract = driver.find_element_by_name(elementName)
            except Exception as exp:
                if isinstance(exp, selenium.common.exceptions.NoSuchElementException):
                    if debug: print("    ({}) locating {} ...".format(numTries,elementName))
                elif isinstance(exp, selenium.common.exceptions.ElementNotInteractableException):
                    if debug: print("    ({}) locating {} ...".format(numTries,elementName))
                else:
                    if debug: print(exp)
                    break
            finally:
                numTries += 1
                time.sleep(1)
        if elemToExtract is None:
            if debug: print("    (x): could not locate name={}".format(elementName))
            return False
        return elemToExtract.text

else:
    def getTextFromName(driver,elementName,delay=10,debug=False):
        if debug: print("ERROR: no module 'selenium' - 'getValueFromName()' is not available")
        return False
