from os      import curdir, chdir, curdir
from sys     import argv
from os.path import abspath

import mekpie.debug    as debug
import mekpie.messages as messages

from .cli         import panic, log
from .util        import first, rest, last, file_as_str, check_is_dir
from .config      import get_config
from .arguments   import parse_arguments, pre_config_commands
from .definitions import Options

def mekpie(options):
    root = abspath(curdir)
    if type(options) != type(Options()):
        panic(messages.api_no_options)
    prepare_for_command(options)
    perform_command(options)
    chdir(root)

def main(args=rest(argv)):
    try:
        debug.args = args
        mekpie(parse_arguments(args))
    except KeyboardInterrupt:
        print()

def prepare_for_command(options):
    if options.developer:
        debug.enable()
    if options.changedir:
        chdir(check_is_dir(first(options.changedir)))

def perform_command(options):
    command = options.command
    if command is None:
        panic(messages.no_command)
    elif command in pre_config_commands():
        command(log(options))
    else:
        config = get_config(options)
        command(log(config))