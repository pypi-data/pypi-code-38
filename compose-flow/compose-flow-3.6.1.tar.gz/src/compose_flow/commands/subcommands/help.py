"""
Welcome to Docker Compose Workflows!

This is a utility around Docker Compose to make it easier to use
around commonly used workflows within your development team.
"""
from .base import BaseSubcommand


class Help(BaseSubcommand):
    """
    Subcommand for managing profiles
    """

    @classmethod
    def fill_subparser(self, parser, subparser):
        pass

    def handle(self):
        self.print_subcommand_help(__doc__)
