import os
import importlib
import inspect
import sys
import textwrap

from fastr import exceptions
from fastr import version


def find_commands():
    cmd_dir = os.path.dirname(__file__)
    files = os.listdir(cmd_dir)
    files = [x[:-3] for x in files if x.endswith('.py') and not x.startswith('_')]

    return files


def get_command_module(command):
    command_module = importlib.import_module('fastr.utils.cmd.{}'.format(command))

    if not hasattr(command_module, 'get_parser') or not inspect.isfunction(getattr(command_module, 'get_parser')):
        raise exceptions.FastrAttributeError('Command modules should contain a "get_parser" function')

    if not hasattr(command_module, 'main') or not inspect.isfunction(getattr(command_module, 'main')):
        raise exceptions.FastrAttributeError('Command modules should contain a "main" function')

    return command_module


def print_help(commands=None):
    if commands is None:
        commands = find_commands()

    # Get length of longest command name
    max_name_length = max(len(x) for x in commands) + 4
    max_text_length = 80 - max_name_length

    help = []
    for command in sorted(commands):
        module = get_command_module(command)
        if hasattr(module.main, '__doc__'):
            doc_string = module.main.__doc__.strip().splitlines()[0]
            doc_string = textwrap.wrap(doc_string, width=max_text_length)
        else:
            doc_string = ['Undocumented territory']

        doc_string = ['{command:<{len}} {text}'.format(command=command if nr == 0 else '',
                                                       len=max_name_length,
                                                       text=text) for nr, text in enumerate(doc_string)]

        help.append('\n'.join(doc_string))

    command_help_list = '\n'.join(help)
    print ("""usage: fastr [-h] subcommand

subcommand:
  The sub command to use


List of sub commands:
{}""".format(command_help_list))


def main():
    # Get all files in utils following the bin_*.py name convention
    commands = find_commands()

    # Strip the first argument, this should be a sub command
    # and if it is not we will display the main help

    if len(sys.argv) < 2:
        print_help()
        return

    subcommand = sys.argv[1]

    if subcommand not in commands:
        print_help()
        return

    # Path sys.argv to look like "fastr subcommand" was one command
    sys.argv = ['{} {}'.format(sys.argv[0], subcommand)] + sys.argv[2:]

    module = get_command_module(subcommand)
    module.main()


def add_parser_doc_link(parser, filepath):
    cmd_name = os.path.splitext(os.path.basename(filepath))[0]
    parser.description = "{}\nMore information can be found at: https://fastr.readthedocs.io/en/{}/fastr.commandline.html#cmdline-{}".format(
        parser.description if parser.description else '',
        "develop" if version.not_default_branch else version.version,
        cmd_name
    )
    return parser
