#encoding:utf-8
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.remote_connection import RemoteConnection
import functools
import logging
from selenium.webdriver.support.wait import WebDriverWait

class BaseCrawl(object):

    __host = "127.0.0.1"
    __browser = None

    def __init__(self, hubip = "127.0.0.1:4444"):
        logging.debug("server ip : " + hubip)
        self.__host = hubip
        self.makeDriver()

    # create browser
    def makeDriver(self):
        hostname = "http://" + self.__host + "/wd/hub"
        self.__browser = webdriver.Remote(command_executor=hostname, desired_capabilities=DesiredCapabilities.CHROME)

    # get browser
    def getBrowser(self):
        return self.__browser

    # get content of the request url
    def getContent(self, url):
        self.getBrowser().get(url)
        self.waitLast()

    def waitLast(self, t=30):
        self.getBrowser().implicitly_wait(t)

    # close the browser by key
    def closeWin(self):
        self.__browser.close()

    # find single element
    def findElement(self, fType, value):
        oriFunc = lambda a, b: self.__browser.find_element(a, b)

        execFunc = functools.partial(oriFunc, fType, value)

        return self.funcExecute(execFunc)

    # find multi elements
    def findElements(self, fType, value):
        oriFunc = lambda a, b: self.__browser.find_elements(a, b)

        execFunc = functools.partial(oriFunc, fType, value)

        return self.funcExecute(execFunc)

    # safe execute method
    def funcExecute(self, func):
        try:
            return func()
        except Exception as e:
            return None
            
    # get all tabs
    def getTabs(self):
        return self.__browser.window_handles

    # jump to the next tab
    def toNextTab(self):
        handlers = self.getTabs()
        current_handlers = self.__browser.current_window_handle
        for h in range(len(handlers)):
            if handlers[h] == current_handlers:
                if (h + 1) < len(handlers):
                    self.__browser.switch_to_window(handlers[h+1])

    def clickElement(self, element, type=0, timeout=30, interval=1, waitObject=None):
        '''
            在页面上面点击

            分为两种类型，0点击后在当前页面等待，1点击后要跳转到新页面等待

        '''


        if element is None:
            return

        element.click()

        if type == 1:
            self.toNextTab()
            
        if waitObject is not None:
            WebDriverWait(self.getBrowser(), timeout, interval).until(waitObject)
        else:
            self.waitLast(timeout) 

    def toFirstTab(self):
        self.getBrowser().switch_to_window(self.getTabs()[0])


    def __del__(self):
        self.__browser.quit()