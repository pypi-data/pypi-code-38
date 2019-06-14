import logging
import os

from polyswarmartifact import ArtifactType

from polyswarmclient.abstractmicroengine import AbstractMicroengine
from polyswarmclient.producer import Producer

logger = logging.getLogger(__name__)

REDIS_ADDR = os.getenv('REDIS_ADDR', 'localhost:6379')
QUEUE = os.getenv('QUEUE')

TIME_TO_POST_ASSERTION = 4
KEY_TIMEOUT = 20


class Microengine(AbstractMicroengine):
    def __init__(self, client, testing=0, scanner=None, chains=None, artifact_types=None, bid_strategy=None):
        if artifact_types is None:
            artifact_types = [ArtifactType.FILE]
        super().__init__(client, testing, None, chains, artifact_types, bid_strategy)

        if QUEUE is None:
            raise ValueError('No queue configured, set the QUEUE environment variable')
        if QUEUE.endswith('_results'):
            raise ValueError('Queue name cannot end with "_results"')

        self.client.on_run.register(self.__handle_run)
        self.redis = None

    async def __handle_run(self, chain):
        if self.redis is None:
            redis_uri = 'redis://' + REDIS_ADDR

            self.producer = Producer(self.client, redis_uri, QUEUE, TIME_TO_POST_ASSERTION)
            await self.producer.start()

    async def fetch_and_scan_all(self, guid, artifact_type, uri, duration, chain):
        """Overrides the default fetch logic to embed the URI and index rather than downloading on producer side

        Args:
            guid (str): GUID of the associated bounty
            artifact_type (ArtifactType): Artifact type for the bounty being scanned
            uri (str):  Base artifact URI
            duration (int): Blocks until vote round ends
            chain (str): Chain we are operating on

        Returns:
            list(ScanResult): List of ScanResult objects
        """
        return await self.producer.scan(guid, artifact_type, uri, duration, chain)
