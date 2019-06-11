class ReadException(Exception):
    pass

class NoSuchProcess(Exception):
    
    def __init__(self, pid):
        super().__init__()
        self.pid = pid

    def __str__(self):
        return 'No process was found with pid %d' % self.pid


class ConnectException(Exception):

    def __init__(self, code):
        super().__init__()
        self.code = code

    def __str__(self):
        return 'Connect is fail, return code is %d' % self.code


class TimeoutException(Exception):

    def __init__(self, time):
        super().__init__()
        self.time = time

    def __str__(self):
        return 'Connect time is %d' % self.time

