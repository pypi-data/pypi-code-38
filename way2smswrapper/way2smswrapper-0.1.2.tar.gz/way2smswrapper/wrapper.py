#!./env/bin/python3

import time, getpass
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from xvfbwrapper import Xvfb


def login() :
    global MobileNo, Pass, SendNo
    print('\n')
    MobileNo = input('Enter Way2Sms-Registered Mobile No. : ')
    Pass = getpass.getpass('Enter Way2Sms Password : ')
    SendNo = input('SMS Need To Be Send To Mobile No. : ')

def sms(Message) :
    do = Xvfb(width=1120, height=550)
    do.start()

    browser = webdriver.Firefox()
    browser.get('http://site21.way2sms.com/content/index.html')

    uelem = browser.find_element_by_id('username')
    uelem.send_keys(MobileNo)
    pelem = browser.find_element_by_id('password')
    pelem.send_keys(Pass)
    pelem.submit()

    while True :
        time.sleep(1)
        try :
            sendl = browser.find_element_by_id('sendSMS')
            break
        except Exception :
            continue
    sendl.click()


    while True :
        time.sleep(1)
        try :
            frame = browser.find_element_by_id('frame')
            break
        except Exception :
            continue

    browser.switch_to_frame(frame)

    ph = browser.find_element_by_id('mobile')
    ph.send_keys(SendNo)

    text = browser.find_element_by_id('message')
    text.send_keys(Message)
    send = browser.find_element_by_id('Send')
    send.click()

    browser.switch_to_default_content()

    while True :
        time.sleep(1)
        try :
            lout = browser.find_element_by_class_name('lout')
            break
        except Exception :
            continue

    lout.click()
    browser.quit()
    do.stop()

					#Created By $implic@
