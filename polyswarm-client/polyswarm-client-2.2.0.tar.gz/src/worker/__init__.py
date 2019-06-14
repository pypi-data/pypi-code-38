import asyncio
import json
import logging
import signal
import sys
import time

import aiohttp
import aioredis
from polyswarmartifact import ArtifactType

from polyswarmclient.utils import asyncio_join, asyncio_stop, exit, MAX_WAIT

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 5.0


class ApiKeyException(Exception):
    pass


class ExpiredException(Exception):
    pass


class Worker(object):
    def __init__(self, redis_addr, queue, task_count=1, download_limit=1, scan_limit=1, api_key=None, testing=0,
                 scanner=None):
        self.redis_uri = 'redis://' + redis_addr
        self.queue = queue
        self.api_key = api_key
        self.testing = testing
        self.scanner = scanner
        self.task_count = task_count
        self.download_limit = download_limit
        self.scan_limit = scan_limit
        self.download_lock = None
        self.scan_lock = None
        self.tries = 0
        self.finished = False

    def handle_signal(self):
        logger.critical(f'Received SIGTERM. Gracefully shutting down.')
        self.finished = True

    def run(self):
        while not self.finished:
            loop = asyncio.SelectorEventLoop()

            # Default event loop does not support pipes on Windows
            if sys.platform == 'win32':
                loop = asyncio.ProactorEventLoop()

            asyncio.set_event_loop(loop)

            loop.add_signal_handler(signal.SIGTERM, self.handle_signal)
            try:
                asyncio.get_event_loop().run_until_complete(self.setup())
                gather_task = asyncio.gather(*[self.run_task(i) for i in range(self.task_count)])
                asyncio.get_event_loop().run_until_complete(gather_task)
            except asyncio.CancelledError:
                logger.info('Clean exit requested, exiting')

                asyncio_join()
                exit(0)
            except Exception:
                logger.exception('Unhandled exception at top level')
                asyncio_stop()
                asyncio_join()

                self.tries += 1
                wait = min(MAX_WAIT, self.tries * self.tries)

                logger.critical(f'Detected unhandled exception, sleeping for {wait} seconds then resetting task')
                time.sleep(wait)
                continue

    async def setup(self):
        self.scan_lock = asyncio.Semaphore(value=self.scan_limit)
        self.download_lock = asyncio.Semaphore(value=self.download_limit)
        if not await self.scanner.setup():
            logger.critical('Scanner instance reported unsuccessful setup. Exiting.')
            exit(1)

    async def run_task(self, task_index):
        conn = aiohttp.TCPConnector(limit=0, limit_per_host=0)
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
            redis = await aioredis.create_redis_pool(self.redis_uri)
            while not self.finished:
                try:
                    next_job = await redis.blpop(self.queue, timeout=1)
                    if next_job is None:
                        continue

                    _, job = next_job
                    job = json.loads(job.decode('utf-8'))
                    logger.info(f'Got job on task {task_index}', extra={'extra': job})

                    guid = job['guid']
                    uri = job['uri']

                    polyswarmd_uri = job['polyswarmd_uri']

                    if self.api_key and not polyswarmd_uri.startswith('https://'):
                        raise ApiKeyException()

                    index = job['index']
                    chain = job['chain']

                    duration = job['duration']
                    timestamp = job['ts']
                    artifact_type = ArtifactType(int(job['artifact_type']))

                    if timestamp + duration <= time.time() // 1:
                        raise ExpiredException()

                except OSError:
                    logger.exception('Redis connection down')
                    continue
                except aioredis.errors.ReplyError:
                    logger.exception('Redis out of memory')
                    continue
                except KeyError as e:
                    logger.exception(f"Bad message format on task {task_index}: {e}")
                    continue
                except ExpiredException:
                    logger.exception(f'Received expired job {guid} index {index}')
                    continue
                except ApiKeyException:
                    logger.exception("Refusing to send API key over insecure transport")
                    continue
                except (AttributeError, TypeError, ValueError):
                    logger.exception('Invalid job received, ignoring')
                    continue

                headers = {'Authorization': self.api_key} if self.api_key is not None else None
                uri = f'{polyswarmd_uri}/artifacts/{uri}/{index}'
                async with self.download_lock:
                    try:
                        response = await session.get(uri, headers=headers)
                        response.raise_for_status()

                        content = await response.read()
                    except aiohttp.ClientResponseError:
                        logger.exception(f'Error fetching artifact {uri} on task {task_index}')
                        continue
                    except asyncio.TimeoutError:
                        logger.exception(f'Timeout fetching artifact {uri} on task {task_index}')
                        continue

                async with self.scan_lock:
                    result = await self.scanner.scan(guid, artifact_type, content, chain)

                j = json.dumps({
                    'index': index,
                    'bit': result.bit,
                    'verdict': result.verdict,
                    'confidence': result.confidence,
                    'metadata': result.metadata,
                })

                logger.info(f'Scan results on task {task_index}', extra={'extra': j})

                key = f'{self.queue}_{guid}_{chain}_results'
                try:
                    await redis.rpush(key, j)
                    self.tries = 0
                except OSError:
                    logger.exception('Redis connection down')
                except aioredis.errors.ReplyError:
                    logger.exception('Redis out of memory')
