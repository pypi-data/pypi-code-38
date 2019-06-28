"""Abstract stuff such as base classes, types, etc

Separated based on the hypothesis that such things tend to have many dependents
but not many dependencies within a project.
"""
from abc import ABC, abstractmethod
from typing import List


class Formatter(ABC):
    """Template class for checker plugins
    """

    @abstractmethod
    def check(self, path: str) -> List[str]:
        """Check format of a single file.
        """

    @abstractmethod
    def fix(self, path: str) -> List[str]:
        """Attempt to fix the format of a single file.
        """

    @abstractmethod
    def match(self, path: str) -> bool:
        """Check if this checker is applicable to file.
        """
