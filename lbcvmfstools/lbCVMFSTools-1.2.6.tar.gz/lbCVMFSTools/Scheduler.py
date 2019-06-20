from lbCVMFSTools.Injector import inject, injector
from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface
from lbCVMFSTools.TransactionHandlerInterface import \
    TransactionHandlerInterface
from contextlib import contextmanager
import logging
from lbCVMFSTools import Audit
import time
from multiprocessing import Process, Queue
import errno
import sys
from signal import signal, SIGCHLD, SIG_DFL


@inject(taskHandler=TaskHandlerInterface,
        transactionHandler=TransactionHandlerInterface)
class Scheduler():
    def __init__(self, taskHandler=None, transactionHandler=None):
        self.taskHandler = taskHandler
        self.transactionHandler = transactionHandler
        self.stop_timeout = False
        if hasattr(self.taskHandler, 'no_auto_start'):
            if self.taskHandler.no_auto_start:
                return
        self.start()

    def _execute(self, task, queue):
        try:
            self.taskHandler.perform_task(task)
        except Exception as e:
            queue.put(e)

    def start(self):
        if not self.taskHandler.should_run():
            return
        tasks = self.taskHandler.get_list_of_tasks()
        self.taskHandler.preTransaction()
        all_ok = True
        for task in tasks:
            current_task_id = self.taskHandler.__class__.__name__
            Audit.write(Audit.COMMAND_START, command=current_task_id)
            t_name = str(task)
            if isinstance(task, dict):
                t_name = task.get('task_name', str(task))
            logging.info("Starting executing: %s" % t_name)
            error = self.execute(task=task)
            if error:
                all_ok = False
                logging.info("Fail executing: %s" % t_name)
                logging.error(error)
            else:
                logging.info("Successfully executed: %s" % t_name)
            Audit.write(Audit.COMMAND_END)
        if all_ok:
            self.taskHandler.update_last_run()
        self.taskHandler.postTransaction(success=all_ok)
        if not all_ok:
            raise Exception("Failed executing")

    def handle_signal(self, _, __):
        raise Warning("Process has finished")

    def execute(self, task):
        try:
            with self.transaction():
                if self.taskHandler.timeout:
                    error_queue = Queue()
                    executor = Process(target=self._execute,
                                       args=(task, error_queue))
                    executor.start()
                    signal(SIGCHLD, self.handle_signal)
                    try:
                        time.sleep(self.taskHandler.timeout)
                    except Warning as e:
                        logging.info("Process finished before timeout")
                    # Unmap signal for the case when the timeout is reached
                    signal(SIGCHLD, SIG_DFL)
                    proc_done = not executor.is_alive()
                    if not proc_done:
                        logging.error("Terminating process due to timeout")
                        executor.terminate()
                        raise OSError(errno.ETIMEDOUT)
                    if not error_queue.empty():
                        raise error_queue.get()
                else:
                    self.taskHandler.perform_task(task)
            return None
        except UserWarning as e:
            return None
        except Exception as e:
            return e

    @contextmanager
    def transaction(self):
        logging.info("Starting transaction")
        self.transactionHandler.transactionStart()
        try:
            yield
            logging.info("Sending transaction")
            Audit.write(Audit.TRANSACTION_START)
            self.transactionHandler.transactionPublish()
            Audit.write(Audit.TRANSACTION_END)
        except Exception as e:
            logging.info("Aborting transaction")
            logging.error(e)
            self.transactionHandler.transactionAbort()
            raise e
