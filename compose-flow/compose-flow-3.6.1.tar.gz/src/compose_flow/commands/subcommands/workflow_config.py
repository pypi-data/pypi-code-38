import os

from .base import BaseSubcommand


class WorkflowConfig(BaseSubcommand):
    remote_action = False
    setup_profile = False

    def cat(self):
        """
        Prints the loaded compose file to stdout
        """

        config_path = self.workflow.app_config_path
        if os.path.exists(config_path):
            with open(config_path, 'r') as fh:
                print(fh.read())

    @classmethod
    def fill_subparser(cls, parser, subparser):
        subparser.add_argument('action')
