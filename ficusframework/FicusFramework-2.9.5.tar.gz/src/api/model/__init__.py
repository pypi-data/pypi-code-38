
class ClassInfo(dict):
    @property
    def className(self):
        return self.__getitem__("className")

    @className.setter
    def className(self, value: str):
        self.__setitem__("className", value)

    @property
    def methodName(self):
        return self.__getitem__("methodName")

    @methodName.setter
    def methodName(self, value: str):
        self.__setitem__("methodName", value)

    @property
    def lineNumber(self):
        return self.__getitem__("lineNumber")

    @lineNumber.setter
    def lineNumber(self, value: int):
        self.__setitem__("lineNumber", value)

class LogMessage(dict):

    @property
    def actorName(self):
        return self.__getitem__("actorName")

    @actorName.setter
    def actorName(self, value: str):
        self.__setitem__("actorName", value)

    @property
    def classInfo(self)->ClassInfo:
        return self.__getitem__("classInfo")

    @classInfo.setter
    def classInfo(self, value: ClassInfo):
        self.__setitem__("classInfo", value)

    @property
    def threadName(self):
        return self.__getitem__("threadName")

    @threadName.setter
    def threadName(self, value: str):
        self.__setitem__("threadName", value)

    @property
    def message(self):
        return self.__getitem__("message")

    @message.setter
    def message(self, value: str):
        self.__setitem__("message", value)

    @property
    def traceId(self):
        return self.__getitem__("traceId")

    @traceId.setter
    def traceId(self, value: str):
        self.__setitem__("traceId", value)

    @property
    def exception(self)->Exception:
        return self.__getitem__("exception")

    @exception.setter
    def exception(self, value: Exception):
        self.__setitem__("exception", str(value))