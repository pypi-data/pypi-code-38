# coding=utf8
import pollworker
import logging
import time
from errorbuster import formatError
from bgtask import Configuration, RedisConnection, TaskTransfer, TaskHolder


def worker_proccess(pid, message):
    tasktransfer = TaskTransfer.restore(message)
    currentTask = TaskHolder.instance().getTask(tasktransfer.func_name)
    if not currentTask:
        logging.error('No suck task: %s' % tasktransfer.func_name)
        return
    start_ts = time.time() * 1000
    return_data = ''
    try:
        return_data = currentTask.run(tasktransfer)
    except RuntimeError:
        logging.error('proc_%s Execute Task %s timeout-more than %s\'s' % (pid,
                                                                           currentTask.name,
                                                                          currentTask.timeout))
        return
    except Exception as ex:
        logging.error(formatError(ex))
        return
    finally:
        end_ts = time.time() * 1000
    logging.info('proc_%s execute Task %s finished in %d\'ms with return data: %s' % (pid,
                                                                                     currentTask.name,
                                                                                     int(end_ts-start_ts),
                                                                                     return_data))


class RedisPoller(object):
    def __init__(self):
        self.redis = RedisConnection.instance()
        self.configure = Configuration.instance()
        self.redis.init_redis(self.configure.host, self.configure.port, self.configure.queue_name)

    def poll(self):
        return self.redis.waitfor()


class Server(object):
    def __init__(self):
        pollworker.regist_poller(RedisPoller())
        pollworker.regist_worker(worker_proccess)

    def start(self, logging_level=logging.INFO):
        logging.basicConfig(
            level=logging_level,
            format='%(asctime)s-%(filename)s[line:%(lineno)d]-%(levelname)s: %(message)s'
        )
        configue = Configuration.instance()
        pollworker.start(configue.worker_count)