import sys

import argparse
from argparse import ArgumentParser
from collections import defaultdict, MutableMapping
from functools import reduce, partial
from operator import getitem

from argus_cli.parser import parse_function
from argus_cli.helpers.log import log


class _ModuleDefaultDict(defaultdict):
    """A defaultdict that is specialized for use with the Module class

    The key has to be passed to the module.
    The key isn't passed to the class in a normal defaultdict.
    """

    def __missing__(self, key):
        self[key] = self.default_factory(name=key)
        return self[key]


class _ModuleAction(argparse._SubParsersAction):
    """Stores the name of the plugin to a attribute on the namespace

    Will add the name of the module to the _modules attribute of the namespace.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        super().__call__(parser, namespace, values, option_string)
        try:
            namespace._modules.insert(0, values[0])
        except AttributeError:
            namespace._modules = [values[0]]


class Module(MutableMapping):
    """Storage for argument parsers.

    This is basically a dict with argparse support.
    """

    def __init__(self, name=None, module=None, providers=None):
        self.providers = providers or []

        provider_parsers = [provider.parser for provider in self.providers]
        if module:
            self.argument_parser = module.add_parser(name, parents=provider_parsers)
        else:
            # If there are no parent, then this is the root module
            self.argument_parser = ArgumentParser(parents=provider_parsers)

        self.subparser = self.argument_parser.add_subparsers(action=_ModuleAction)

        # Make sure that sub-modules automatically gets a parent
        self._dict = _ModuleDefaultDict(
            partial(Module, module=self.subparser, providers=providers)
        )

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        if key in self._dict and (
                not isinstance(value, Command)
                or value.function.__code__ != self._dict[key].function.__code__
        ):
            # Due to the fact that plugin.py loads every single file,
            # a command can be loaded twice. Thus we'll have to check the code object as well.
            raise KeyError("A function with the name {} already exists.".format(key))

        self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)


class Provider(object):
    """A function that provides some functionality to commands."""
    called = False

    def __init__(self, name, func, parents=None):
        self.name = name
        self.function = func
        self.parser = ArgumentParser(add_help=False, parents=parents or [])

        _register_arguments(self.parser, parse_function(func))

    def __call__(self, *args, **kwargs):
        # Make sure that the provider is only called ones.
        # TODO: Should look into how to solve this whole provider stuff in a better way.
        if self.called:
            return
        self.called = True

        return self.function(*args, **kwargs)


class Command(object):
    """A callable with an accompanying argument parser."""

    def __init__(self, name: str, func: callable, module: Module = None, providers: list = None):
        self.name = name
        self.function = func
        self.providers = (providers or [])
        if module is not None:
            self.providers.extend(module.providers)

        argparse_initializer = module.subparser.add_parser if module is not None else ArgumentParser
        self.argument_parser = argparse_initializer(
            name,
            parents=[provider.parser for provider in self.providers]
        )

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)


def _register_arguments(parser: ArgumentParser, metadata: dict):
    """Registers the arguments to the given argument parser.

    Used for lazy parsing of the commands.
    """
    parser.help = metadata.get("help")
    parser.description = metadata.get("description")

    for argument, options in metadata["arguments"].items():
        names = options.pop("names")

        if options.get("required") is False:
            prefixed_names = []
            for name in names:
                prefix = "-" if len(name) is 1 else "--"
                prefixed_names.append(prefix + name)
            names = prefixed_names
        elif len(names) > 1:
            log.warn("%s is a positional argument, and can thus not have an alias. Ignoring aliases." % names[0])
            names = [names[0]]

        # FIXME: Fix for ARGUSUSER-1747, but this doesn't seem the way its supposed to work.
        # Argparse doesn't accept BOTH action='store_true' AND a type keyword argument
        if options.get("action") == "store_true" or options.get("action") == "store_false":
            if options.get("type"):
                del options["type"]
        parser.add_argument(*names, **options)


def _error_or_help(parser):
    if any(keyword in sys.argv for keyword in ("--help", "-h")):
        parser.print_help()
        parser.exit()
    parser.error("Not enough arguments")


def _get_command_from_arguments(argv: list, module: Module):
    """Gets the command to execute based on arguments.

    This part skips the help-message, as we haven't parsed the command yet.
    """
    base_args = [arg for arg in argv if (arg != "--help" and arg != "-h")]
    _, base_args = parse_providers(base_args, module.providers)

    module_arguments, remaining_args = module.argument_parser.parse_known_args(base_args)
    if not hasattr(module_arguments, "_modules"):
        _error_or_help(module.argument_parser)

    command = reduce(getitem, module_arguments._modules, module)
    if not isinstance(command, Command):
        _error_or_help(command.argument_parser)

    # Because we're passing the remaining args around, we'll have to reintroduce the help message.
    if "--help" in argv or "-h" in argv:
        remaining_args.append("--help")

    return command, remaining_args


def parse_providers(argv: list, providers: list):
    """Parses and runs the given providers

    :returns: Remaining arguments.
    """
    provider_arguments = {}
    for provider in providers:
        args, argv = provider.parser.parse_known_args(argv)
        provider_arguments.update(vars(args))
        provider(**vars(args))

    return provider_arguments, argv


def _parse_command(argv: list, command: Command):
    """Gets arguments that can be passed to the callable command

    Also runs the providers that the command requires.

    NOTE:
        That we're running the providers from here might prove confusing.
        Should be looked into at some point.
    """
    provider_arguments, argv = parse_providers(argv, command.providers)
    arguments = vars(command.argument_parser.parse_args(argv))

    for arg in provider_arguments:
        del arguments[arg]

    return arguments


def parse_arguments(func: [Module, Command], argv: list = None) -> (callable, dict):
    """Two parts: Module args and command args

    :param func: A function with a
    :param argv: Arguments to parse. If none, sys.argv will be used.
    """
    # This can't be set as a default in the signature.
    # Seems like it isn't initialized when the module gets loaded.
    argv = sys.argv[1:] if argv is None else argv

    if hasattr(func, "_command"):
        func = func._command
        first_argument_parse = lambda argv, func: (func, argv)
    elif isinstance(func, Module):
        first_argument_parse = _get_command_from_arguments
    else:
        raise ValueError(
            "The first argument has to be a Module or a Command. Given {}".format(type(func))
        )

    # Grabs the correct command and removes the module arguments.
    command, remaining_args = first_argument_parse(argv, func)

    # Registering the metadata is done at a later point to not do unnecessary operations with _parse_function().
    # A single call to _parse_function() takes quite some time, so it's better to do it JIT.
    log.debug("Registering metadata for {}".format(command))
    _register_arguments(
        command.argument_parser,
        parse_function(command.function)
    )

    log.debug("Parsing command arguments")
    arguments = _parse_command(remaining_args, command)

    return command, arguments
