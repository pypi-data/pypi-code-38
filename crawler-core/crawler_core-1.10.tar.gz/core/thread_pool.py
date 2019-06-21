# coding:utf-8
from queue import Queue
from threading import Thread

# from database import Database
#
# def db_engine(dbname='imenik'):
#     db = Database
#     db.db_type = 'Oracle'
#     db.server = dbname
#     db = db()
#     return db


class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """
    def __init__(self, tasks, thread_number):
        Thread.__init__(self)
        self.thread_number = thread_number
        self.tasks = tasks
        self.daemon = True
        self.start()


    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            kargs.update({'Thread': self.thread_number})
            try:
                func(*args, **kargs)
            except Exception as e:
                # An exception happened in this thread
                print({'ErrorLog': str(e), 'Args': args})
            finally:
                # Mark this task as done, whether an exception happened or not
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        self.tasks.qsize()
        for _ in range(num_threads):
            Worker(self.tasks,_)

    def add_task(self, func, *args, **kwargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kwargs))

    def map(self, func, args_list, **kwargs):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args, **kwargs)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()


