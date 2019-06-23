import logging
from missinglink.resource_manager.docker.sync_async_tools import run_blocking_code_in_thread
from dateutil import parser
import time
import docker
import asyncio
import requests
import json

logger = logging.getLogger(__name__)


class StatGenerator:
    def __init__(self, container, name=None):
        self.container = container
        self.id = name or self.container.name

    def _keep_reading_stats(self):
        try:
            self.container.reload()
            if self.container.status != 'running':
                logger.debug('%s:STATS: No more stats: %s', self.id, self.container.status)
                return False
        except requests.exceptions.ReadTimeout:
            # Edge case where the docker deamon is unresponsive during IOPS heavy periods
            logger.warning('%s:STATS: Timeout reading stats: %s', self.id, self.container.status)
            time.sleep(30)

        return True

    def _get_stat_from_docker(self):
        try:
            stat = self.container.stats(stream=False)
            return self._stats(stat)
        except json.decoder.JSONDecodeError:
            logger.debug('Failed to get stats from docker daemon - json serialisation issue')
            return None

    def _read_stats_blocking(self):
        try:
            while self._keep_reading_stats():
                stat_obj = self._get_stat_from_docker()
                if stat_obj is None:
                    if not self._keep_reading_stats():
                        break

                    logger.warning('%s:STATS: Empty Stats, state: %s', self.id, self.container.status)
                    continue

                logger.debug('%s:STAT: Sending stats %s', self.id, stat_obj)
                return stat_obj
            logger.debug('%s:STATS: DONE Sending stats', self.id)
            raise StopAsyncIteration
        except docker.errors.NotFound:
            raise StopAsyncIteration

    async def __anext__(self):
        try:
            x = await run_blocking_code_in_thread(self._read_stats_blocking, logger=logger, loop=asyncio.get_event_loop())
            return x
        except StopIteration:
            raise StopAsyncIteration

    def __aiter__(self):
        logger.debug('%s:STATS: start', self.id)
        return self

    def _get_stat_id(self, stat):
        # Windows containers do not return the id in the stat object
        return stat.get('id') or self.container.id

    def _stats(self, stat):
        if not ('read' in stat and parser.parse(stat['read']).year != 1):
            return

        # https://github.com/moby/moby/blob/eb131c5383db8cac633919f82abad86c99bffbe5/cli/command/container/stats_helpers.go#L175
        def mem_usage():
            memstat = stat.get('memory_stats', {})
            return memstat.get('usage', 0), memstat.get('limit', 0)

        # https://github.com/moby/moby/blob/eb131c5383db8cac633919f82abad86c99bffbe5/cli/command/container/stats_helpers.go#L175
        def cpu_usage():
            cpu_percent = 0.0
            pre_cpu_stat = stat.get('precpu_stats', {})
            pre_cpu = pre_cpu_stat.get('cpu_usage', {}).get('total_usage', 0)
            pre_system = pre_cpu_stat.get('system_cpu_usage', 0)
            cur_system = stat.get('cpu_stats', {}).get('system_cpu_usage', 0)
            cur_cpu = stat.get('cpu_stats', {}).get('cpu_usage', {}).get('total_usage', 0)
            cpu_delta = cur_cpu - pre_cpu
            system_delta = cur_system - pre_system
            cpu_count = len(stat.get('cpu_stats', {}).get('cpu_usage', {}).get('percpu_usage', []))

            if cpu_delta > 0 and system_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * cpu_count * 100

            return cpu_count, cpu_percent

        mem_usage, mem_limit = mem_usage()
        mem_limit = max(0.0001, mem_limit)
        cpu_count, cpu_percent = cpu_usage()
        shares = max(0.0001, self.container.attrs['HostConfig'].get('NanoCpus', 0) / 1000000000.0)
        x = {
            'id': self._get_stat_id(stat),
            'cpu': {
                'usage': round(cpu_percent, 2),
                'count': cpu_count,
                'shares': shares,
                'of_shares': round(cpu_percent / shares, 2)
            },
            'mem': {
                'usage': round((mem_usage * 100.0) / mem_limit, 2),
                'limit': round(mem_limit, 2),
            }
        }
        return x
