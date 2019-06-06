import logging
import random
import os

from concurrent.futures import CancelledError

from polyswarmartifact import ArtifactType

from polyswarmclient.abstractambassador import AbstractAmbassador
from polyswarmclient.corpus import DownloadToFileSystemCorpus

logger = logging.getLogger(__name__)

ARTIFACT_DIRECTORY = os.getenv('ARTIFACT_DIRECTORY', 'docker/artifacts')
ARTIFACT_BLACKLIST = os.getenv('ARTIFACT_BLACKLIST', 'truth.db').split(',')
BOUNTY_TEST_DURATION_BLOCKS = int(os.getenv('BOUNTY_TEST_DURATION_BLOCKS', 5))


class Ambassador(AbstractAmbassador):
    """Ambassador which submits artifacts from a directory"""

    def __init__(self, client, testing=0, chains=None, watchdog=0, submission_rate=30):
        """Initialize a filesystem ambassador

        Args:
            client (`Client`): Client to use
            testing (int): How many test bounties to respond to
            chains (set[str]): Chain(s) to operate on
        """
        super().__init__(client, testing, chains, watchdog, submission_rate)

        self.artifacts = []
        u = os.getenv("MALICIOUS_BOOTSTRAP_URL")
        if u:
            logger.info("Unpacking malware corpus at {0}".format(u))
            d = DownloadToFileSystemCorpus()
            d.download_and_unpack()
            bfl = d.get_benign_file_list()
            mfl = d.get_malicious_file_list()
            logger.info("Unpacking complete, {0} malicious and {1} benign files".format(len(mfl), len(bfl)))
            self.artifacts = bfl + mfl
        else:
            for root, dirs, files in os.walk(ARTIFACT_DIRECTORY):
                for f in files:
                    self.artifacts.append(os.path.join(root, f))

    async def generate_bounties(self, chain):
        """Submit bounty from the filesystem

        Args:
            chain (str): Chain sample is being requested from
        """
        amount = await self.client.bounties.parameters[chain].get('bounty_amount_minimum')

        while True:
            try:
                filename = random.choice(self.artifacts)

                logger.info('Submitting file %s', filename)
                ipfs_uri = await self.client.post_artifacts([(filename, None)])
                if not ipfs_uri:
                    logger.error('Error uploading artifact to IPFS, continuing')
                    continue

                await self.push_bounty(ArtifactType.FILE, amount, ipfs_uri, BOUNTY_TEST_DURATION_BLOCKS, chain)
            except CancelledError:
                logger.warning('Cancel requested')
                break
            except Exception:
                logger.exception('Exception in bounty generation task, continuing')
                continue
