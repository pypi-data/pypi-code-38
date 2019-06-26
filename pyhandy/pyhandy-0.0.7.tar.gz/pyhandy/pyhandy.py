'''
File:          pyhandy.py
File Created:  Wednesday, 19th June 2019 5:49:40 pm
Author:        xss (callmexss@126.com)
Description:   handy python tools to make my life easier
-----
Last Modified: Wednesday, 19th June 2019 6:00:06 pm
Modified By:   xss (callmexss@126.com)
-----
'''
import doctest
import os
import random
import shutil
import time

from functools import wraps
from inspect import signature


def typeassert(*ty_args, **ty_kwargs):
    """Check type of specific arguments."""

    def decorator(func):
        sig = signature(func)
        bind_types = sig.bind_partial(*ty_args, **ty_kwargs).arguments

        def wrapper(*args, **kwargs):
            for name, obj in sig.bind(*args, **kwargs).arguments.items():
                if name in bind_types:
                    if not isinstance(obj, bind_types[name]):
                        raise TypeError(f"{obj} must be {bind_types[name]}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


class RandomHandy:
    """A worker who generate random things."""

    @typeassert(rand=random.Random)
    def __init__(self, rand=None):
        """Construct a RandomHandy
        
        Arguments:
            rand {random.Random} -- an instance of random.Random class
        """
        self.rand = rand if rand else random.Random()

    @typeassert(size=int, scope=tuple, duplicated=bool, etype=str)
    def gen_list(self, size=10, scope=(-100, 100), duplicated=False,
                 etype=int):
        """Generate a random list.
        
        Keyword Arguments:
            size {int} -- the length of the list (default: {10})
            scope {tuple} -- the scope of the elements (default: {(-100, 100)})
            duplicated {bool} -- unique or not (default: {False})
            etype {[type]} -- the type of elements (default: {int})
        
        Returns:
            list -- a random generated list
        """
        start, end = scope
        if size > (end - start) and not duplicated:
            raise ValueError(
                f"The size `{size}` is larger than the given scope `{scope}` "
                "to generate a unique random list.")

        if duplicated:
            ret = [self.rand.randint(start, end) for count in range(size)]
        else:
            ret = self.rand.sample(range(start, end), size)

        if etype is int:
            return ret
        elif etype is float:
            return [self.rand.random() * x for x in ret]

    @typeassert(n=int, range_l=int, range_r=int)
    def generate_random_array(self, n=100, range_l=0, range_r=100):
        """Generate a random integer array
        
        Arguments:
            n {int} -- size of the array
            range_l {int} -- left boundary
            range_r {int} -- right boundary
        
        Returns:
            list -- a list of random integers
        """
        assert range_l < range_r
        return [random.randint(range_l, range_r) for i in range(n)]

    @typeassert(n=int, swap_times=int)
    def generate_nearly_ordered_array(self, n=100, swap_times=10):
        """Generate a nearly ordered array
        
        Arguments:
            n {int} -- size of the array
            swap_times {int} -- swap times
        
        Returns:
            list -- a nearly ordered array
        """
        li = [i for i in range(n)]
        for i in range(swap_times):
            posx = random.randint(0, n - 1)
            posy = random.randint(0, n - 1)
            li[posx], li[posy] = li[posy], li[posx]
        return li


class SortHandy:
    @typeassert(arr=list)
    def is_sorted(self, arr):
        """whether an array is sorted
        
        Arguments:
            arr {list} -- an array
        
        Returns:
            bool -- True if array is sorted else False
        """
        for i in range(len(arr)):
            if arr[i] > arr[i + 1]:
                return False
            return True

    @typeassert(arr=list)
    def testSort(self, sort_func, arr):
        start = time.clock()
        sort_func(arr)
        end = time.clock()
        assert self.is_sorted(arr)

        print(f"{sort_func.__name__} : {(end - start)} s")


class TimeHandy:
    """Time handy."""

    @staticmethod
    @typeassert(float, str)
    def get_format_time(epoch_time, fmt="%Y-%m-%d %H:%M:%S"):
        """Convert Epoch time to string format time
        
        Arguments:
            epoch_time {float} -- epoch time
        
        Keyword Arguments:
            fmt {str} -- string format pattern (default: {"%Y-%m-%d %H:%M:%S"})

            Commonly used format codes:

            %Y  Year with century as a decimal number.
            %m  Month as a decimal number [01,12].
            %d  Day of the month as a decimal number [01,31].
            %H  Hour (24-hour clock) as a decimal number [00,23].
            %M  Minute as a decimal number [00,59].
            %S  Second as a decimal number [00,61].
            %z  Time zone offset from UTC.
            %a  Locale's abbreviated weekday name.
            %A  Locale's full weekday name.
            %b  Locale's abbreviated month name.
            %B  Locale's full month name.
            %c  Locale's appropriate date and time representation.
            %I  Hour (12-hour clock) as a decimal number [01,12].
            %p  Locale's equivalent of either AM or PM.

        Returns:
            str -- string format time
        """
        return time.strftime(fmt, time.localtime(epoch_time))

    @staticmethod
    @typeassert(str, str)
    def get_epoch_time(date_time, pattern="%Y-%m-%d %H:%M:%S"):
        """Get epoch time from string format time
        
        Arguments:
            date_time {str} -- string format time
        
        Keyword Arguments:
            pattern {str} -- string format pattern (default: {"%Y-%m-%d %H:%M:%S"})

            Commonly used format codes:

            %Y  Year with century as a decimal number.
            %m  Month as a decimal number [01,12].
            %d  Day of the month as a decimal number [01,31].
            %H  Hour (24-hour clock) as a decimal number [00,23].
            %M  Minute as a decimal number [00,59].
            %S  Second as a decimal number [00,61].
            %z  Time zone offset from UTC.
            %a  Locale's abbreviated weekday name.
            %A  Locale's full weekday name.
            %b  Locale's abbreviated month name.
            %B  Locale's full month name.
            %c  Locale's appropriate date and time representation.
            %I  Hour (12-hour clock) as a decimal number [01,12].
            %p  Locale's equivalent of either AM or PM.
        
        Returns:
            float -- epoch time
        """
        return time.mktime(time.strptime(date_time, pattern))


class FSHandy:
    """File System handy."""
    pass


if __name__ == '__main__':
    worker = RandomHandy()

    fmttime = TimeHandy.get_format_time(12346)
    print(fmttime)
