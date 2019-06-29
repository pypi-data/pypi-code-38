import time

from DynamicWebParse import Base as Base


class RequestXPath():
    def getElems(self, XPath, driver, breakTime=None):
        return Base.getWithFunction(driver.find_elements_by_xpath, XPath, breakTime)

    def getElem(self, XPath, driver, breakTime=None):
        return Base.getWithFunction(driver.find_element_by_xpath, XPath, breakTime)

    def clickElem(self, XPath, driver, breakTime=None):
        startTime = time.time()
        while True:
            elem = self.getElem(XPath, driver, breakTime)
            if Base.makeFunctions([elem.click], breakTime):
                break
            else:
                if breakTime is not None and time.time() - startTime > breakTime:
                    print("Cannot make click elem")
                    return False
        return True

    def clickElems(self, XPath, driver, breakTime=None):
        startTime = time.time()
        while True:
            elems = self.getElems(XPath, driver, breakTime)
            if len(elems) > 0:
                if Base.makeFunctions([elem.click for elem in elems], breakTime):
                    break
                else:
                    if breakTime is not None and time.time() - startTime > breakTime:
                        print("Cannot make click elem")
                        return False
            else:
                if breakTime is not None and time.time() - startTime > breakTime:
                    print("Cannot get elem")
                    return False
        return True

    def notNecessarlyClick(self, XPath, driver, breakTime=None):
        elems = self.getElems(XPath, driver, breakTime)
        if len(elems) > 0:
            if Base.makeFunctions([elem.click for elem in elems], breakTime):
                return True
            else:
                print("not all click elem")
                return False