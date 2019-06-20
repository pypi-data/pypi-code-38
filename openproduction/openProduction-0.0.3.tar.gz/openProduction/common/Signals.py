from concurrent.futures import ThreadPoolExecutor

class Signal:
    
    def __init__(self, asynchron=False):
        self._connectors = []
        self._pool = ThreadPoolExecutor(5)
        self._async = asynchron
    
    def connect(self, cb):
        self._connectors.append(cb)
        
    def disconnect(self, cb=None):
        if cb == None:
            self._connectors = []
        else:
            try:
                self._connectors.remove(cb)
            except:
                pass
        
    def emit(self, *args,**kwargs):
        for c in self._connectors:
            if hasattr(c, "emit"):
                if self._async:
                    self._pool.submit(c.emit, *args, **kwargs)
                else:
                    c.emit(*args, **kwargs)
            else:
                if self._async:
                    self._pool.submit(c, *args, **kwargs)
                else:
                    c(*args, **kwargs)
            
            
if __name__ == "__main__":
    
    def _onConnect(*args, **kwagrs):
        print ("test connect " + args[0])
    def _onConnect2(*args, **kwagrs):
        print ("test connect2 " + args[0])
    def _onConnectSignal2(*args, **kwagrs):
        print ("test chained signal " + args[0])
        
    s2 = Signal()
    s2.connect(_onConnectSignal2)
    s = Signal()
    s.connect(_onConnect)
    s.connect(_onConnect2)
    s.connect(s2)
    s.emit("arg11")