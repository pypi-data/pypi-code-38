import time
import traceback

from selenium.webdriver.common.keys import Keys

from parse.RequestXPath import RequestXPath


class Requests():
    def __init__(self, driver):
        self.__requestsFactory = RequestXPath()
        self.__driver = driver

    def setFactoryXPath(self):
        self.__requestsFactory = RequestXPath()

    def getElem(self, getData, breakTime=None):
        return self.__requestsFactory.getElem(getData, self.__driver, breakTime)

    def getElems(self, getData, breakTime=None):
        return self.__requestsFactory.getElems(getData, self.__driver, breakTime)

    def clickElem(self, getData, breakTime=None):
        return self.__requestsFactory.clickElem(getData, self.__driver, breakTime)

    def clickElems(self, getData, breakTime=None):
        return self.__requestsFactory.clickElems(getData, self.__driver, breakTime)

    def notNecessaryClick(self, getData, breakTime=None):
        return self.__requestsFactory.notNecessarlyClick(getData, self.__driver, breakTime)

    def allwaysLoadPage(self, url, timeWait=60):
        while True:
            try:
                self.__driver.set_page_load_timeout(timeWait)

                self.__driver.get(url)
                break
            except:
                print('TIMEOUT:\n', traceback.format_exc())
                time.sleep(1)


def clickGetElemCtrl(driver, get):
    startTime = time.time()
    while True:
        try:
            elem = driver.find_element_by_xpath(get)
            elem.send_keys(Keys.COMMAND + 't')
            elem.send_keys(Keys.ENTER)
            break
        except:
            if time.time() - startTime > 5:
                print('Ошибка:\n', traceback.format_exc())
                print('stop')
                return False
            continue
    return True
