_DEFAULT_POOL = None


def threadpool(f, executor=None):
    global _DEFAULT_POOL
    from functools import wraps
    import concurrent.futures
    if _DEFAULT_POOL is None:
        _DEFAULT_POOL = concurrent.futures.ThreadPoolExecutor()

    @wraps(f)
    def wrap(*args, **kwargs):
        return (executor or _DEFAULT_POOL).submit(f, *args, **kwargs)

    return wrap


def thread_encapsulation(f):
    from threading import Thread
    from functools import wraps
    @wraps(f)
    def decorator(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs)
        t.start()
        return t

    return decorator


class TimerTrigger:
    def __init__(self, action, t:float, start=False, max=0, **kwargs):
        #print('Loadinnnnnnn')
        self.action = action
        self.start = start
        self.run(float(t))
        self.max_i = max
        #print('loadeded')

    def unregister(self):
        self.action = None

    #@threadpool
    @thread_encapsulation
    def run(self, t):
        import time

        i = 0
        print('timer start with', t, 'seconds')
        while self.action and (i < self.max_i or self.max_i == 0):
            if not self.start:
                self.start = True
            else:
                print('triggering action')
                self.action(time=t, trigger_count=i + 1)

            time.sleep(t)
            i += 1
            
        print('timer ended')


triggers = {'timer': TimerTrigger}