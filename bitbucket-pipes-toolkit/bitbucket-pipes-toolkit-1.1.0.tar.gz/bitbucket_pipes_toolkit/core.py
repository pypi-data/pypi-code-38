import os
from collections.abc import Sequence
import json
import glob

import yaml
from cerberus import Validator

from .helpers import fail, success, configure_logger, enable_debug, get_logger


logger = configure_logger()


class ArrayVariable(Sequence):
    """

    Example:

    >>> env = {
    ...        'EXTRA_ARGS_COUNT': 3,
    ...        'EXTRA_ARGS_0': '--description',
    ...        'EXTRA_ARGS_1': 'text containing spaces',
    ...        'EXTRA_ARGS_2': '--verbose'}
    >>>
    >>> array_variable = ArrayVariable('EXTRA_ARGS', env)
    >>> array_variable[2]
    '--verbose'
    """

    def __init__(self, name, env):
        self._count = int(env.get(f'{name}_COUNT', '0'))
        self._variables = [env.get(f'{name}_{i}') for i in range(self._count)]

    def __getitem__(self, i):
        return self._variables[i]

    def __len__(self):
        return self._count

    @classmethod
    def test(cls):
        test_env={
            'EXTRA_ARG_COUNT': 3,
            'EXTRA_ARGS_0': '--description',
            'EXTRA_ARGS_1': 'text containing spaces',
            'EXTRA_ARGS_2': '--verbose'
        }
        array_variable=cls('test_variable', test_env)


class SharedData:
    """This is an interface to the shared pipes data directory

    Example:

    >>> shared_data = SharedData('/tmp')
    >>> shared_data.get_variable('foo') is None
    True
    >>> shared_data.set_variable('foo', 'bar')
    >>> shared_data.get_variable('foo')
    'bar'
    >>> shared_data.purge()

    Example storing complex data

    >>> shared_data = SharedData('/tmp')
    >>> shared_data.set_variable('my_data', {'my_variable': 'my_value'})
    >>> shared_data.get_variable('my_data')['my_variable']
    'my_value'
    >>> shared_data.purge()
    """

    def __init__(self, path):
        self._path = path
        self._shared_json_file = os.path.join(self._path, '_shared_variables.json')


    def get_json(self, name):
        with open(os.path.join(self._path, name), 'r') as fp:
            return json.load(name)

    def store_json(self, name, data):
        with open(os.path.join(self._path, name), 'w+') as fp:
            return json.dump(data, fp)

    def set_variable(self, key, value):
        """Set the shared varialbe

        Args:
            key (str): Variable key
            value: The value of the variable
        """
        try:
            with open(self._shared_json_file, 'r') as storage:
                data = json.loads(storage.read())
            with open(self._shared_json_file, 'w') as storage:
                data[key] = value
                json.dump(data, storage)
        except FileNotFoundError:
            with open(self._shared_json_file, 'w+') as storage:
                data = {key: value}
                json.dump(data, storage)

    def get_variable(self, key):
        """Get the value of some variable

        Args:
            key (str): Variable key

        Returns:
            The value of the variable.
        """
        try:
            with open(self._shared_json_file, 'r') as storage:
                data = json.load(storage)
                return data.get(key)
        except FileNotFoundError as error:
            return None

    def purge(self):
        """
        Purge all shared data
        """
        files = glob.glob(os.path.join(self._path, '_shared_*'))
        for f in files:
            os.remove(f)



class Pipe:
    """Base class for all pipes. Provides utitilfdfites to work with configuration, validation etc.

    Attributes:
        variables (dict): Dictionary containing the pipes variables.
        schema (dict): Dictionary with the pipe parameters shema in the cerberus format.
        env (dict): Dict-like object conitining pipe parameters. This is usually the environment variables that 
            you get from os.environ

    Args:
        pipe_metadata (dict): Dictionary containing the pipe metadata
        schema (dict): Shema for pipe variables.
        
    Pipe variables validation
        Pip variables validation is done at the time of initializing a pipe. The environment variables are
        validated against the schema provided. See https://docs.python-cerberus.org/en/stable/ for more 
        details on how to specify schemas.

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

    def __init__(self, pipe_metadata=None, schema=None, env=None):
        if pipe_metadata is None:
            pipe_metadata = {}
        if env is None:
            self.env = os.environ.copy()
        else:
            self.env = env

        self.metadata = pipe_metadata

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
        env = {key:yaml.safe_load(value) for key, value in self.env.items() if key in schema}

        for key, key_schema in schema.items():
            if key_schema.get('type') == 'list':
                env[key] = ArrayVariable(key, self.env)

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
