from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class DynamicWebParse():
    def __init__(self, pathDriver):
        self.__path = pathDriver
        self.__driver = None

    def getDriver(self):
        return self.__driver

    def makeUnvisibleDriver(self):
        self.makeDisplay()
        self.__driver = self.initDriver(self.makeLessOption())
        return self.__driver

    def makeVisibleDriver(self):
        self.__driver = self.initDriver()
        return self.__driver

    def makeDisplay(self, visible=0, size=(1920, 1080)):
        return Display(visible=visible, size=size).start()

    def makeLessOption(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        return chrome_options

    def initDriver(self, options=None):
        return webdriver.Chrome(self.__path, chrome_options=options) if options is not None else webdriver.Chrome(self.__path)

    def __del__(self):
        try:
            self.__driver.close()
        except:
            print("dont have driver")

