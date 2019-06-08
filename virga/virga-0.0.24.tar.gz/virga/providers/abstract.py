import abc
import json

import logging
import re

import datetime
import sys
import unicodedata
import os
import jmespath
import yaml


ERROR = 40
SUCCESS = 20


class AbstractProvider:
    """
    Abstract Provider class.

    This class can be used for creating concrete classes representing a provider.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, args: any):  # NOQA
        self.args = args
        self.tests = None
        self.definitions_path = None
        self._logger = None
        self._definitions = None

    def set_tests(self, tests: dict):
        """Set the test as separate process for making the class generic."""
        self.tests = tests

    @abc.abstractmethod
    def action(self):
        """Entry point for the battery of tests."""
        raise NotImplementedError('Implement action method')

    @abc.abstractmethod
    def lookup(self, section: str, identifier: str, resource_id: str) -> str:
        """
        Implement the _lookup function for searching resources outside the test scope.

        The sentence is: "look in the section for the resource with identifier == resource_id".

            _lookup(subnets, name, my-subnet)

        The object target of the _lookup doesn't need to be searched for actual tests on itself.

        :param section: The section where the resource should belong
        :param identifier: Resource identifier
        :param resource_id: Resource ID

        :return: The resource selected

        :raises VirgaException: If the resource is not found
        """
        raise NotImplementedError('Implement lookup method')

    @abc.abstractmethod
    def sample(self, resource_type: str, resource_id: str):
        """Stub for obtaining resource samples."""
        raise NotImplementedError('Implement sample method')

    def get_definitions_path(self) -> str:
        """Workaround for having an abstract property."""
        if self.definitions_path is None:
            raise NotImplementedError('Implement definition_file property')
        return self.definitions_path

    def read_definitions(self) -> dict:
        """Read the definitions."""
        definitions_path = self.get_definitions_path()
        if self.args.definitions is not None:
            definitions_path = self.args.definitions
        definitions = {}
        for item in [x for x in os.listdir(definitions_path) if x.endswith('.yaml')]:
            with open(os.path.join(definitions_path, item)) as definition:
                definitions.update(yaml.full_load(definition))
        return definitions

    @property
    def logger(self):
        """Logger property."""
        if self._logger is None:
            self._logger = self.set_logger(self.args)
        return self._logger

    @property
    def definitions(self):
        """Definition property."""
        if self._definitions is None:
            self._definitions = self.read_definitions()
        return self._definitions

    @staticmethod
    def set_logger(args: any):
        """
        Set the logger.

        :param args: Args from the command line
        :return: Instantiated logger
        """
        logging.addLevelName(SUCCESS, 'SUCCESS')
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')

        log_level = logging.INFO
        # If the arg had the debug flag set
        if args.debug:
            log_level = logging.DEBUG
        # If the arg had the silent flag set accept only critical
        if args.silent:
            log_level = logging.CRITICAL

        if args.logfile is not None:
            handler = logging.FileHandler(args.logfile)
        else:
            handler = logging.StreamHandler()
        handler.setLevel(log_level)
        handler.setFormatter(formatter)

        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)
        logger.addHandler(handler)
        return logger

    def logs(self, messages: list):
        """
        Log a list of messages.

        Outcome format
        {
            'level':   int
            'message': 'string'
        }

        :param messages: List of outcome dictionaries
        """
        for message in messages:
            self.logger.log(message.get('level', logging.CRITICAL), message.get('message', 'No message'))

    def flatten(self, data: any) -> list:
        """
        Flatten and return the list of lists of lists ... of data.

        :param data: Deep nested list of data
        :return: Flattened list of data
        """
        if not isinstance(data, list):
            data = [data]
        result = []
        for item in data:
            if not isinstance(item, list):
                result.append(item)
            else:
                result.extend(self.flatten(item))
        return result

    def outcome(self, result: any) -> bool:
        """
        Check every possible outcome from the query.

        :param result: Result of the query
        :return: True if the test has been successful, False otherwise
        """
        if result is None:
            return False
        result = self.flatten(result)
        len_result = len(result)
        if len_result == 0:
            return False
        if next((x for x in result if x is not None), None) is None:
            return False
        if not any(result):
            return False
        return True

    def _lookup(self, test: str) -> str:
        """
        Find and substitute the lookup value from the test string if any.

        Call the implemented method lookup for getting the actual ID and substitute the value before the query.

        :param test: Test string
        :return: The test string modified
        """
        result = test
        for group in re.findall(r'_lookup\(([\w\s\'_,-]*)\)', test):
            parameters = [x.strip(' \'') for x in group.split(',')]
            result = result.replace('_lookup(%s)' % group, self.lookup(*parameters))
        return result

    def output(self, resource: dict, resource_id: str):
        """
        Save the resource in a JSON file.

        If the arg -output is set, dump on file the result of the query in JSON format.
        It is only for testing purposes.

        :param resource: Resource to dump
        :param resource_id: Resource ID
        """
        def slugify(value, allow_unicode=False):
            """Thanks Django (https://www.djangoproject.com/) always inspiring."""
            value = str(value)
            if allow_unicode:
                value = unicodedata.normalize('NFKC', value)
            else:
                value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
            value = re.sub(r'[^\w\s-]', '', value).strip().lower()
            return re.sub(r'[-\s]+', '-', value)

        def handler(obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            return obj
        if self.args.output is not None:
            with open('%s/%s.json' % (self.args.output, slugify(resource_id)), 'w') as p_file:
                json.dump(resource, p_file, indent=2, default=handler)

    def assertion(self, test: str, context: str, resource: dict, resource_id: str) -> dict:
        """
        The actual query.

        Action performed:
        - call the `output` method
        - lookup the lookup word
        - search the resource for the test
        - return the outcome

        :param test: The test to perform
        :param context: Label of the section
        :param resource: The resource to analyse
        :param resource_id: The resource ID
        :return: The outcome
        """
        # output call at this point is a compromise for avoiding circular dependencies
        self.output(resource, resource_id)
        test = self._lookup(test)
        result = jmespath.search(test, resource)
        success = self.outcome(result)
        test_message = '%s: %s eval %s == %s' % (resource_id, test, str(result), success)
        self.logger.debug(test_message)

        message = 'Context: %(context)s - ID: %(resource)s - Test: %(test)s'

        return {
            'message': message % dict(context=context, resource=resource_id, test=test),
            'debug': resource,
            'success': success,
            'level': SUCCESS if success else logging.ERROR,
        }

    @staticmethod
    def result(messages: list):
        """
        Accept in input the message list and if any of the tests fails, the app exits with an error.

        The message is a dictionary having the key 'success' containing a boolean.

        :param messages: List of messages.
        """
        num_errors = len([x for x in messages if not x.get('success', False)])
        if num_errors > 0:
            message_error = 'is an error' if num_errors == 1 else 'are %d errors' % num_errors
            sys.stderr.write('There %s on %s tests.\n' % (message_error, len(messages)))
            sys.exit(1)
