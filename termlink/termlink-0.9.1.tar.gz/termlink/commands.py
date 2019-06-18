"""Commands

This module is built for constructing command patterns.
"""

from abc import ABC, abstractmethod

class SubCommand(ABC):
    """
    An interface for create sub-commands
    """

    @staticmethod
    @abstractmethod
    def execute(args):
        """
        Executes based on the provided arguments

        Args:
            args: `argparse` parsed arguments
        """
