import argparse
import collections
import inspect
import re
import sys
from datetime import datetime
from functools import wraps, partial
from pydoc import locate

import dateparser
import yaml

from argus_cli.helpers.formatting import to_caterpillar_case
from argus_cli.helpers.log import log


def parse_function(function: callable) -> dict:
    """Parses a functions parameters and help-text from its docstring and annotations.

    :param function: A function
    :return: The description and arguments (in order) for the function
    """
    parsed = {}

    log.debug("Parsing arguments and docstring for %s..." % function.__name__)

    parsed["arguments"] = _parse_parameters(function)

    if function.__doc__:
        parsed = _parse_docstring(function, parsed)

    return parsed


def _parse_parameter(name: str, parameter: inspect.Parameter) -> dict:
    """Parses a parameter"""
    log.debug("Parsing parameter %s" % name)

    options = {}
    if parameter.kind is parameter.VAR_POSITIONAL:
        # This is necessary due to the nargs argument would always be
        # overwritten if the parameter wasn't a vararg.
        options["number_of_arguments"] = "*"
    if parameter.default is not parameter.empty:
        # Same reasoning as above, would overwrite when it shouldn't
        options["default"] = parameter.default

    return get_argument_creator(
        # An empty annotation is "empty" in stead of None...
        parameter.annotation if parameter.annotation is not inspect.Parameter.empty else None
    )(
        name=name,
        required=parameter.default is parameter.empty or parameter.kind is inspect.Parameter.VAR_POSITIONAL,
        **options
    )


def _parse_parameters(function: callable) -> dict:
    """Parses a functions parameters.

    :param function: The function to parse
    :returns: All arguments, ready to pass to argparse
    """
    arguments = collections.OrderedDict()
    signature = inspect.signature(function)

    log.debug("%s arguments: %s" % (function.__name__, signature))

    for name, parameter in signature.parameters.items():
        if parameter.kind == inspect.Parameter.VAR_KEYWORD:
            # **kwargs Have to be defined in docstrings
            log.debug("**%s argument ignored. kwargs are added from the docstring." % name)
            continue
        arguments[name] = _parse_parameter(name, parameter)

    log.debug("%s: Registered commands from signature:\n\t%s" % (function.__name__, arguments))
    return arguments


def _parse_docstring(function: callable, parsed: dict) -> dict:
    """Parses a function's docstring for more info about it and it's parameters.

    :param function: The function to parse
    :param parsed: Existing arguments for the function
    :return: Short description, Long description and more argument info
    """

    def _parse_docstring_aliases(docstring: str) -> dict:
        """Parses the docstring for parameter aliases

        :param docstring: The docstring to parse
        """
        #: Gets aliases for a parameter
        alias_regex = re.compile(r":alias (?P<name>\w+):\s+(?P<aliases>.*)")

        for name, aliases in alias_regex.findall(docstring):
            if name not in parsed["arguments"]:
                raise NameError("%s is not an argument. An argument has to exist to be aliased." % name)
            for alias in aliases.split(","):
                parsed["arguments"][name]["names"].append(to_caterpillar_case(alias.strip()))

        return parsed["arguments"]

    def _parse_docstring_parameters(docstring: str) -> dict:
        """Parses the docstring for extra info about parameters.

        :param docstring: The docstring to parse
        """
        #: Gets doc for a parameter. `argument_type` is optional.
        param_regex = re.compile(r":param\s?(?P<argument_type>\w*) (?P<name>\w+): (?P<doc>.*)")

        for argument_type, name, doc in param_regex.findall(docstring):
            if argument_type and parsed["arguments"].get("type"):
                log.warning(
                    "Argument %s's type is set in both function annotation and docstring. Prioritizing docstring." % name
                )

            new_argument = get_argument_creator(
                locate(argument_type) if argument_type else None,
                False
            )(
                # TODO: This should be looked a bit into.
                parsed["arguments"].get(name, {}).get("names", [name])[0],
                required=None if parsed["arguments"].get(name) else False
            )
            argument = parsed["arguments"].setdefault(name, new_argument)

            if argument is not new_argument:
                argument.update(new_argument)
            if "type" not in argument and argument_type:
                # Special case to handle when there is no type from before
                argument["type"] = _str_or_file

            argument["help"] = doc

        return parsed["arguments"]

    # Escape all % { and } so argparse doesnt crash when trying to format the string
    docstring = function.__doc__.replace("{", "{{").replace("}", "}}").replace("%", "%%").split("\n", 1)

    parsed["help"] = docstring[0].strip()

    if len(docstring) <= 1:
        return parsed

    description = docstring[1]

    match = re.compile(r":(?:param|alias)").search(description)
    arguments_part = description[match.start():] if match else None
    parsed["description"] = (description[:match.start()] if match else description).strip()

    if arguments_part:
        parsed["arguments"] = _parse_docstring_parameters(arguments_part)
        parsed["arguments"] = _parse_docstring_aliases(arguments_part)

    return parsed


def _create_argument(
        name: str,
        required: bool = None,
        type: callable = None,
        default: object = None,
        number_of_arguments: str = None,
        action: str = None,
        choices: list = None,
) -> dict:
    nick_name = to_caterpillar_case(name) if required is False else name
    if default is True:
        nick_name = "no-%s" % nick_name if len(nick_name) > 1 else nick_name

    argument = {"names": [nick_name]}

    if required is False:
        # Required can not be set for positionals, so we only set it if it's not required.
        argument["dest"] = name
        argument["required"] = False

    if default is not None:
        argument["default"] = default
    if number_of_arguments is not None:
        argument["nargs"] = number_of_arguments
    if action is not None:
        argument["action"] = action
    if choices is not None:
        argument["choices"] = choices
    if type is not None:
        argument["type"] = type

    return argument


@wraps(_create_argument)
def _handle_boolean(*args, **metadata):
    action = None

    if metadata.get("default") is True:
        action = "store_false"
    elif metadata.get("default") is False:
        action = "store_true"

    return _create_argument(
        *args,
        action=action,
        type=bool if not action else None,
        **metadata
    )


def get_argument_creator(argument_type: type, assume_list_type: bool = True) -> _create_argument:
    """Gets the correct create argument handler.

    This is necessary because some types needs special handling.

    :param argument_type: The type of the argument
    :param assume_list_type: If True, a list will automatically be assumed to be a string
    :returns: Argument creator function
    """
    if argument_type is sys.stdin:
        # This is a special case for stdin, where it's allowed to have specified parameter.
        # Normally the framework will parse instances of FileType just fine and accept stdin if the user uses "-".
        # See the argparse documentation on FileType.
        return partial(_create_argument, type=argparse.FileType('r'), default=sys.stdin, number_of_arguments="?")
    elif inspect.isclass(argument_type) and issubclass(argument_type, datetime):
        return partial(_create_argument, type=dateparser.parse)
    elif inspect.isclass(argument_type) and issubclass(argument_type, (list, tuple)):
        return partial(_create_argument, number_of_arguments="*", type=_str_or_file if assume_list_type else None)
    elif inspect.isclass(argument_type) and issubclass(argument_type, dict):
        return partial(_create_argument, type=yaml.safe_load)
    elif isinstance(argument_type, collections.Container) and not isinstance(argument_type, str):
        if any(isinstance(element, collections.Container) and not isinstance(element, str) for element in argument_type):
            raise ValueError("A list of choices can not have a nested iterable object.")
        return partial(_create_argument, choices=argument_type)
    elif isinstance(argument_type, bool) or argument_type is bool:
        return _handle_boolean
    elif argument_type is str:
        return partial(_create_argument, type=_str_or_file)
    elif argument_type is not None and not callable(argument_type):
        raise ValueError("Argument with type {} is not a valid argument type.".format(argument_type))
    else:
        return partial(_create_argument, type=argument_type)


def _str_or_file(argument):
    """Helper type to parse a string as a file.

    This is because of the implementation of @<file> didn't work as expected originally,
    and this might not be the best practice way to do a cli application.
    """
    if argument.startswith('@'):
        with open(argument[1:], 'r') as f:
            output = "".join(f.readlines())
    else:
        output = argument

    return output
