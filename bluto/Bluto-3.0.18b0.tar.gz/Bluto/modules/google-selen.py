from selenium import webdriver
from pyvirtualdisplay import Display
import os
import time

NEXT_BUTTON_XPATH = '//input[@type="submit" and @value="Google Search"]'
display = Display(visible=0, size=(800, 600))
display.start()
executable = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../doc/driver/chromedriver'))
browser = webdriver.Chrome(executable_path=executable)
browser.get('https://www.google.co.uk')
time.sleep(3)
test = browser.find_element_by_name('q')
test.send_keys('@"saga.co.uk"')
time.sleep(3)
button = test.find_element_by_xpath(NEXT_BUTTON_XPATH)
button.click()
print('stop')