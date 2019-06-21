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
import random
import doctest
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


class RandomWorker:
    """A worker who generate random things."""

    @typeassert(rand=random.Random)
    def __init__(self, rand=None):
        """Construct a RandomWorker
        
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


@typeassert(int, int, int)
def generate_random_array(n=100, range_l=0, range_r=100):
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


@typeassert(int, int)
def generate_nearly_ordered_array(n=100, swap_times=10):
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


@typeassert(list)
def is_sorted(arr):
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


@typeassert(sort_name=str, arr=list)
def testSort(sort_name, sort_func, arr):
    start = time.clock()
    sort_func(arr)
    end = time.clock()
    assert is_sorted(arr)

    print(f"{sort_name} : {(end - start)} s")



if __name__ == '__main__':
    worker = RandomWorker()

    def selection_sort(arr):
        for i in range(len(arr)):
            min_index = i
            for j in range(i + 1, len(arr)):
                if arr[j] < arr[min_index]:
                    min_index = j
            arr[i], arr[min_index] = arr[min_index], arr[i]

    def insertion_sort(arr):
        for i in range(1, len(arr)):
            e = arr[i]
            j = i
            while j > 0 and arr[j - 1] > e:
                arr[j] = arr[j - 1]
                j -= 1
            arr[j] = e


    # li = worker.gen_list(10000, (0, 100000))
    li = generate_nearly_ordered_array(10000, 10)
    li1 = li[:]
    testSort("selection_sort", selection_sort, li)
    testSort("insertion_sort", insertion_sort, li1)