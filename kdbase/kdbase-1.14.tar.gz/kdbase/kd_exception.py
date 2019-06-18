class ReadException(Exception):
    pass

class NoSuchProcess(Exception):
    
    def __init__(self, pid):
        super().__init__()
        self.pid = pid

    def __str__(self):
        return 'No process was found with pid %d' % self.pid


class ConnectException(Exception):

    def __init__(self, name, code):
        super().__init__()
        self.name = name
        self.code = code

    def __str__(self):
        return '%s Connect is fail, return code is %d' % (self.name, self.code)


class ConnectTimeOutException(Exception):

    def __init__(self, name, time):
        super().__init__()
        self.name = name
        self.time = time

    def __str__(self):
        return '%s Connect is fail,timeout is %d' % (self.name, self.time)

class ProcessTimeOutException(Exception):

    def __init__(self, time, pid, hostname):
        super(ProcessTimeOutException, self).__init__()
        self.time = time
        self.pid = pid
        self.host_name = hostname

    def __str__(self):
        return 'Host %s: Process %s: Time out! Limit time is %fs.' % (self.host_name, self.pid, self.time)

class ProcessMemoryOutException(Exception):

    def __init__(self, total_memory, limit_memory, pid, hostname):
        super(ProcessMemoryOutException, self).__init__()
        self.out_of_memory = total_memory - limit_memory
        self.pid = pid
        self.host_name = hostname

    def __str__(self):
        return 'Host %s: Process %s: Memory out! Exceed: %fMB.' % (self.host_name, self.pid, self.out_of_memory)


