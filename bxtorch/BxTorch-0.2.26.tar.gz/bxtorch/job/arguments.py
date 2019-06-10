#
#  job/arguments.py
#  bxtorch
#
#  Created by Oliver Borchert on May 15, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

from abc import ABC, abstractmethod
import argparse

class _Argument(ABC):
    """
    Base class for describing a specific type of argument for a job.
    """

    def __init__(self, identifier, default=None, allow_list=False, help=None):
        """
        Initializes a new argument according to the given parameters:

        Parameters:
        -----------
        - identifier: str
            The name of the argument. Set on the command line by 
            ``--identifier`` and can be accessed on the job with the
            ``.identifier`` property.
        - default: type, default: None
            The default value for the argument. If not given, the argument is
            assumed to be required.
        - allow_list: bool, default: False
            Determines whether the argument can be set multiple times, resulting
            in a list of values.
        - help: str, default: None
            A description of the argument.
        """
        self.identifier = identifier
        self.default = default
        self.allow_list = allow_list
        self.help = help

    def register_on(self, parser):
        """
        Adds the argument to the specified parser.

        Parameters:
        -----------
        - parser: argparse.ArgumentParser
            The parser to add the argument to.
        """
        kwargs = {
            'required': self.default is None,
            'default': self.default,
            'help': self.help, 
            'action': 'append' if isinstance(self.default, list) \
                      else self._action
        }

        if kwargs['action'] not in ('store_true', 'store_false'):
            kwargs['type'] = self._from_string

        parser.add_argument(f'--{self.identifier}', **kwargs)

    @property
    def _action(self):
        return 'store'

    @abstractmethod
    def _from_string(self, value):
        pass


class Boolean(_Argument):
    """
    Argument of type boolean. 
    
    Note:
    -----
    You may not provide a value on the command line. Setting a boolean argument
    (i.e. flag) simply inverts the default value.
    """

    @property
    def _action(self):
        return 'store_false' if self.default else 'store_true'

    def _from_string(self, value):
        raise argparse.ArgumentTypeError(
            'Invalid option for boolean argument.'
        )


class Integer(_Argument):
    """
    Argument of type integer.
    """

    def _from_string(self, value):
        return int(value)


class String(_Argument):
    """
    Argument of type string.
    """

    def _from_string(self, value):
        return value


class Float(_Argument):
    """
    Argument of type float.
    """

    def _from_string(self, value):
        return float(value)
