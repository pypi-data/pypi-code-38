
from .base import BaseBuildSubcommand


class Build(BaseBuildSubcommand):
    """
    Subcommand for building Docker images
    """

    dirty_working_copy_okay = True

    def handle(self):
        self.build()
