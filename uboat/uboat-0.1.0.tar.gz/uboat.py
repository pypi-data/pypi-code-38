__version__ = '0.1.0'

import argparse
from functools import wraps

# =============================================================================

class Flag:
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.kwargs = kwargs
    

class SubCommand:
    def __init__(self, name):
        self.name = name
        self.flags = []
        self.kwargs = {}
        self.func = None


class CommandManager:
    def __init__(self):
        self.flags = []
        self.config = {}
        self.sub_config = {}
        self.sub_commands = []


def flag(name, **kwargs):
    """Function acts like a wrapper for flag parameters that would be used
    inside of a ``argparse`` ``add_argument()`` call."""
    return Flag(name, **kwargs)


def add_flags(*args):
    """Registers command line flags with the CommandManager. Takes one or more
    :func:`flag` calls which are wrappers to the ``argparse`` 
    ``add_argument()`` method."""
    manager.flags.extend(args)


def configure(**kwargs):
    """Registers configuration parameters for the ``ArgumentParser``. All
    parameters passed to this method are sent through to the 
    ``ArgumentParser`` constructor."""
    manager.config = kwargs


def configure_subparser(**kwargs):
    """Registers configurtion parameters for the subparser created inside the
    ``ArgumentParser``. All parameters passed to this method are sent through
    to the ``add_suparsers()`` method on the ``ArgumentParser``."""
    manager.sub_config = kwargs


# -----------------------------------------------------------------------------
# Sub-command Parser
# -----------------------------------------------------------------------------

def process_arguments():
    """Method to be called to have the program parse the command line
    arguments and execute any sub-commands found there.
    """

    # create the parser and subparsers
    parser = argparse.ArgumentParser(**manager.config)
    subparser = parser.add_subparsers(**manager.sub_config)

    #import pudb; pudb.set_trace()

    # for each flag (for the command line, not for the sub-commands), add them
    # to the parser
    for flag in manager.flags:
        parser.add_argument(flag.name, **flag.kwargs)

    # for each cmd, register it with the parser
    for cmd in manager.sub_commands:
        # create the sub-parser
        cmd_parser = subparser.add_parser(cmd.name, **cmd.kwargs)

        # if there were flags defined for the sub-command, add them
        for flag in cmd.flags:
            cmd_parser.add_argument(flag.name, **flag.kwargs)

        # register the function to be called when the command is invoked
        cmd_parser.set_defaults(func=cmd.func)

    # everything should be registered and ready to go, call the actual parser
    args = parser.parse_args()

    # since this library is for sub-commands, we can assume you must give a
    # sub-command
    if not hasattr(args, 'func'):
        parser.print_help()
        exit()

    # execute the function associated with the command and then return the
    # argument Namespace from the parser
    args.func(args)
    return args


# -----------------------------------------------------------------------------
# Command Registration Decorator
# -----------------------------------------------------------------------------

def command(*decorator_args, **decorator_kwargs):
    """Decorator for registering new sub-commands. 

    Simplest case is to be called without parameters, registering a
    sub-command with the name of the function wrapped.

    .. code-block:: python

        @uboat.command
        def show(args):
            print('This is the "show" sub-command running')

    Alternatively, parameters can be passed to the decorator. Using a
    parameter ``name`` will override the method's name as the sub-command. One
    or more :func:`flag` methods can be passed in to configure flags or
    arguments for the sub-command. All parameters of the :func:`flag` call are
    passed through to the ``argparse`` ``add_argument()`` call. Parameters not
    wrapped in the :func:`flag` method are passed through to the creation of
    the subparser.

    .. code-block:: python

        @uboat.command(
            flag('packages', nargs='+', help='List of packages to add'), 
            name='install', help='Pretends to install something')
        def install_cmd(args):
            print('Installing:', ','.join(args.packages))
            print('Done')

    The above registers a sub-command called "install" (NB: `not`
    "install_cmd") which takes a parameter with one or more argument stored in
    "packages". This is the equivalent of the following ``argparse`` code:

    .. code-block:: python

        import argparse

        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        install_parser = subparsers.add_parser('install', 
            help='Pretends to install something')
        install_parser.ad_argument('packages', nargs='+', 
            help='List of packages to add')
        install_parser.set_defaults(func=install_cmd)

        args = parser.parse_args()
        args.func(args)

    """
    called_with_parms = True
    if len(decorator_args) == 1 and callable(decorator_args[0]):
        # decorator can be of form "@smear", or "@smear('stuff')"
        # in the first case there will only one argument and it will be
        # the wrapped function
        called_with_parms = False

    def decorator(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)

        # register the command with the uboat singleton
        cmd = SubCommand(method.__name__)

        if 'name' in decorator_kwargs:
            # user provided an alternate name, use that and remove it from
            # the calling dict
            cmd.name = decorator_kwargs['name']
            del decorator_kwargs['name']

        if called_with_parms:
            # only add the decorator_args if this was called with parameters,
            # otherwise decorator_args contains the calling method
            cmd.flags = decorator_args

        cmd.kwargs = decorator_kwargs
        cmd.func = wrapper

        manager.sub_commands.append(cmd)
        return wrapper

    #if len(decorator_args) == 1 and callable(decorator_args[0]):
    if not called_with_parms:
        return decorator(*decorator_args, **decorator_kwargs)

    return decorator

# =============================================================================

manager = CommandManager()
