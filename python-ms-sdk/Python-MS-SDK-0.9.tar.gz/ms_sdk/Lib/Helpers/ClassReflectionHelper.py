from ms_sdk.Entities.Product import Product


class ClassReflectionHelper:

    __className = None

    def __init__(self, className):
        self.__className = className

    def getShortName(self):
        return eval('self.__className').getShortName()

    def getShortLowerCaseName(self):
        return str(self.__className).lower()
        # return str(self.getShortName()).lower()