import json
from functools import reduce
from operator import getitem
from pprint import pprint

import pkg_resources

from argus_cli.arguments import parse_arguments, Module, Provider, Command
from argus_cli.helpers.formatting import to_caterpillar_case
from argus_cli.helpers.log import log


def import_external_plugins(entry_point_name: str):
    """Import other plugins that are installed on the system.

    The implementation is done with reference to this python guide:
    https://packaging.python.org/guides/creating-and-discovering-plugins/#using-package-metadata

    TODO: Investigate a better placement for loading these external plugins.
    """
    return {
        entry_point.name: entry_point.load()
        for entry_point in pkg_resources.iter_entry_points(entry_point_name)
    }


def run(func: callable = None, argv: list = None):
    """Will run the given command or module with commandline arguments

    Works with functions that have been registered with:
        register_command()
    Or without any arguments when a module has been initialized with:
        create_module()

    :param func: A function that has been registered.
    :raises ValueError: When the given function is not registered.
    """
    command, arguments = parse_arguments(func, argv)

    log.debug("Running command \"{}\"".format(command))
    result = command(**arguments)

    if isinstance(result, dict):
        print(json.dumps(result, indent=2))
    elif result:
        pprint(result)


def create_module(providers: list = None) -> Module:
    """Set up for running a set of commands in a suite.

    Technical overview:
        Creates the commands module in the argument handler.
        This has to be created before any commands are registered.

    :param providers: All providers that this module requires to run.
    :param entry_point: The name of the entry_point of external plugins.
    """
    if providers is None:
        providers = []

    log.info("Setting up module for commands")
    module = Module(providers=[provider._provider for provider in providers])

    return module


def register_command(
        alias: str = None,
        extending: tuple = None,
        module: Module = None,
        providers: list = None,
) -> callable:
    """Marks the given function as a command.

    Allows for calling the function on the commandline.
    Will also automatically add the module's providers to the command.

    :param alias: If the user wants a custom name on the plugin
    :param extending: A existing plugin to extend
    :param module: The base module to register against. If None it will register against the base module.
    :param providers: List of Providers that are required to call the function.
    """
    extending = (extending,) if isinstance(extending, str) else extending
    providers = providers or []
    base_module = module

    def decorate(func):
        # Rename all plugins and commands to caterpillar-case-format to conform to common cli naming.
        plugin_name = tuple(map(to_caterpillar_case, extending or (func.__module__,)))
        command_name = to_caterpillar_case(alias or func.__name__)

        log.debug("Registering command \"%s\" in plugin \"%s\""
                  % (command_name, "/".join(plugin_name)))

        if base_module is not None:
            sub_module = reduce(getitem, plugin_name, base_module)

            command = Command(command_name, func, sub_module, providers=providers)
            sub_module[command_name] = command
        else:
            command = Command(command_name, func, providers=providers)

        # TODO: Should probably return the command in stead.
        func._command = command

        return func

    return decorate


def register_provider(name: str = None) -> callable:
    """Marks the given function as a provider.

    Providers allow extra functionallity to be executed before another command.

    :param name: Alternative name for the module
    """
    def decorate(func):
        provider_name = to_caterpillar_case(name or func.__name__)

        log.debug("Registering provider \"{}\"".format(name))
        func._provider = Provider(name, func)

        return func

    return decorate
