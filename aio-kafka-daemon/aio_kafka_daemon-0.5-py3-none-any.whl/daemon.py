"""
aiokafkadaemon Daemon class
"""
import asyncio
import logging
import signal
from .worker import Worker


async def default_exit_handler(signame, worker, logger):
    logger.warning(f'Exit signal {signame} requested, default '
                   f'handler activated, stopping daemon.')
    await worker.stop()


class Daemon:
    def __init__(self, test=False, worker=None,
                 abort_handler=None, **kwargs):
        """
        :param test:
        :param worker:
        """
        self._worker = worker
        self._signal_handler = abort_handler \
            if abort_handler \
            else default_exit_handler
        if not self._worker:
            self._worker = Worker(**kwargs)

    async def run(self):
        loop = asyncio.get_event_loop()
        logger = logging.getLogger('Daemon')
        logger.debug('Starting AIOKafkaDaemon')
        for signame in ('SIGINT', 'SIGTERM'):
            loop.add_signal_handler(
                getattr(signal, signame), lambda: asyncio.ensure_future(
                    self._signal_handler(signame, self._worker, logger)
                )
            )
        await self._worker.run()
        logger.debug('AIOKafkaDaemon stopped')


def main():
    daemon = Daemon()
    daemon.run()


if __name__ == '__main__':
    main()
