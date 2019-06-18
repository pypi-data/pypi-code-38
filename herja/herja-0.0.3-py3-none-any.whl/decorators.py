#!python3
"""This file is designed to provide decorators for other files."""


import argparse
import inspect
import logging
import os
import shlex
import sys

from functools import wraps


#
#   Function Decorators
#

def args2keywords(function):
    """
    Wrap a function such that is converts given NameSpace objects into keywords.

    :param function: the decorated function that requires keywords
    :return: a wrapped function that accepts args
    """
    @wraps(function)
    def wrapper(args, **kwargs):
        kwargs.update(**vars(args))
        return function(**kwargs)
    return wrapper


#
#   Argument Intercept Decorators
#

class ArgumentIntercept:
    """Parse the arguments given to the decorated function and pass the resulting NameSpace."""

    # overwrite this in children
    main_class = False

    def __init__(self):
        """Assign the tuples to self, to be passed in upon calling."""
        self.parser = argparse.ArgumentParser()

    def __call__(self, function):
        """Intercept the given arguments and pass them to the parser."""
        @wraps(function)
        def wrapper(arguments):

            if (arguments is None) or isinstance(arguments, list):
                args = self.parser.parse_args(arguments)

            elif isinstance(arguments, (bytes, str)):
                args = self.parser.parse_args(shlex.split(arguments))

            else:
                raise RuntimeError('Unhandled arguments type: "{}"'.format(type(arguments)))

            # logging should be configured if this is a main class and we are inside '__main__'.
            if self.main_class:

                level = logging.NOTSET
                logging.basicConfig(
                    format='%(asctime)s [%(levelname)9s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=level
                )
                logging.debug('Logging level set to: %d', level)

            return function(args)

        # if the parent frame's __name__ is not __main__, this is not a "main" class
        if inspect.currentframe().f_back.f_globals['__name__'] != '__main__':
            self.main_class = False

        # return the function if this is not a main class
        if not self.main_class:
            return wrapper

        # call the decorated function and exit with the system code if possible.
        result = wrapper(None)
        if isinstance(result, int):
            sys.exit(result)
        sys.exit(0)


class Parse(ArgumentIntercept):
    """Parse the given arguments with CreateParser."""

    main_class = False

    def __init__(self, *tuples):
        """Add all of the arguments to the parser."""
        super(Parse, self).__init__()
        for args, kwargs in tuples:
            self.parser.add_argument(*args, **kwargs)


class ParseCommands(ArgumentIntercept):
    """Parse the given arguments with CreateParserCommands."""

    main_class = False

    def __init__(self, *command_tuples):
        """Add all of the subparsers to the parser."""
        super(ParseCommands, self).__init__()
        subparsers = self.parser.add_subparsers(dest='command')
        for cmd_name, cmd_help, tuples in command_tuples:
            option = subparsers.add_parser(cmd_name, help=cmd_help)
            for args, kwargs in tuples:
                option.add_argument(*args, **kwargs)


#
#   Main Decorators
#

class Main(Parse):
    """Parse and call the decorated function."""

    main_class = True


class MainCommands(ParseCommands):
    """ParseCommands and call the decorated function."""

    main_class = True


#
#   Require Class Decorators
#

class Require:
    """A decorator that raises a RuntimeError if any of the given args are not True."""

    def __init__(self, *args):
        """Ensure each argument given to this decorator evaluates to True with the function."""
        for arg in args:
            if not bool(arg):
                raise RuntimeError('Requirement failed: %r' % arg)

    def __call__(self, function):
        """Return the same function as was decorated."""
        return function


class RequireDirs:
    """A decorator that raises a RuntimeError if any of the given args are not directories."""

    def __init__(self, *args):
        """Ensure each argument given to this decorator evaluates to True with the function."""
        for arg in args:
            if not os.path.isdir(arg):
                raise RuntimeError('Directory not found: %r' % arg)

    def __call__(self, function):
        """Return the same function as was decorated."""
        return function


class RequireFiles:
    """A decorator that raises a RuntimeError if any of the given args are not files."""

    def __init__(self, *args):
        """Ensure each argument given to this decorator evaluates to True with the function."""
        for arg in args:
            if not os.path.isfile(arg):
                raise RuntimeError('File not found: %r' % arg)

    def __call__(self, function):
        """Return the same function as was decorated."""
        return function


@Main()
def main(args):
    """
    When this script is the main one executed, this function will be performed.

    :param args: a Namespace object
    :return: a system exit code
    """
    print(args)
    return 0
