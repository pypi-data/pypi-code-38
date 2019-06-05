from six.moves import queue
import time
import threading

class BurstyQueue(object):
    """Thread-safe queue that throttles low-priority items"""
    
    def __init__(self, period):
        self.get_lock = threading.Lock()
        self.counter_lock = threading.Lock()
        self.counter = 0
        self.period = period
        self.last_get_time = 0
        self.waiting_queue = queue.Queue()
        self.main_queue = queue.PriorityQueue()
        
    def _next_c(self):
        with self.counter_lock:
            self.counter += 1
            return self.counter
        
    def put(self, item, low_priority=True):
        self.main_queue.put((low_priority, self._next_c(), item))
        
    def _get_high_priority_if_available(self, timeout):
        timeout_time = time.time() + timeout
        end_of_period = self.last_get_time + self.period
        finish_t = min(timeout_time, end_of_period)
        while True:
            now = time.time()
            delta = finish_t - now if finish_t > now else 0
            try: 
                low_priority, _c, item = self.main_queue.get(block=delta>0, timeout=delta)
                if low_priority:
                    self.waiting_queue.put(item)
                else:
                    return item
            except queue.Empty:
                if delta == 0:
                    raise
        
    def get_ignore_throttling(self, timeout=0):
        with self.get_lock:
            if not self.waiting_queue.empty():
                return self.waiting_queue.get()
            
            return self.main_queue.get(block=timeout>0, timeout=timeout)[2]
            
    def get(self, timeout=0, ignore_throttling=False):
        
        if ignore_throttling:
            return self.get_ignore_throttling(timeout)
        
        with self.get_lock:
            start = time.time()
            
            try: 
                rv = self._get_high_priority_if_available(timeout)
                self.last_get_time = time.time()
                return rv
            except queue.Empty:
                pass # no high priority elem available
            
            if not self.waiting_queue.empty(): # earlier element available
                self.last_get_time = time.time()
                return self.waiting_queue.get() # consume low priority elem
            
            elapsed = time.time() - start
            if elapsed >= timeout:
                raise queue.Empty
            
            delta = timeout - elapsed
            _low_priority, _t, rv = self.main_queue.get(block=delta>0, timeout=delta) # Fetch event from main queue
            self.last_get_time = time.time()
            return rv    
    
        