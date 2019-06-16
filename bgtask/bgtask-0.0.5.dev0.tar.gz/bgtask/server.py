# coding=utf8
import multiprocessing
import logging
import time
import signal
import sys
from errorbuster import formatError
from bgtask import Configuration, RedisConnection, TaskTransfer, TaskHolder


def signal_handler(_, __):
    sys.exit(0)


def worker_proccess(pid, host, port, queue_name):
    signal.signal(signal.SIGTERM, signal_handler)
    logging.info('worker:%s started', pid)
    try:
        RedisConnection.instance().init_redis(host, port, queue_name)
        while True:
            q_n, data = RedisConnection.instance().waitfor()
            if q_n != queue_name:
                continue
            try:
                tasktransfer = TaskTransfer.restore(data)
                currentTask = TaskHolder.instance().getTask(tasktransfer.func_name)
                if not currentTask:
                    logging.error('No suck task: %s' % tasktransfer.func_name)
                    continue
                start_ts = time.time() * 1000
                return_data = ''
                try:
                    return_data = currentTask.run(tasktransfer)
                except RuntimeError:
                    logging.error('proc_%s Execute Task %s timeout-more than %s\'s' % (pid,
                                                                                       currentTask.name,
                                                                                       currentTask.timeout))
                    continue
                except Exception as ex:
                    logging.error(formatError(ex))
                    continue
                finally:
                    end_ts = time.time() * 1000
                logging.info('proc_%s execute Task %s finished in %d\'ms with return data: %s' % (pid,
                                                                                                 currentTask.name,
                                                                                                 int(end_ts-start_ts),
                                                                                                 return_data))
            except Exception as e:
                logging.error(formatError(e))

    except Exception as e:
        logging.error(formatError(e))


class Server(object):
    def __init__(self):
        self.configuration = Configuration.instance()

    def start(self, logging_level=logging.INFO):
        logging.basicConfig(
            level=logging_level,
            format='%(asctime)s-%(filename)s[line:%(lineno)d]-%(levelname)s: %(message)s'
        )
        procs = []
        try:

            for pid in range(self.configuration.worker_count):
                proc = multiprocessing.Process(target=worker_proccess, args=(
                    pid,
                    self.configuration.host,
                    self.configuration.port,
                    self.configuration.queue_name, ))
                proc.start()
                procs.append(proc)

            def on_term(_, __):
                for proc in procs:
                    proc.terminate()
            signal.signal(signal.SIGTERM, on_term)

            for proc in procs:
                proc.join()

        except KeyboardInterrupt:
            for proc in procs:
                proc.join()

        except Exception as e:
            for proc in procs:
                proc.join()
            logging.error(formatError(e))


