# references :
# https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes
# https://mattgathu.github.io/multiprocessing-logging-in-python/

import logging
import sys
from logging import FileHandler
import multiprocessing
import threading
import traceback
import os


class MultiprocessingLogHandler(logging.Handler):
    """
        Multiprocessing Log Handler

        This handler makes it possible for several processes
        to log to the same file by using a queue.
    """
    # _sentinel is object denotes that now end of thread(queue listener).
    # If self.queue.get() == None, Then it means while loop will break and results into termination of thread.
    _sentinel = None

    def __init__(self, log_file):
        """
        :param log_file: **Full or relative path with log file name.
        """
        log_folder = os.path.dirname(log_file)
        print("Logging folder : " + str(log_folder))
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        logging.Handler.__init__(self)
        self._handler = FileHandler(log_file, mode='a')
        # Log format
        self.format_str = "%(asctime)s | %(levelname)-9s | %(codetype)s | %(logcode)s | %(message)s"
        self.formatter_obj = logging.Formatter(self.format_str)
        # set Formatter to Handlers. There are two Handler.
        # This Handler is main inherited Handler.
        logging.Handler.setFormatter(self, self.formatter_obj)
        # This Handler is FileHandler which writes logRecords to file.
        self._handler.setFormatter(self.formatter_obj)
        # Queue initialization.
        self.queue = multiprocessing.Queue(-1)
        # Thread queue_listener_thread creation and run.
        self.queue_listener_thread = threading.Thread(target=self.queue_listener, daemon=True)
        self.queue_listener_thread.start()

    def queue_listener(self):
        """
            This function executed by queue_listener_thread.
            It will wait for entry in queue.
            Listen to queue for record.
            Then sends logRecord to Handler(i.e. File Handler)
        """
        while True:
            try:
                # print("waiting to get record from queue.")
                record = self.queue.get()
                if record == self._sentinel:
                    # print("_sentinel Found ..Breaking")
                    break
                # print(record)
                self._handler.emit(record)
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                # print("EOF Error  ... breaking.. queue listener")
                self.queue.put_nowait(self._sentinel)
                break
            except:
                traceback.print_exc(file=sys.stderr)

    def send_to_queue(self, record):
        """
        Add logRecord to queue.
        :param record: logRecord Object
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            self.queue.put_nowait(record)
            return True
        except Exception as e:
            print(traceback.format_exc())
            return False

    def emit(self, record):
        """
        Override logging.Handler's emit() function.
        This function does formatting of logRecord.
        And Adds logRecord to queue.
        :param record: logRecord Object
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            self.format(record)
            self.send_to_queue(record)
            return True
        except (KeyboardInterrupt, SystemExit):
            print(traceback.format_exc())
            raise
        except:
            self.handleError(record)
            return False

    def close(self):
        """
        Override logging.Handler's close() function.
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            # print("In MultiprocessingHandler close()")
            self.queue.put_nowait(self._sentinel)
            # Check if any log remaining in queue
            self.queue_listener()
            self._handler.close()
            logging.Handler.close(self)
            return True
        except Exception as e:
            print(traceback.format_exc())
            return False
