import aioredis
import asyncio
import json
import logging
import time

from polyswarmclient.abstractscanner import ScanResult

logger = logging.getLogger(__name__)

KEY_TIMEOUT = 20


class Producer:
    def __init__(self, client, redis_uri, queue, time_to_post):
        self.client = client
        self.redis_uri = redis_uri
        self.queue = queue
        self.time_to_post = time_to_post
        self.redis = None

    async def start(self):
        self.redis = await aioredis.create_redis_pool(self.redis_uri)

    async def scan(self, guid, artifact_type, uri, expiration_blocks, chain):
        """Creates a set of jobs to scan all the artifacts at the given URI that are passed via Redis to workers

            Args:
                guid (str): GUID of the associated bounty
                artifact_type (ArtifactType): Artifact type for the bounty being scanned
                uri (str):  Base artifact URI
                expiration_blocks (int): Blocks until vote round ends
                chain (str): Chain we are operating on

            Returns:
                list(ScanResult): List of ScanResult objects
            """
        # Ensure we don't wait past the vote round duration for one long artifact
        timeout = expiration_blocks - self.time_to_post
        logger.info(f' timeout set to {timeout}')

        async def wait_for_result(result_key):
            try:
                with await self.redis as redis:
                    result = await redis.blpop(result_key, timeout=timeout)
                    if result is None:
                        logger.critical('Timeout waiting for result in bounty %s', guid)
                        return None

                    j = json.loads(result[1].decode('utf-8'))

                    # increase perf counter for autoscaling
                    q_counter = f'{self.queue}_scan_result_counter'
                    await redis.incr(q_counter)

                    return j['index'], ScanResult(bit=j['bit'], verdict=j['verdict'], confidence=j['confidence'],
                                                  metadata=j['metadata'])
            except aioredis.errors.ReplyError:
                logger.exception('Redis out of memory')
            except OSError:
                logger.exception('Redis connection down')
            except (AttributeError, ValueError, KeyError):
                logger.error('Received invalid response from worker')
                return None

        num_artifacts = len(await self.client.list_artifacts(uri))
        jobs = [json.dumps({
            'ts': time.time() // 1,
            'guid': guid,
            'artifact_type': artifact_type.value,
            'uri': uri,
            'index': i,
            'chain': chain,
            'duration': timeout,
            'polyswarmd_uri': self.client.polyswarmd_uri}) for i in range(num_artifacts)]

        if jobs:
            try:
                await self.redis.rpush(self.queue, *jobs)

                key = '{}_{}_{}_results'.format(self.queue, guid, chain)
                results = await asyncio.gather(*[wait_for_result(key) for _ in jobs])
                results = {r[0]: r[1] for r in results if r is not None}

                # Age off old result keys
                await self.redis.expire(key, KEY_TIMEOUT)

                return [results.get(i, ScanResult()) for i in range(num_artifacts)]
            except OSError:
                logger.exception('Redis connection down')
            except aioredis.errors.ReplyError:
                logger.exception('Redis out of memory')

        return []
