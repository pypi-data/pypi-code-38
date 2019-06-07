from threading import Thread
from egcg_core.exceptions import EGCGError
from .stream_executor import StreamExecutor


class ArrayExecutor(StreamExecutor):
    def __init__(self, cmds, stream):
        """
        :param cmds:
        :param bool stream: Whether to run all commands in parallel or one after another
        """
        super().__init__(cmds)
        self.executors = []
        self.exit_statuses = []
        self.stream = stream
        for c in cmds:
            self.executors.append(StreamExecutor(c))

    def run(self):
        try:
            if self.stream:
                for e in self.executors:
                    e.start()
                for e in self.executors:
                    self.exit_statuses.append(e.join())
            else:
                for e in self.executors:
                    e.start()
                    self.exit_statuses.append(e.join())
        except Exception as err:
            self.exception = err

    def join(self, timeout=None):
        # noinspection PyCallByClass
        Thread.join(self, timeout)
        if self.exception:
            self._stop()
            self.error(self.exception.__class__.__name__ + ': ' + str(self.exception))
            raise EGCGError('Commands failed: ' + str(self.exit_statuses)) from self.exception
        self.info('Exit statuses: %s', self.exit_statuses)
        return sum(self.exit_statuses)
