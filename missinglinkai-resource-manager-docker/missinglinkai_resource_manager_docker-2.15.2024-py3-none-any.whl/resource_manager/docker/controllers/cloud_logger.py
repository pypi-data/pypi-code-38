import asyncio
import datetime
import logging
import aiohttp
from unicodedata import category
import dateutil.parser

from missinglink.resource_manager.docker.utils import is_windows_containers

logger = logging.getLogger(__name__)


class CloudLogger:
    allowed_white_spaces = set(['\n', '\t'])
    MAX_LOGS_PER_SUBMISSION = 1000
    MAX_WAIT_ON_CLOSE_SECONDS = 15
    EMPTY_LOG_SLEEP_SECONDS = 1

    @classmethod
    def get_printable(cls, x):
        # https://stackoverflow.com/a/19016117/133568
        if isinstance(x, bytes):
            x = x.decode('utf-8')
        return ''.join([s for s in x if s in cls.allowed_white_spaces or category(s)[0] != "C"])

    def __init__(self, endpoint, loop=None):
        self.endpoint = endpoint
        self.loop = loop or asyncio.get_event_loop()

        self.pending_logs = []
        self.transit_logs = []
        self.running = True
        self._refresh_session()
        self._setup_task()

    def _setup_task(self):
        self.task = asyncio.ensure_future(self.send_logs(), loop=self.loop)
        self.task.add_done_callback(self._on_done)

    def _refresh_session(self):
        self.session = aiohttp.ClientSession(loop=self.loop)

    def __enter__(self):
        raise TypeError("Use async with instead")

    def __exit__(self, exc_type, exc_val, exc_tb):
        # __exit__ should exist in pair with __enter__ but never executed
        pass  # pragma: no cover

    async def __aenter__(self):
        return self

    @property
    def _has_any_logs(self):
        return self.pending_logs or self.transit_logs

    def _reverse_logs(self):
        if not self.pending_logs:
            return
        logger.warning('reversing %s log lines' % len(self.pending_logs))
        self.pending_logs = list(self.pending_logs[::-1])

    def _drop_logs(self):
        if not self.pending_logs:
            return

        start_ts = dateutil.parser.parse(self.pending_logs[-1]['ts']).strftime("%Y-%m-%d %H:%M:%S")
        end_ts = dateutil.parser.parse(self.pending_logs[0]['ts']).strftime("%Y-%m-%d %H:%M:%S")
        log_lines_count = len(self.pending_logs)
        logger.warning('%s Log lines for the period %s - %s ware not reported due to logging backlog' % (log_lines_count, start_ts, end_ts))
        self.pending_logs = [{'level': 'WARNING', 'message': '%s Log lines for the period %s - %s ware not reported due to logging backlog' % (log_lines_count, start_ts, end_ts), 'category': 'Resource Manager', 'ts': datetime.datetime.utcnow().isoformat()}]

    async def wait_for_logs(self, seconds):
        stop_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
        while self._has_any_logs and datetime.datetime.utcnow() < stop_time:
            await asyncio.sleep(1)

    async def close(self):
        self.running = False
        await self.wait_for_logs(self.MAX_WAIT_ON_CLOSE_SECONDS)
        self._reverse_logs()
        await self.wait_for_logs(self.MAX_WAIT_ON_CLOSE_SECONDS)
        self._drop_logs()
        await self.wait_for_logs(self.MAX_WAIT_ON_CLOSE_SECONDS)
        self.task.cancel()
        await self.session.close()
        await  asyncio.sleep(0.25)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _on_done(self, done_task: asyncio.Task):
        # noinspection PyBroadException
        try:
            done_task.result()
            logger.debug('%s: logs transmission completed ', self.endpoint)
        except asyncio.CancelledError:
            logger.info('Line %s was not sent to server, the send task was cancelled', ' , '.join(self.transit_logs))
        except asyncio.InvalidStateError:
            logger.info("Line %s was not sent to server, the send task hasn't started", ' , '.join(self.transit_logs))

        except Exception:
            logger.exception('Failed to post log line %s', ' , '.join(self.transit_logs))

    def _return_transit_logs_to_pending(self):
        self.pending_logs = self.transit_logs + self.pending_logs
        self.pending_logs = []

    def _build_log_transmission_batch(self):
        self.transit_logs, self.pending_logs = list(self.pending_logs[:self.MAX_LOGS_PER_SUBMISSION]), list(self.pending_logs[self.MAX_LOGS_PER_SUBMISSION:])

    def __handle_cancelled(self, ex):
        if isinstance(ex, asyncio.CancelledError):
            logger.warning('CancelledError when sending logs, returning %s log lines to the queue (with %s log lines already pending) ', len(self.transit_logs), len(self.pending_logs))
            # pass cancelled to parent
            raise ex

    async def _send_logs_internal(self):
        if not self.transit_logs:
            return

        logger.debug('%s logs lines to be sent, %s left in queue', len(self.transit_logs), len(self.pending_logs))
        start_time = datetime.datetime.utcnow()

        post_args = {
            'url': self.endpoint,
            'json': self.transit_logs,
        }

        if is_windows_containers():
            post_args['verify_ssl'] = False

        await self.session.post(**post_args)
        end_time = datetime.datetime.utcnow()
        logger.debug('%s logs lines sent in %s, %s left in queue', len(self.transit_logs), end_time - start_time, len(self.pending_logs))
        self.transit_logs = []

    async def _send_logs_iteration(self):
        if not self.pending_logs:
            return await asyncio.sleep(self.EMPTY_LOG_SLEEP_SECONDS)

        try:
            self._build_log_transmission_batch()
            await self._send_logs_internal()

        except aiohttp.client_exceptions.ClientConnectorError as ex:
            logger.info('Failed to send "%s" to ML: %s', ' , '.join(self.transit_logs), str(ex))
            self._return_transit_logs_to_pending()

        except RuntimeError:
            logger.warning('RuntimeError when sending logs, returning %s log lines to the queue (with %s log lines already pending) ', len(self.transit_logs), len(self.pending_logs))
            self._refresh_session()
            self._return_transit_logs_to_pending()

        except Exception as ex:
            self.__handle_cancelled(ex)
            logger.exception('Failed to send %s log lines:' % len(self.transit_logs))
            for line in self.transit_logs:
                logger.error(line)

    def _print_pending_logs(self, func_=None):
        func_ = func_ or logger.warning
        func_('Failed to send %s log lines', len(self.pending_logs))

    async def send_logs(self):
        while self.running or self._has_any_logs:
            try:
                await self._send_logs_iteration()
            except asyncio.CancelledError:
                self._print_pending_logs()
                return

    def _guess_log_level(self, line, step_name, given_level=None):
        if given_level:
            return given_level, line

        for reserved in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'FATAL']:
            target_prefix = f'{reserved}: '.lower()
            if line.lower().startswith(target_prefix):
                return reserved, line[len(target_prefix):]

        log_level_guess = 'INFO' if step_name.endswith('run') else 'DEBUG'
        return log_level_guess, line

    async def on_log(self, line, step_name=None, log_level=None):

        printable = self.get_printable(line)
        if not printable:
            return
        if not self.running:
            logger.error('Remote logger is closed, won\'t send: %s', line)
            return

        log_level, printable = self._guess_log_level(printable, step_name, log_level)
        self.pending_logs.append({'level': log_level, 'message': printable, 'category': step_name or 'CloudLogger', 'ts': datetime.datetime.utcnow().isoformat()})
