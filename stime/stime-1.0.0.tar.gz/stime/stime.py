# coding=utf-8

_current_time = 0.0 # interpreted as a number of seconds since the epoch.

def time():
    """Return the time in seconds since the epoch as a floating point number."""
    return _current_time

def monotonic():
    """Return the time in seconds since the epoch as a floating point number."""
    return time() # since time is arbitrary, there should be no difference

def tick(time_increment=1.0):
    """Increments the current time by 1.0 seconds or the value provided as argument."""
    global _current_time
    _current_time += time_increment

def reset(now=0.0):
    """Reset the current time to 0.0 or the value provided as argument."""
    global _current_time
    _current_time = now
