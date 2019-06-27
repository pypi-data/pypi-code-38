import timeit

def snooze(value):
    '''
    time.sleep() substitute
    Keep busy for some time (very roughly and depending on machine, `value` is in ms)

    :param value: Time
    :type value: Number
    '''
    for i in range(int(0.65e3 * value)):
        _ = 2 ** (i / value)

class Timer:
    def __init__(self,name = None):
        self.name = name
    def __enter__(self,*args):
        self.start_time = timeit.default_timer()
    def __exit__(self,*args):
        elapsed = timeit.default_timer()-self.start_time
        print('Elapsed time '+('({})'.format(self.name) if self.name else '')+': {:.3f}s'.format(elapsed))

