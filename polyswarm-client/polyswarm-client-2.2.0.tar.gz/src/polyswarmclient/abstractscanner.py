import logging

from polyswarmartifact.schema.verdict import Verdict
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)  # Initialize logger


class ScanResult(object):
    """Results from scanning one artifact"""

    def __init__(self, bit=False, verdict=False, confidence=1.0, metadata=Verdict().set_malware_family('').json()):
        """Report the results from scanning one artifact

        Args:
            bit (bool): Are we asserting on this artifact
            verdict (bool): Is this artifact malicious (True) or benign (False)
            confidence (float): How confident are we in our verdict ranging from 0.0 to 1.0
            metadata (str): Optional metadata from the scan
        """
        self.bit = bit
        self.verdict = verdict
        self.confidence = confidence
        self.metadata = metadata

    def __repr__(self):
        return '<ScanResult bit={}, verdict={}, confidence={}, metadata={}>'.format(self.bit, self.verdict,
                                                                                    self.confidence, self.metadata)


class AbstractScanner(ABC):
    """
    Base `Scanner` class. To be overwritten with other scanning logic.
    """

    @abstractmethod
    async def scan(self, guid, artifact_type, content, chain):
        """Override this to implement custom scanning logic

        Args:
            guid (str): GUID of the bounty under analysis, use to track artifacts in the same bounty
            artifact_type (ArtifactType): Artifact type for the bounty being scanned
            content (bytes): Content of the artifact to scan
            chain (str): What chain are we operating on
        Returns:
            ScanResult: Result of this scan
        """
        pass

    async def setup(self):
        """Override this method to implement custom setup logic.

        This is run immediately after the Scanner class is instantiated and before any calls to the scan() method.

        Args:
            None

        Returns:
            status (bool): Did setup complete successfully?
        """
        return True
