import datetime

##################################################

def _milliseconds(timedelta):
    return timedelta.total_seconds() * 1000


##################################################

def min_median_max(x):
    "calculate min median max from a list of timedeltas, returns the time in milliseconds"
    mn = 0
    median = 0
    mx = 0
    if x :
        lenx = len(x)
        ordered = sorted(x)
        mn = _milliseconds(ordered[0])
        mx = _milliseconds(ordered[-1])
        if 1 == lenx % 2 :
            # odd number of samples
            median = _milliseconds(ordered[lenx // 2])
        else:
            # even number of samples
            median = 0.5 * _milliseconds(ordered[lenx // 2] + ordered[(lenx // 2) - 1])
    return (mn, median, mx)


##################################################

class Base(object):
    def __init__(self, aggregation_count):
        self.aggregation_count = aggregation_count

    def append_wait(self, delta):
        pass

    def append_exec(self, delta):
        pass

    def append_erro(self, delta):
        pass
