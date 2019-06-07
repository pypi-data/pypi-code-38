from select import select
from threading import Thread
from egcg_core.executor import Executor
from egcg_core.exceptions import EGCGError


class StreamExecutor(Thread, Executor):
    def __init__(self, cmd):
        """
        :param str cmd: A shell command to be executed
        """
        self.exception = None
        Executor.__init__(self, cmd)
        Thread.__init__(self)

    def join(self, timeout=None):
        """
        Ensure that both the thread and the subprocess have finished, and return self.proc's exit status.
        :param int timeout: As Thread.join
        """
        super().join(timeout=timeout)
        if self.exception:
            self._stop()
            self.error('Encountered a %s error: %s', self.exception.__class__.__name__, self.exception)
            raise EGCGError('Command failed: ' + self.cmd) from self.exception

        return self.proc.wait()

    def run(self):
        try:
            self._stream_output()
        except Exception as e:
            self.exception = e

    def _stream_output(self):
        """Run self._process and log its stdout/stderr until an EOF."""
        proc = self._process()
        read_set = [proc.stdout, proc.stderr]
        while read_set:
            rlist, wlist, xlist = select(read_set, [], [])

            for stream, emit in ((proc.stdout, self.info), (proc.stderr, self.error)):
                if stream in rlist:
                    line = stream.readline().decode('utf-8').strip()
                    if line:
                        emit(line)
                    else:
                        stream.close()
                        read_set.remove(stream)
