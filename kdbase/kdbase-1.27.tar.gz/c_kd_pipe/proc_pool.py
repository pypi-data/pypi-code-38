import multiprocessing
import time
import os

def func(who='1'):
    print "user:", who
    time.sleep(1)
    print "end"
    return "done " + who

class WorkerPool(object):
    def __init__(self, worker_num):
        self.__pool = multiprocessing.Pool(processes=worker_num)
        self.__results = []

    def push(self, func, args):
        self.__results.append(self.__pool.apply_async(func, args))
        

    def wait_until_finish(self):
        self.__pool.close()
        self.__pool.join()
        
    def get_results(self):
        return self.__results

def main():
    pool = WorkerPool(4)
    for i in xrange(10):
        who = "user %d" % (i)
        pool.push(func, (who, ))
        print 'pid:%d' % os.getpid()
    time.sleep(10)
    pool.wait_until_finish()
    print pool.get_results()
    for res in pool.get_results():
        print ":::", res.get()
    print "all process(es) done."

if __name__ == "__main__":
    main()

