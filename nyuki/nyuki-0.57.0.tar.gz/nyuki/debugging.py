import signal
import logging
import collections
from nyuki.api import resource, Response


log = logging.getLogger(__name__)


@resource('/samples')
class ApiSampleEmitter:

    async def get(self, request):
        if self.nyuki._sampler is None:
            return Response(status=404)
        return Response(self.nyuki._sampler.output_stats())


class StackSampler:

    """
    Basic stack sampler, inspired by https://nylas.com/blog/performance
    Can be easily paired with https://github.com/brendangregg/FlameGraph
    """

    def __init__(self, interval=0.005):
        log.info('Debug mode, sampling enabled every %s', interval)
        self.interval = interval
        self._stack_counts = collections.defaultdict(int)

    def __del__(self):
        self.stop()

    def start(self):
        signal.signal(signal.SIGVTALRM, self._sample)
        signal.setitimer(signal.ITIMER_VIRTUAL, self.interval)

    def stop(self):
        self._stack_counts = collections.defaultdict(int)
        signal.setitimer(signal.ITIMER_VIRTUAL, 0)

    def _sample(self, signum, frame):
        stack = []
        while frame is not None:
            stack.append('{}({})'.format(
                frame.f_code.co_name,
                frame.f_globals.get('__name__'),
            ))
            frame = frame.f_back

        stack = ';'.join(reversed(stack))
        self._stack_counts[stack] += 1
        signal.setitimer(signal.ITIMER_VIRTUAL, self.interval)

    def output_stats(self):
        lines = []
        ordered_stacks = sorted(
            self._stack_counts.items(),
            key=lambda kv: kv[1],
            reverse=True,
        )
        lines.extend([
            '{} {}'.format(frame, count)
            for frame, count in ordered_stacks
        ])
        return '\n'.join(lines) + '\n'
