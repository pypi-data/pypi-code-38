"""
Kompose subcommand
"""
import argparse
import logging
import os

from .passthrough_base import PassthroughBaseSubcommand

from compose_flow import errors

DEFAULT_COMPOSE_FILENAME = 'docker-compose.yml'


class Kompose(PassthroughBaseSubcommand):
    """
    Subcommand for migrating to Kubernetes with kompose commands
    """
    command_name = 'kompose'
    dirty_working_copy_okay = True
    update_version_env_vars = True

    def __init__(self, *args, check_profile=True, version=None, **kwargs):
        self.check_profile = check_profile
        self._version = version

        super().__init__(*args, **kwargs)

    def get_command(self):
        command = super().get_command()

        profile = self.workflow.profile
        command.extend(['-f', profile.filename])
        command.extend(['-o', 'compose-flow-kompose.yml'])

        return command

    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    @property
    def version(self):
        """
        Returns the version in the environment, unless it was overridden in this Compose instance
        """
        return self._version or self.env.version  # pylint: disable=E1101
