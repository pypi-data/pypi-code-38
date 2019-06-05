from six.moves.queue import Queue

class MockSocket(object): 
    
    def __init__(self, msp, read_queue, write_queue):
        
        self.msp = msp
        self.read_queue = read_queue
        self.write_queue = write_queue
        
    def add_read_error(self, exception):
        def raise_error():
            raise exception
        
        self.read_queue.put(raise_error)
        
    def read(self):
        if self.msp.closed:
            return b""
        
        return self.read_queue.get()()
    
    def sendall(self, buf):
        self.write_queue.put(lambda: buf)
        
    def shutdown(self, ignored):
        pass
    
    def close(self):
        self.msp.closed = True
        self.read_queue.put(lambda: b"")
        self.write_queue.put(lambda: b"")
    
    def settimeout(self, ignored):
        pass
    


class MockSocketPair(object): 
    def __init__(self):
        self.closed = False
        a2b = Queue()
        b2a = Queue()
        self.a = MockSocket(msp=self, read_queue=b2a, write_queue=a2b)
        self.b = MockSocket(msp=self, read_queue=a2b, write_queue=b2a)

