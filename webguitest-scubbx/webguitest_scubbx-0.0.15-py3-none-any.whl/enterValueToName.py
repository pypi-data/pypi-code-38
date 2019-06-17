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
    from selenium.webdriver.common.keys import Keys
    seleniumAvailable = True
except ImportError:
    pass


if seleniumAvailable:
    def enterValueToName(driver,elementName,textcontent,pressEnter=False,delay=10,debug=False):
        numTries = 1
        elemToEnter = None
        if debug: print("    (0): locating {} ...".format(elementName))
        while (elemToEnter is None) and (numTries < delay):
            try:
                elemToEnter = driver.find_element_by_name(elementName)
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
        if elemToEnter is None:
            if debug: print("    (x): could not locate name={}".format(elementName))
            return False
        elemToEnter.clear()
        elemToEnter.send_keys(textcontent)
        if pressEnter:
            elemToEnter.send_keys(Keys.RETURN)
        if debug: print("    (✓): entered {} into {}".format(textcontent, elementName))
        return True

else:
    def enterValueToName(driver,elementName,textcontent,pressEnter=False,delay=10,debug=False):
        if debug: print("ERROR: no module 'selenium' - 'enterValueToName()' is not available")
        return False
