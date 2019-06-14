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

class ProcessTimeoutException(Exception):

    def __init__(self, time):
        super(ProcessTimeoutException, self).__init__()
        self.time = time

    def __str__(self):
        return 'Limit time is %d' % self.time

class ProcessMemoryoutException(Exception):

    def __init__(self, memory):
        super(ProcessMemoryoutException, self).__init__()
        self.memory = memory

    def __str__(self):
        return 'Limit memory is %d' % self.memory

