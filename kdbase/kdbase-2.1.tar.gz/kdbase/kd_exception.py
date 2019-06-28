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

    def __init__(self, time, pid, hostname, how_long_no_output):
        super(ProcessTimeOutException, self).__init__()
        self.time = time
        self.pid = pid
        self.host_name = hostname
        self.no_output = how_long_no_output

    def __str__(self):
        return 'Host %s: Process %s: Time out! Limit time is %fs. But the program has no output for %fs' % (self.host_name, self.pid, self.time, self.no_output)

class ProcessMemoryOutException(Exception):

    def __init__(self, total_memory, limit_memory, pid, hostname):
        super(ProcessMemoryOutException, self).__init__()
        self.out_of_memory = total_memory - limit_memory
        self.pid = pid
        self.host_name = hostname
        self.limit_memory = limit_memory
        self.total_memory = total_memory

    def __str__(self):
        return 'Host %s: Process %s: Memory out! Limit memory size is %fMB. But the memory size of our program is up to %fsMB. Exceed memory size is %fMB.' % (self.host_name, self.pid, self.limit_memory, self.total_memory, self.out_of_memory)
