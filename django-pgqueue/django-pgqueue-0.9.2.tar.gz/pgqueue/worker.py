import logging
import signal
import sys
import os

from django.core.management import BaseCommand


class Worker:
    logger = logging.getLogger(__name__)
    wait_timeout = 10
    queue = None

    def __init__(self):
        self._shutdown = False
        self._is_waiting = False

    def handle_shutdown(self, sig, frame):
        if self._is_waiting:
            # If there're no active tasks let's exit immediately.
            sys.exit(0)

        self.logger.info('Waiting for active tasks to finish...')
        self._shutdown = True

    def bind_signals(self):
        """Handle the signals for warm shutdown."""
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def start(self):
        self.bind_signals()
        self.queue.listen()
        self.logger.info('Worker is started with pid {}'.format(os.getpid()))

        while True:
            if self._shutdown:
                return

            job = self.queue.dequeue()
            if job is None:
                self.wait()
                continue

            try:
                self.queue.run_job(job)
            except Exception as e:
                self.logger.exception('Error in %r: %r.', job, e, extra={
                    'data': {
                        'job': job.as_dict(),
                    },
                })

    def wait(self):
        self._is_waiting = True
        self.queue.wait(self.wait_timeout)
        self._is_waiting = False


class WorkerCommand(Worker, BaseCommand):
    def before_start(self):
        pass

    def handle(self, *args, **options):
        self.before_start()
        self.start()
