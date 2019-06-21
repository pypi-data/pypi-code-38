from functools import lru_cache
import logging

from abc import ABC

from compose_flow import errors, shell
from compose_flow.config import get_config
from compose_flow.errors import (
    CommandError,
    EnvError,
    NoSuchConfig,
    NoSuchProfile,
    NotConnected,
    ProfileError,
    TagVersionError,
)


class BaseSubcommand(ABC):
    """
    Parent class for any subcommand class
    """

    dirty_working_copy_okay = False

    # profile checks only check environment by default
    profile_checks = ['check_env']

    # whether this subcommand should connect to the remote host
    remote_action = True

    # whether the env should be in read/write mode
    rw_env = False

    # by default command setup the workflow environment
    setup_environment = True

    # by default commands setup render a profile compose file
    setup_profile = True

    # when creating a workflow environment, whether variables that reference
    # the project version should be updated (i.e. DOCKER_IMAGE)
    update_version_env_vars = False

    def __init__(self, workflow):
        self.workflow = workflow

    @property
    def logger(self):
        return logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    def do_validate_profile(self):
        return True

    def execute(self, command: str, **kwargs):
        """
        Executes the given command
        """
        # get the environment from kwargs or else use the workflow environment
        # use the `or` syntax so that the environment data is not evaluated unless env is not passed in
        env = kwargs.pop('_env', None) or self.workflow.environment.data

        return shell.execute(command, env, **kwargs)

    def get_subcommand(self, name: str) -> object:
        """
        Returns the requested subcommand class by name
        """
        from . import get_subcommand_class

        subcommand_cls = get_subcommand_class(name)

        return subcommand_cls(self.workflow)

    @classmethod
    def fill_subparser(cls, parser, subparser):
        """
        Stub for adding arguments to this subcommand's subparser
        """

    def handle(self):
        return self.handle_action()

    def handle_action(self):
        action = self.workflow.args.action

        action_fn = getattr(self, f'action_{action}', None)
        if not action_fn:
            action_fn = getattr(self, action, None)

        if action_fn:
            return action_fn()
        else:
            self.print_subcommand_help(self.__doc__, error=f'unknown action={action}')

    def is_dirty_working_copy_okay(self, exc: Exception) -> bool:
        """
        Checks to see if the project's compose-flow.yml allows for the env to use a dirty working copy

        To configure an environment to allow a dirty working copy, add the following to the compose-flow.yml

        ```
        options:
          env_name:
            dirty_working_copy_okay: true
        ```

        This defaults to False
        """
        config = get_config() or {}
        env = self.workflow.args.environment

        dirty_working_copy_okay = self.workflow.args.dirty or config.get(
            'options', {}
        ).get(env, {}).get('dirty_working_copy_okay', self.dirty_working_copy_okay)

        return dirty_working_copy_okay

    def is_env_error_okay(self, exc):
        return False

    def is_env_runtime_error_okay(self):
        return False

    def is_missing_config_okay(self, exc):
        return False

    def is_missing_env_arg_okay(self):
        return False

    def is_missing_profile_okay(self, exc):
        return False

    def is_not_connected_okay(self, exc):
        return False

    def is_write_profile_error_okay(self, exc):
        return False

    def print_subcommand_help(self, doc, error=None):
        print(doc.lstrip())

        self.workflow.parser.print_help()

        if error:
            return f'\nError: {error}'

    @classmethod
    def setup_subparser(cls, parser, subparsers):
        name = cls.__name__.lower()
        aliases = getattr(cls, 'aliases', [])

        subparser = subparsers.add_parser(name, aliases=aliases)
        subparser.set_defaults(subcommand_cls=cls)

        cls.fill_subparser(parser, subparser)


class BaseBuildSubcommand(BaseSubcommand):
    """
    Provides common functionality used by subcommands which build images
    """

    rw_env = True
    remote_action = True
    update_version_env_vars = True

    def do_validate_profile(self):
        return False

    @classmethod
    def fill_subparser(cls, parser, subparser) -> None:
        pass

    def is_missing_env_arg_okay(self):
        return True

    @property
    @lru_cache()
    def compose(self):
        """
        Returns a Compose subcommand
        """
        from .compose import Compose

        return Compose(self.workflow)

    def build(self, pull=True):
        compose_args = ['build']

        if pull:
            compose_args.append('--pull')

        self.compose.handle(extra_args=compose_args)
