'''Demo Pcall

The purpose of this AEtest script is to demonstrate how to use/leverage pcall
in your testscript/libraries. An equivalent multiprocessing code will also
be provided in order to show comparisons.

To run this script in standalone:

    bash$ python demo_pcall.py

'''
import time
import multiprocessing

from pyats.async_ import pcall
from pyats import aetest

def add(x, y):
    return x + y

def snoop(seconds):
    time.sleep(seconds)


class TestcaseUsingPcall(aetest.Testcase):

    @aetest.test
    def pcall_using_varkwargs(self):
        results = pcall(add, x = (1, 10, 100, 1000),
                             y = (2, 20, 200, 2000))

        print('Results are: %s' % repr(results))

    @aetest.test
    def pcall_using_iargs(self):
        results = pcall(add, iargs = [(1, 2),
                                      (10, 20),
                                      (100, 200),
                                      (1000, 2000)])
        print('Results are: %s' % repr(results))

    @aetest.test
    def pcall_with_timeouts(self):
        pcall(snoop, seconds = (1000000, 100000000), timeout = 2)

class TestcaseUsingMultiprocessing(aetest.Testcase):

    @aetest.test
    def async_using_process(self):
        queue = multiprocessing.SimpleQueue()

        def worker(func, kwargs):
            queue.put(func(**kwargs))

        p1 = multiprocessing.Process(target = worker, 
                                     kwargs = {'func': add,
                                               'kwargs': {'x': 1, 
                                                          'y': 2}})

        p2 = multiprocessing.Process(target = worker, 
                                     kwargs = {'func': add,
                                               'kwargs': {'x': 10, 
                                                          'y': 20}})
        p3 = multiprocessing.Process(target = worker, 
                                     kwargs = {'func': add,
                                               'kwargs': {'x': 100, 
                                                          'y': 200}})
        p4 = multiprocessing.Process(target = worker, 
                                     kwargs = {'func': add,
                                               'kwargs': {'x': 1000, 
                                                          'y': 2000}})

        p1.start()
        p2.start()
        p3.start()
        p4.start()
        p1.join()
        p2.join()
        p3.join()
        p4.join()

        results = []

        while not queue.empty():
            results.append(queue.get())

        print('Results are: %s' % repr(results))

    @aetest.test
    def async_using_pool(self):
        with multiprocessing.Pool(processes = 4) as pool:
            results = pool.starmap(add, zip([1, 10, 100, 1000], 
                                            [2, 20, 200, 2000]))
        
        print('Results are: %s' % repr(results))



# standalone execution
if __name__ == '__main__':
    aetest.main()