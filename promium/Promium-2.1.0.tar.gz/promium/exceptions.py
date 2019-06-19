

class PromiumException(Exception):
    pass


class PromiumTimeout(PromiumException):
    def __init__(self, message="no error message", seconds=10):
        self.message = f"{message} (waited {seconds} seconds)"
        super(PromiumTimeout, self).__init__(self.message)


class ElementLocationException(PromiumException):
    pass


class LocatorException(PromiumException):
    pass


class BrowserConsoleException(PromiumException):
    pass
