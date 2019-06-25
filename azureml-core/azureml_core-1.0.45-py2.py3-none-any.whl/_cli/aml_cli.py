# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse
import collections
import importlib
import sys
import json

from azureml._cli import abstract_subgroup

# A named tuple to store a parent parser, its add_subparser_handle and a subgroup while performing
# the breadth-first search over packages to register all commands.
# add_subparser_handle is obtained by calling parser.add_subparsers(), and for a parser add_subparsers()
# function cannot be called multiple times, so we need to call it once and maintain a handle to it.
# subgroup is an object of a derived class of AbstractSubGroup.
SubgroupParserInfo = collections.namedtuple("SubgroupParserInfo", "parent_parser add_subparser_handle subgroup")

# Named tuple that stores a subgroup and the the partial command name till the subgroup.
SubgroupCommandNameInfo = collections.namedtuple("SubgroupCommandNameInfo", "subgroup partial_command_name")


# Environment variable to indicate that the azureml._cli is in use.
# Mainly used for output formatting. azureml._cli returns JSON formatted outputs while
# az CLI can return non JSON outputs for pretty printing for users. Also used for some
# options that are only present in azureml._cli and not in az ml CLI.

# This env variable is here and not in azureml._base_sdk_common.base_sdk_common.py because
# azureml._base_sdk_common.base_sdk_common.py has high importing latency, which will slow down the azureml._cli
AZUREML_CLI_IN_USE = None


class AmlCli(abstract_subgroup.AbstractSubGroup):
    def get_subgroup_name(self):
        """Returns the name of the subgroup.
        This name will be used in the cli command."""
        return "azureml._cli"

    def get_subgroup_title(self):
        """Returns the subgroup title as string. Title is just for informative purposes, not related
        to the command syntax or options. This is used in the help option for the subgroup."""
        return "azureml._cli commands"

    def get_nested_subgroups(self):
        """Returns sub-groups of this sub-group."""
        return super(AmlCli, self).compute_nested_subgroups(__package__)

    def get_commands(self, for_azure_cli=False):
        """ Returns commands associated at this sub-group level."""
        from azureml._cli.cli_command import CliCommand
        return [] if for_azure_cli else [
            CliCommand(
                "login",
                "Interactive Login",
                [],
                "azureml._base_sdk_common.common#perform_interactive_login")
        ]


def _add_arguments_to_command_subparser(command_subparser, argument_list):
    """Adds arguments related to a command to its subparser.
    command_subparser is the subparser for the command.
    argument_list is a list of objects of Argument class."""

    if argument_list is None:
        return

    for argument_obj in argument_list:
        # Only adding those arguments that are not None, so that the unspecified arguments take their subparser default
        # values, and we don't have to deal with default values.

        # Empty positional arguments give exceptions, so we have to check if short form or long form argument is ""
        positional_argument_list = []
        if len(argument_obj.short_form) > 0:
            positional_argument_list.append(argument_obj.short_form)
        if len(argument_obj.long_form) > 0:
            positional_argument_list = positional_argument_list + argument_obj.long_form

        command_subparser.add_argument(*positional_argument_list, **argument_obj.get_key_based_arguments_as_dict())


def _get_command_function_object(function_path):
    """ Returns a function object based on the supplied function name. The function
    name is assumed to be of module_name#funciton_name format, where module_name should
    be resolvable from sys.path."""
    assert len(function_path) > 0, "Invalid function name supplied={0}".format(function_path)

    split_list = function_path.split("#")
    assert len(split_list) == 2, "Invalid function name supplied={0}".format(function_path)
    module_object = importlib.import_module(split_list[0])
    function_object = getattr(module_object, split_list[1])
    return function_object


def _register_subgroups_and_commands(root_parser):
    """Performs a breadth-first search over the subgroups package structure and registers corresponding subparsers
    and commands."""
    aml_cli = AmlCli()
    subgroups_list = [SubgroupParserInfo(root_parser, root_parser.add_subparsers(
        help=aml_cli.get_subgroup_name() + " sub-commands help"), aml_cli)]

    while len(subgroups_list) > 0:
        temp_subgroup_list = []
        for subgroup_parser_object in subgroups_list:

            # Registering subparsers for the commands first.
            commands_at_current_subgroup = subgroup_parser_object.subgroup.get_commands()
            for command_obj in commands_at_current_subgroup:
                command_subparser = subgroup_parser_object.add_subparser_handle.add_parser(
                    command_obj.get_command_name(), help=command_obj.get_command_title())
                _add_arguments_to_command_subparser(command_subparser, command_obj.get_command_arguments())

                # Setting the command handler function_path here.
                # Only putting the function path here, we are not importing the module and getting
                # a function object here because that is a slow process, as we only want to
                # do that on a command execution and not when a user is just browsing packages using -h option,
                # which will be fast if we delay loading modules on an actual command.
                command_subparser.set_defaults(function_path=command_obj.get_handler_function_path())

                command_subparser.set_defaults(cli_to_function_args=command_obj.get_cli_to_function_arg_map())
                # We don't need to add a subparser to command_subparser, as it is a command.

            # Registering subparsers for the subparsers at this level now.
            subgroups_at_current_subgroup = subgroup_parser_object.subgroup.get_nested_subgroups()
            for subgroup_obj in subgroups_at_current_subgroup:
                subgroup_subparser = subgroup_parser_object.add_subparser_handle.add_parser(
                    subgroup_obj.get_subgroup_name(), help=subgroup_obj.get_subgroup_title())

                temp_subgroup_list.append(SubgroupParserInfo(subgroup_subparser, subgroup_subparser.add_subparsers(
                    help=subgroup_obj.get_subgroup_name() + " sub-command help"), subgroup_obj))
        subgroups_list = temp_subgroup_list


# A dictionary that stores <full_command_name, CliCommand> tuple.
# This dictionary is populated in load_command_table_azurecli
# and is used to register arguments for a command in load_arguments
_azure_command_dict = {}


def load_azurecli_help(helps):
    """
    Performs a bread-first search over the azureml._cli package structure and loads all the commands
    in az_command_loader's command table.

    This function doesn't register commands' arguments.
    Those are registered using the load_arguments function when an actual command is invoked from the
    command line.

    :param az_command_loader:
    :type az_command_loader: MachineLearningCommandsLoader, which extends from AzCommandsLoader
    :param _: We don't use this argument.
    :return: Returns none, as the function directly modifies az_command_loader's command table.
    """

    # Performing azure cli related imports.
    # Note: These import are time consuming, so we are performing them here instead of putting
    # them on the top of this file and slowing down azureml._cli

    top_level_command_name = "ml"
    aml_cli = AmlCli()
    subgroups_list = [SubgroupCommandNameInfo(aml_cli, top_level_command_name)]
    while len(subgroups_list) > 0:
        temp_subgroup_list = []
        for subgroup_object in subgroups_list:
            # We don't register flighting commands with az CLI.
            if not subgroup_object.subgroup.register_with_azure_cli():
                continue

            # Register the help for the subgroup
            helps[subgroup_object.partial_command_name] = """
                type: group
                short-summary: {}
            """.format(subgroup_object.subgroup.get_subgroup_title())

            # Checking the subgroups for the current subgroup.
            for subgroup_obj in subgroup_object.subgroup.get_nested_subgroups():
                temp_subgroup_list.append(SubgroupCommandNameInfo(
                    subgroup_obj, subgroup_object.partial_command_name + " " + subgroup_obj.get_subgroup_name()))
        subgroups_list = temp_subgroup_list


def load_command_table_azurecli(az_command_loader, _):
    """
    Performs a bread-first search over the azureml._cli package structure and loads all the commands
    in az_command_loader's command table.

    This function doesn't register commands' arguments.
    Those are registered using the load_arguments function when an actual command is invoked from the
    command line.

    :param az_command_loader:
    :type az_command_loader: MachineLearningCommandsLoader, which extends from AzCommandsLoader
    :param _: We don't use this argument.
    :return: Returns none, as the function directly modifies az_command_loader's command table.
    """

    # Performing azure cli related imports.
    # Note: These import are time consuming, so we are performing them here instead of putting
    # them on the top of this file and slowing down azureml._cli

    from azure.cli.core.commands import CliCommandType
    # Exception handler behavior from our sdk
    from azureml._base_sdk_common.cli_wrapper._common import cli_exception_handler

    top_level_command_name = "ml"
    aml_cli = AmlCli()
    subgroups_list = [SubgroupCommandNameInfo(aml_cli, top_level_command_name)]

    while len(subgroups_list) > 0:
        temp_subgroup_list = []
        for subgroup_object in subgroups_list:
            # We don't register flighting commands with az CLI.
            if not subgroup_object.subgroup.register_with_azure_cli():
                continue

            # Generating immediate commands at this subgroup first.
            commands_at_current_subgroup = subgroup_object.subgroup.get_commands(for_azure_cli=True)

            if len(commands_at_current_subgroup) > 0:
                parsed = commands_at_current_subgroup[0].get_handler_function_path().split("#")
                assert len(parsed) == 2, "Wrong function handler path format: {}".format(
                    commands_at_current_subgroup[0].get_handler_function_path())

                function_handler_module = parsed[0]

                # This is basically a command group in azure CLI.
                # TODO : This is a place to add our table transformer if needed.
                cli_command_type = CliCommandType(operations_tmpl=function_handler_module + "#{}")

                with az_command_loader.command_group(subgroup_object.partial_command_name, cli_command_type) as g:
                    for command_obj in commands_at_current_subgroup:
                        curr_parsed = command_obj.get_handler_function_path().split("#")
                        assert len(parsed) == 2, "Wrong function handler path format: {}".format(
                            command_obj.get_handler_function_path())

                        assert curr_parsed[0] == function_handler_module, \
                            "Handler functions for all CLI commands in subgroup = {} should be in " \
                            "module = {}. Found = {}".format(
                                subgroup_object.partial_command_name,
                                function_handler_module,
                                curr_parsed[0])

                        g.command(command_obj.get_command_name(), curr_parsed[1],
                                  exception_handler=cli_exception_handler)
                        full_command_name = subgroup_object.partial_command_name + " " + command_obj.get_command_name()

                        # This is needed to disable function signature scraping by az cli
                        az_command_loader.command_table[full_command_name].arguments_loader = lambda: []
                        # We override the command description with our description.
                        az_command_loader.command_table[full_command_name].description = command_obj.get_command_title

                        # Adding an entry in the dictionary that will be used to register this command's arguments.
                        full_command_name = subgroup_object.partial_command_name + " " + command_obj.get_command_name()
                        _azure_command_dict[full_command_name] = command_obj

            # Checking the subgroups for the current subgroup.
            subgroups_at_current_subgroup = subgroup_object.subgroup.get_nested_subgroups()
            for subgroup_obj in subgroups_at_current_subgroup:
                temp_subgroup_list.append(SubgroupCommandNameInfo(
                    subgroup_obj, subgroup_object.partial_command_name + " " + subgroup_obj.get_subgroup_name()))
        subgroups_list = temp_subgroup_list


def load_arguments(az_command_loader, current_command):
    """
    This function loads arguments for current_command using az_command_loader.

    This function only loads arguments for current_command.
    Unlike az CLI codebase, this function doesn't load arguments of all commands,
    which improves the performance.

    :param az_command_loader:
    :type az_command_loader: MachineLearningCommandsLoader, which extends from AzCommandsLoader
    :param current_command: The current command name.
    :type current_command: str
    :return: Returns none, as the function directly modifies az_command_loader's command table.
    """

    if current_command not in _azure_command_dict:
        # This is not a azureml._cli command, it is some other command, so this function just
        # returns.
        return

    # TODO: Azure CLI also has a lot of fancy features that we are not using now,
    # but might want to use those some time.
    with az_command_loader.argument_context(current_command) as c:
        # Now registering each argument.
        for argument_obj in _azure_command_dict[current_command].get_command_arguments():
            # Only adding those arguments that are not None, so that the unspecified arguments
            # take their subparser default values, and we don't have to deal with default values.

            # Empty positional arguments give exceptions, so we have to check if short form or long
            # form argument is ""
            positional_argument_list = []
            if len(argument_obj.short_form) > 0:
                positional_argument_list.append(argument_obj.short_form)

            if len(argument_obj.long_form) > 0:
                positional_argument_list = positional_argument_list + argument_obj.long_form

            argument_name = argument_obj.function_arg_name

            arguments_dict = argument_obj.get_key_based_arguments_as_dict()

            # Adding "options_list" key, which is required by Azure CLI
            arguments_dict["options_list"] = positional_argument_list
            # Use extra instead of argument in conjunction with the empty
            # lambda to get the arguments flowing through
            c.extra(argument_name, **arguments_dict)

            # Adding these also to add back the "metadata" that we didn't register by overriding the lambda.
            if argument_obj.positional_argument:
                c.positional(argument_name, **arguments_dict)
            else:
                c.argument(argument_name, **arguments_dict)


def _to_camel_case(snake_str):
    components = snake_str.split('_')
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + "".join(x.title() for x in components[1:])


def _process_single_return_object(return_object):
    from msrest.serialization import Model
    if isinstance(return_object, Model):
        object_dict = return_object.as_dict()
        return json.dumps({_to_camel_case(k): v for k, v in object_dict.items()}, indent=4, sort_keys=True)
    elif isinstance(return_object, dict):
        return json.dumps(return_object, indent=4, sort_keys=True)
    else:
        sys.exit("CLIError: Unsupported command output type: {}".format(type(return_object)))


class dummy(object):
    def __enter__(self):
        pass

    def __exit__(self, *args):
        pass


def _configure_debugging(debug_mode, func_name):
    if debug_mode:
        # Turn on diagnostics
        from azureml.core import diagnostic_log
        return diagnostic_log(context_name=func_name)
    else:
        return dummy()


def start_cli():
    """ This function is called by __main__.py to start the azureml._cli"""

    global AZUREML_CLI_IN_USE
    AZUREML_CLI_IN_USE = True

    parser = argparse.ArgumentParser(description="AzureML-specific cli")
    parser.add_argument("--debug", action="store_true", dest="debug")
    _register_subgroups_and_commands(parser)

    options = parser.parse_args()
    options_dict = vars(options)

    debug_mode = options_dict.pop('debug', False)

    # If there is a function specified to handle a cli command, then function_path is a key in the returned options.
    if "function_path" in options_dict:
        with _configure_debugging(debug_mode, options_dict["function_path"]):
            function_object = _get_command_function_object(options_dict["function_path"])
            cli_to_function_arg_map = options_dict["cli_to_function_args"]

            # Run the appropriate command handler function
            filter_function_arguments = {}

            for arg_name, arg_value in options_dict.items():
                if arg_name in ["function_path", "cli_to_function_args"]:
                    continue

                function_arg_name = cli_to_function_arg_map[arg_name]
                filter_function_arguments[function_arg_name] = arg_value

            try:
                # Calling the function to handle the command.
                # Similar to azure.cli, we just print whatever we get in return.

                # All function arguments in python are treated as both positional and keyword based.
                # So just unwrapping the dictionary here works irrespective of the order of
                # positional arguments in the handler function.

                cmd_output = function_object(**filter_function_arguments)

                # TODO: This is mainly for the project system commands.
                # This code needs to move to project system so the CLIs always get back a dictionary, rather
                # than arbitrary class objects.
                from collections import Iterator
                if cmd_output:
                    if isinstance(cmd_output, (list, Iterator)):
                        for element in cmd_output:
                            print(_process_single_return_object(element))
                    else:
                        print(_process_single_return_object(cmd_output))
            except Exception as e:
                sys.exit(e)
