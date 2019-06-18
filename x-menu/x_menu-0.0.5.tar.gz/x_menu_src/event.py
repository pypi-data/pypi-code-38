from functools import wraps
from concurrent.futures import ThreadPoolExecutor
import curses

class EventMix:
    
    instances = {}
    instances_opts = {}

    _background = ThreadPoolExecutor(16)
    _counter = {}
    
    def action_listener(self, ch, *args, callback = None, **kargs):
        fn = EventMix.instances.get(ch, '')
        if fn:
            if hasattr(self, fn):
                f = getattr(self, fn)
            else:
                return
        else:
            return

        f_opts = EventMix.instances_opts.get(f, {'background':False})
        if f:
            if f_opts['background']:
                res = EventMix._background.submit(f, *args, **kargs)
                if callback:
                    res.add_done_callback(lambda x: callback(x.result()))
            else:
                res = f(*args, **kargs)
                if callback:
                    callback(res)

    @classmethod
    def register(cls, ch, func, background=False, **kargs):
        kargs.update({"background":background})
        if isinstance(ch, str):
            ch = ord(ch)
        
        cls.instances[ch] = func.__name__
        cls.instances_opts[func] = kargs
        cls._counter[ch] = 0

    @classmethod
    def if_run(cls, ch):
        return cls._counter.get(ch, 0)

    def ready_key(self, ch):
        if isinstance(ch, int):
            EventMix._counter[ch]= 0
        else:
            EventMix._counter[ord(ch)]= 0
    
    @classmethod
    def run_background(cls, func, *args,callback=None, **kargs):
        res = cls._background.submit(func, *args, **kargs)
        if callback:
            res.add_done_callback(lambda x: callback(*x.result()))
            

 
def listener(ch,use=1,background=False):
    if isinstance(ch,str):
        ch = ord(ch)
    def _run(funcs):
        EventMix.register(ch, funcs, background=background)
        @wraps(funcs)
        def __run(self,*args, **kargs):
            if EventMix.if_run(ch) < use:
                # if isinstance(ch, str):
                    # ch = ord(ch)
                
                n = EventMix._counter.get(ch, 0) + 1
                EventMix._counter[ch] = n
                # import pdb;pdb.set_trace()
                return funcs(self,*args, **kargs)
        return __run
    return _run
