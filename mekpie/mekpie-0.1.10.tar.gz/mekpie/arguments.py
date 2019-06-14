import mekpie.debug    as debug
import mekpie.messages as messages

from .create      import command_new, command_init
from .definitions import Options, Option
from .cli         import panic, tell
from .util import (
    first,
    rest,
    tab,
    split,
    empty,
    underline,
)
from .compiler import (
    command_run,
    command_test,
    command_clean,
    command_build,
    command_debug,
    command_dist,
)

def command_help(cfg):
    tell(messages.usage, end='\n\n')

def command_version(cfg):
    tell(messages.version)

def pre_config_commands():
    return [
        command_help,
        command_version,
        command_new,
        command_init,
    ]

def available_options():
    return [
        flag('quiet',            ['-q', '--quiet']),
        flag('release',          ['-r', '--release']),
        flag('developer',        ['-d', '--developer']),
        flag('mode',             ['-m', '--mode'], 2),
        flag('changedir',        ['-c', '--changedir'], 2),
        command(command_help,    ['-h', '--help', 'help']),
        command(command_version, ['-V', '--version', 'version']),
        command(command_new,     ['new']),
        command(command_init,    ['init']),
        command(command_clean,   ['clean']),
        command(command_build,   ['build']),
        command(command_run,     ['run']),
        command(command_test,    ['test']),
        command(command_debug,   ['debug']),
        command(command_dist,    ['dist']),
    ]

def parse_arguments(args):
    argsall = args[:]
    options = Options()
    args, programargs = split(args, '--')
    options.programargs = programargs
    while not empty(args):
        arg = first(args)
        for option in available_options():
            if arg in option.names:
                option.handler(options, args[:option.nargs], argsall)
                args = args[option.nargs:] if option.nargs else []
                break
        else:
            argument_error(messages.unknown_argument, first(args), argsall)
    if options.mode:
        options.mode = first(options.mode)
    return options

def flag(name, aliases, nargs=1):

    def handle_flag(options, args, argsall):
        if options[name]:
            argument_error(messages.repeated_option.format(name), name, argsall)
        else:
            options[name] = rest(args) or True

    return Option(
        names   = aliases,
        nargs   = nargs,
        handler = handle_flag,
    )

def command(command, aliases):

    def handle_command(options, args, argsall):
        if options.command:
            argument_error(messages.too_many_arguments, command, argsall)
        else:
            options.commandargs = rest(args)
            options.command     = command

    return Option(
        names   = aliases,
        handler = handle_command,
    )

def argument_error(message, arg, args):
    args = ['mekpie'] + args
    panic(f'{message}\n{tab(underline(arg, args))}')