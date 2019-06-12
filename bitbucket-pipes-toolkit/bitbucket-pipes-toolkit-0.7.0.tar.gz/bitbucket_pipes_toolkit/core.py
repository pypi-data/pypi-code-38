import os

import yaml
from cerberus import Validator

from .helpers import fail, success, configure_logger, enable_debug, get_logger


logger = configure_logger()


class Pipe:
    """Base class for all pipes. Provides utitilites to work with configuration, validation etc.

    Attributes:
        variables (dict): Dictionary containing the pipes variables.
        schema (dict): Dictionary with the pipe parameters shema in the cerberus format.

    """

    def fail(self, message):
        """Fail the pipe and exit.

        Args:
            message (str): Error message to show.
        """
        fail(message=message)

    def success(self, message, do_exit=False):
        """Show a success message.

        Args:
            message (str): Message to print
            do_exit (bool): Call sys.exit or not

        """
        success(message, do_exit=do_exit)

    def enable_debug_log_level(self):
        """Enable the DEBUG log level."""

        if self.get_variable('DEBUG'):
            logger.setLevel('DEBUG')

    def __init__(self, pipe_metadata=None, schema=None):
        if pipe_metadata is None:
            pipe_metadata = os.path.join(os.path.dirname(__file__), 'pipe.yml')

        with open(pipe_metadata, 'r') as f:
            self.metadata = yaml.safe_load(f.read())

        self.variables = None
        self.schema = schema
        # validate pipe parameters
        self.variables = self.validate()

    @classmethod
    def from_pipe_yml(cls, ):
        pass

    def validate(self):
        """Validates the environment variables against a provided schema.

        Variable schema is a dictionary in a cerberus format. See https://docs.python-cerberus.org/en/stable/ 
        for more details about this library and validation rules.

        """
        if self.schema is None:
            schema = self.metadata['variables']
        else:
            schema = self.schema

        validator = Validator(
            schema=schema, purge_unknown=True)
        env = {key:yaml.safe_load(value) for key, value in os.environ.items() if key in schema}

        if not validator.validate(env):
            self.fail(
                message=f'Validation errors: \n{yaml.dump(validator.errors, default_flow_style = False)}')
        validated = validator.validated(env)
        return validated

    def get_variable(self, name):
        """Retrive a pipe variable.

        Args:
            name (str): The name of a variable.

        Returns:
            The value of the variable.
        """

        return self.variables[name]

    def run(self):
        """Run the pipe.

        The main entry point for a pipe execution. This will do
        all the setup steps, like enabling debug mode if configure etc.
        """
        self.enable_debug_log_level()
