import os
from typing import List, Tuple
from multiprocessing import Process, Pool, Queue
import signal
from signal import SIGTERM, SIGINT, SIGUSR1, signal as handle_signal

from macrobase_driver import MacrobaseDriver

from structlog import get_logger

log = get_logger('macrobase_pool')


class DriversProccesesPool:

    def __init__(self):
        self._root_pid = os.getpid()
        self._processes: Tuple[MacrobaseDriver, Process] = []

    def _serve(self, driver: MacrobaseDriver, queue: Queue):
        try:
            driver.run()
            queue.put(os.getpid())
        except Exception as e:
            log.error(e)
            raise

    def _get_process(self, driver: MacrobaseDriver) -> Tuple[MacrobaseDriver, Process]:
        def sig_handle(signal, frame):
            pid = os.getpid()

            if pid == self._root_pid:
                log.debug(f'Macrobase Pool completed with {pid} pid')
            else:
                log.debug(f'Driver completed with {pid} pid')
                os.kill(pid, SIGUSR1)

        handle_signal(SIGTERM, lambda s, f: sig_handle(s, f))
        handle_signal(SIGINT, lambda s, f: sig_handle(s, f))

        process = Process(
            name=driver.__class__.__name__,
            target=self._serve,
            kwargs={
                'driver': driver,
                'queue': self.queue,
            },
        )

        return (driver, process)

    def start(self, drivers: List[MacrobaseDriver]):
        self.queue = Queue(maxsize=len(drivers))

        for driver in drivers:
            self._processes.append(self._get_process(driver))

        for driver, process in self._processes:
            process.start()
            log.debug(f'Driver {driver} started with {process.pid} pid')

        self.join_and_terminate()

    def join_and_terminate(self):
        while True:
            pid = self.queue.get()
            log.debug(f'Driver completed with {pid} pid')

            self.terminate()
            break

        for _, process in self._processes:
            process.join()

    def terminate(self):
        # the above processes will block this until they're stopped
        for _, process in self._processes:
            if process.is_alive() is False:
                continue

            process.terminate()
