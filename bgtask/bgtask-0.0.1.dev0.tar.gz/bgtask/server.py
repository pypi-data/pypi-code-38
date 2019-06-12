# coding=utf8
import multiprocessing
import traceback
import logging
import time
from bgtask import Configuration, RedisConnection, TaskTransfer, TaskHolder


def worker_proccess(queue, _number):
    try:
        while True:
            data = queue.get()
            tasktransfer = TaskTransfer.restore(data)
            currentTask = TaskHolder.instance().getTask(tasktransfer.func_name)
            if not currentTask:
                logging.error('No suck task: %s' % tasktransfer.func_name)
                continue
            start_ts = time.time() * 1000
            try:
                return_data = currentTask.run(tasktransfer)
            except RuntimeError:
                logging.error('proc_%s Execute Task %s timeout-more than %s\'s' % (_number,
                                                                                   currentTask.name,
                                                                                   currentTask.timeout))
                continue
            except Exception:
                traceback.print_exc()
                continue
            finally:
                end_ts = time.time() * 1000
            logging.info('proc_%s execute Task %s finished in %s\'s with return data: %s' % (_number,
                                                                                             currentTask.name,
                                                                                             end_ts-start_ts,
                                                                                             return_data))
    except KeyboardInterrupt:
        pass


class Server(object):
    def __init__(self):
        self.configuration = Configuration.instance()

    def start(self):
        try:
            queue = multiprocessing.Manager().Queue()
            pool = multiprocessing.Pool(processes=self.configuration.worker_count)
            for i in range(self.configuration.worker_count):
                pool.apply_async(worker_proccess, args=(queue, i))
            pool.close()
            while True:
                qn, data = RedisConnection.instance().waitfor()
                if qn == self.configuration.queue_name:
                    queue.put(data)
        except KeyboardInterrupt:
            pass

