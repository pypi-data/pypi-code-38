"""
Task subcommand
"""
from functools import lru_cache
import logging
import shlex

from .base import BaseSubcommand

from compose_flow.config import get_config
from compose_flow.errors import CommandError


ALLOWED_COMMANDS = ['compose-flow', 'rancher']
PROFILE_SUBCOMMANDS = ['compose-flow', 'compose']

class Task(BaseSubcommand):
    # tasks should update version vars in order to be able to run tasks
    # that have just been built, but the version vars should not be
    # persisted to the config
    update_version_env_vars = True

    @classmethod
    def fill_subparser(self, parser, subparser):
        subparser.add_argument('name', help='the task name to process')

    @property
    def task_name(self):
        return self.workflow.args.name

    @property
    @lru_cache()
    def task_config(self):
        config = get_config()
        try:
            task = config['tasks'][self.task_name]
        except KeyError:
            raise CommandError(f'task name={self.task_name} not found')

        return task

    @property
    def command_split(self):
        command = self.task_config['command']
        return shlex.split(command)

    @property
    def setup_profile(self):
        if self.command_split[1] in PROFILE_SUBCOMMANDS:
            return True
        else:
            return False

    def handle(self):
        if not self.command_split[0] in ALLOWED_COMMANDS:
            raise NotImplementedError(
                'tasks that are not compose-flow are not yet supported'
            )

        subcommand_name = self.command_split[1]
        subcommand = self.get_subcommand(subcommand_name)

        subcommand_args = self.command_split[2:]

        remainder = self.workflow.args_remainder
        if remainder:
            subcommand_args.extend(remainder)

        subcommand.handle(subcommand_args)

    def is_dirty_working_copy_okay(self, exc: Exception) -> bool:
        dirty_working_copy_okay = super().is_dirty_working_copy_okay(exc)

        if not dirty_working_copy_okay and self.workflow.args.environment in ('local',):
            self.logger.warning(
                (
                    '\n\n'
                    'WARNING: the local environment does not allow a dirty working copy by default.'
                    '\n'
                    'in your compose-flow.yml set `options -> local -> dirty_working_copy_okay` to true'
                    '\n\n'
                )
            )

        return dirty_working_copy_okay

    @property
    def logger(self):
        return logging.getLogger(f'{__name__}.{self.__class__.__name__}')
