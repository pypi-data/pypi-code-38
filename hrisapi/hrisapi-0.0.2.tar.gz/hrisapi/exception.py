import abc


class BaseException(Exception):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def message(self):
        pass

    @abc.abstractmethod
    def code(self):
        pass


class ZOHOAPICallFailed(BaseException):
    CODE = 50001

    def __init__(self, zoho_message, zoho_code):
        super().__init__("{} Zoho Error Code: {}".format(zoho_message, zoho_code))

        self._message = zoho_message
        self._code = zoho_code

    def message(self):
        return self._method

    def code(self):
        return self.CODE


class ZOHOAPIAuthFailed(ZOHOAPICallFailed):
    CODE = 50002
