"""External dependency version module"""
from abc import ABC, abstractmethod

class ExternalVersion(ABC):
    """Define interface for managing external dependency versions"""

    @staticmethod
    @abstractmethod
    def existing():
        """Return installed version"""

    @staticmethod
    @abstractmethod
    def latest():
        """Return latest version available"""

    @staticmethod
    @abstractmethod
    def update(verbose=False):
        """Update installed version to latest if necessary"""
