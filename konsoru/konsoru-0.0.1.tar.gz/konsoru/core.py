import os, re, sys
import argparse, shlex, inspect, atexit
import traceback, subprocess    # could potentially put them inside functions to hide them
from collections import UserDict

from . import config, exceptions, utils

if config.system != 'windows':
    # windows does not have readline module, so importing will result in crash
    import readline


# ------------------------------------------------
# helper functions
# ------------------------------------------------

def _shift(s, delim=None, trim=True):
    args = s.split(sep=delim, maxsplit=1)
    if len(args) == 0:
        first, rest = '', ''
    elif len(args) == 1:
        first, rest = args[0], ''
    else:
        first, rest = args[0], args[1]
    if trim:
        first, rest = first.strip(), rest.strip()
    return first, rest


def _extract_kwargs(func, param_name, exclude_list=()):
    kwargs_map = getattr(func, 'parameter', {})
    kwargs = kwargs_map.get(param_name, {})
    for item in exclude_list:
        if item in kwargs:
            del kwargs[item]
    return kwargs


# ------------------------------------------------
# primary components
# ------------------------------------------------


class _Command:
    def __init__(self, func, name=None, parent=None):
        if not inspect.isfunction(func) and not inspect.ismethod(func):
            raise ValueError('Parameter "func" must be a function or method! (Built-ins are not allowed.)')
        self._func = func
        if not name:
            name = func.__name__
        name = name.strip()
        if re.search(r'\s', name):
            raise ValueError('Whitespace character is disallowed in command name!')
        self._name = name
        self.parent = parent
        self._positional_args = []
        self._is_last_positional_args = False

        fallback = func.__doc__ if config.settings['command']['use_docstring_as_default_description'] else None
        description_str = getattr(func, 'description', fallback)
        if description_str is not None:
            description_str = description_str.strip()

        self.parser = argparse.ArgumentParser(prog=self.fullname, description=description_str,
                                              add_help=config.settings['command']['add_help_flag'],
                                              allow_abbrev=config.settings['command']['match_substr'])
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            if name in getattr(func, 'ignore', set()):
                continue
            if param.kind is param.VAR_POSITIONAL:
                # *args
                self.parser.add_argument(name, nargs='*')
                self._positional_args.append(name)
                self._is_last_positional_args = True
            elif param.kind is param.VAR_KEYWORD:
                # **kwargs
                raise ValueError("Cannot find a way to properly place '%s' as an argument!" % name)
            elif param.default is param.empty:
                # parameters with no default values in the function
                self.parser.add_argument(name)
                self._positional_args.append(name)
            else:
                dest = '-%s' % name if len(name) == 1 else '--%s' % name
                # parameters with default values in the function
                if param.default is True:
                    self.parser.add_argument(dest, action='store_false')
                elif param.default is False:
                    self.parser.add_argument(dest, action='store_true')
                elif param.default is None:
                    self.parser.add_argument(name, nargs='?')
                    self._positional_args.append(name)
                elif isinstance(param.default, (tuple, list)):
                    kwargs = _extract_kwargs(func, name, exclude_list=['action'])
                    self.parser.add_argument(dest, action='append', **kwargs)
                elif isinstance(param.default, (float, int, str)):
                    kwargs = _extract_kwargs(func, name, exclude_list=['action', 'required', 'default'])
                    self.parser.add_argument(dest, action='store', type=type(param.default),
                                             required=False, default=param.default, **kwargs)
                else:
                    # don't add the parameter
                    raise ValueError("Cannot add parameter with default type: '%s'!" %
                                     type(param.default).__name__)

    def run(self, argstr=''):
        try:
            args = self.parser.parse_args(shlex.split(argstr))
        except SystemExit:
            return None
        positionals = []
        kwargs = args.__dict__
        if len(self._positional_args) > 0:
            for name in self._positional_args[:-1]:
                positionals.append(kwargs[name])
                del kwargs[name]
            name = self._positional_args[-1]
            if self._is_last_positional_args:
                positionals += kwargs[name]
            else:
                positionals.append(kwargs[name])
            del kwargs[name]
        return self._func(*positionals, **kwargs)

    @property
    def name(self):
        return self._name

    @property
    def fullname(self):
        parent = self.parent
        fullname = self._name
        while isinstance(parent, _CompositeCommand):
            if parent.name:
                fullname = parent.name + ' ' + fullname
            parent = parent.parent
        return fullname

    @property
    def usage(self):
        return self.parser.format_usage().rstrip()

    @property
    def help(self):
        return self.parser.format_help()


class _CompositeCommand(UserDict):
    """
    A command that has one or more subcommands
    """

    def __init__(self, name, parent=None):
        super().__init__()
        self._name = name
        if re.search(r'\s', name):
            raise ValueError('Whitespace character is disallowed in command name!')
        self.parent = parent

    # can add either composite command or subcommand
    def add_command(self, cmd):
        if cmd.name in self.data:
            raise ValueError('Group "%s" already has "%s"!' % (self._name, cmd.name))
        cmd.parent = self
        self.data[cmd.name] = cmd

    def run(self, argstr=''):
        cmd, argstr = _shift(argstr)
        if config.settings['rules']['case_insensitive']:
            cmd = cmd.lower()
        if cmd in self.data:
            cmd = self.data[cmd]
            return cmd.run(argstr)
        else:
            print('Unknown option: %s' % cmd)
            print(self.help)

    @property
    def name(self):
        return self._name

    @property
    def usage(self):
        return 'usage: %s [option]\n' % self._name

    @property
    def help(self):
        help_msg = self.usage
        help_msg += 'available options:\n'
        for cmd in sorted(self.data):
            help_msg += '    %s\n' % cmd
        return help_msg


class CLI:
    """
    A simple CLI framework that comes with 3 default commands:
        help, exit, quit
    Use add_function() to add a function as a command in the CLI.
    Function parameters are automatically converted to command arguments by
    the following rules:
        1. Parameters with no default value are added as positional arguments
        2. Parameters with True or False default value are added as [--flag]
        3. Parameters with None as default value are added as optional
           positional arguments
        4. Parameters with list or tuple as default value are added as
           appendable [--arg val] (specify multiple times to add to a list of
           strings)
        5. Parameters with other types of default value are added as
           [--arg val] with 'val' automatically parsed to default value's type
        6. *args parameters are added as a list of 0 or more positional
           arguments
        7. **kwargs parameters cannot be added and will raise an error
        8. Parameters with "weird" default value types cannot be added and
           will raise an error
    Function docstring is automatically added as description of the command
    in the command's help message.
    If not explicitly specified, function name is used as the command name.
    """

    def __init__(self, prompt='> ', startup_msg=None, goodbye_msg=None,
                 enable_shell=False, enable_traceback=False, enable_tab_completion=True,
                 enable_eof_exit_confirmation=False, enable_non_tty_echo=True):
        self.prompt = prompt
        self._command_options = {}
        if startup_msg is None:
            exit_commands = ' or '.join(("'%s'" % cmd) for cmd in config.settings['default_commands']['exit'])
            startup_msg = ("Type 'help' to see help message.\n"
                           "Type %s to exit the program." % exit_commands)
        self._startup_msg = startup_msg
        if goodbye_msg is not None:
            atexit.register(lambda: print(goodbye_msg))
        self._exception_behaviors = {}
        self._enable_traceback = enable_traceback
        self._enable_eof_exit_confirmation = enable_eof_exit_confirmation
        self._enable_non_tty_echo = enable_non_tty_echo

        self._shell_commands = []
        self._system = config.system if config.system in config.settings['shell']['allowed_commands'] else \
            config.settings['shell']['default_sys']
        if enable_shell:
            self._shell_commands = config.settings['shell']['allowed_commands'][self._system]

        if enable_tab_completion:
            if config.system != 'windows':
                readline.parse_and_bind("tab: complete")
                readline.set_completer(self._completer)
            else:
                print('[WARNING] Since readline module cannot work on Windows, '
                      'tab completion has no effect!', file=sys.stderr)

        help_commands = config.settings['default_commands']['help']
        exit_commands = config.settings['default_commands']['exit']
        if isinstance(help_commands, str):
            help_commands = [help_commands]
        if isinstance(exit_commands, str):
            exit_commands = [exit_commands]
        for name in help_commands:
            self.add_function(self.print_help, name=name)
        for name in exit_commands:
            self.add_function(CLI.quit, name=name)

    def add_function(self, func, name=None):
        """
        Adds a function as command directly.

        Parameters
        ----------
        func : function
            Function to be added as command. Parameters automatically
            converted to command arguments.
        name : str
            If not given, function name is used as command name.
            Separate by white space to automatically add intermediate
            groups of command.
        """

        if name is None:
            name = func.__name__
        if config.settings['rules']['case_insensitive']:
            name = name.lower()
        fullname = name
        if fullname in self._shell_commands:
            raise ValueError('Command "%s" conflicts with existing shell command!' % fullname)
        name = name.split()
        parent = self._command_options
        while len(name) > 1:
            name_component = name[0]
            compo_cmd = parent.get(name_component, _CompositeCommand(name_component, parent))
            parent[name_component] = compo_cmd
            parent = compo_cmd
            name = name[1:]
        name = name[0]
        if name in parent:
            raise ValueError('Command "%s" already exists!' % fullname)
        parent[name] = _Command(func, name, parent)

    def add_exception_behavior(self, exception, behavior):
        """
        Instructs the console to catch a certain type of exception and then
        perform designated behavior.

        Parameters
        ----------
        exception : type
            Type of exception to catch.
        behavior : function or None
            A function that takes a single argument, the error object.
        """

        self._exception_behaviors[exception] = behavior

    def print_help(self, command_name=None):
        if command_name is None:
            # print help message for CLI
            commands = sorted(self._command_options)
            longest = max(map(len, commands))
            cell_width = max(10, min(20, longest + 2))
            cell_width = int(cell_width)
            n_groupby = 60 // cell_width  # max table width = 60 + 4 = 64

            print('Available commands:')
            for i in range(0, len(commands), n_groupby):
                group = commands[i:i + n_groupby]
                print('    ' + '%-{}s'.format(cell_width) * len(group) % tuple(group))
            print('See help for a specific command by specifying the command name.')
            print('Help message for multi-layered command can still be seen by using '
                  'quotation marks around them.')
            if len(self._shell_commands) > 0:
                print('Some shell commands are also enabled.')
        else:
            subname = command_name
            dictionary = self._command_options
            while subname:
                name, subname = _shift(subname)
                if name not in dictionary:
                    print('Unknown option: %s' % command_name)
                    break
                else:
                    cmd = dictionary[name]
                    if subname:
                        dictionary = cmd
                    else:
                        print(cmd.help)

    def get_command_list(self):
        return sorted(self._command_options)

    def execute(self, user_input):
        cmd, argstr = _shift(user_input)
        if not cmd:  # empty input
            return
        if config.settings['rules']['case_insensitive']:
            cmd = cmd.lower()

        if cmd in self._shell_commands:  # execute a shell command
            # sanitize check input and disallow command that are not in whitelist
            if '$(' in user_input or '`' in user_input:
                raise exceptions.NonCriticalCLIException('Shell command substitution is disallowed!')
            for subcmd in user_input.split('|'):
                cmd, argstr = _shift(subcmd)
                if cmd != '' and cmd not in self._shell_commands:
                    raise exceptions.NonCriticalCLIException('Disallowed shell command: %s' % cmd)
            if '|' in user_input:
                raise exceptions.NonCriticalCLIException('Sorry, piping is disallowed!')

            # execute command and redirect output to python's stdout and stderr according to config
            stdout = subprocess.PIPE if cmd in config.settings['shell']['pipe_stdout'][self._system] else None
            stderr = subprocess.PIPE if cmd in config.settings['shell']['pipe_stderr'][self._system] else None
            proc = subprocess.run(user_input, shell=True, stdout=stdout, stderr=stderr)
            if proc.stdout:
                print(proc.stdout.decode('utf-8'), end='', file=sys.stdout)
            if proc.stderr:
                print(proc.stderr.decode('utf-8'), end='', file=sys.stderr)
            if proc.returncode != 0:
                raise exceptions.NonCriticalCLIException('Shell command failed with exit code: %d' % proc.returncode)
        elif cmd in self._command_options:
            # execute a CLI command
            cmd = self._command_options[cmd]
            cmd.run(argstr)
        else:
            raise exceptions.NonCriticalCLIException('Unknown command: %s' % cmd)

    def loop(self):
        if self._startup_msg != '':
            print(self._startup_msg)
        while True:
            try:
                prompt = ''
                if inspect.isfunction(self.prompt):
                    prompt = self.prompt()
                elif isinstance(self.prompt, str):
                    prompt = self.prompt
                user_input = input(prompt)
                if config.system == 'windows' or \
                        (not sys.stdin.isatty() and self._enable_non_tty_echo):
                    print(user_input)
                self.execute(user_input)
            except EOFError:
                print()
                if self._enable_eof_exit_confirmation:
                    if utils.ask_yes_or_no('Do you really wish to quit?'):
                        break
                else:
                    break
            except KeyboardInterrupt:
                print()
                continue
            except tuple(self._exception_behaviors) as e:
                func = self._exception_behaviors[type(e)]
                if func is not None:
                    func(e)
                continue
            except exceptions.NonCriticalCLIException as e:
                print(str(e))
                continue
            except Exception as e:
                if self._enable_traceback:
                    traceback.print_exc()
                else:
                    print('[%s] %s' % (type(e).__name__, str(e)), file=sys.stderr)
                continue

    # tries to hint user of top-level command and subcommand options, falls back to filesystem
    def _completer(self, text, state):
        line = readline.get_line_buffer().lstrip()
        components = shlex.split(line)
        last_arg = ''
        if not line.endswith(' '):
            last_arg = components[-1]
            components = components[:-1]

        # try to find the component command
        namespace = self._command_options
        for name in components:
            if not isinstance(namespace, (dict, _CompositeCommand)) or name not in namespace:
                namespace = None
                break
            namespace = namespace[name]

        if isinstance(namespace, (dict, _CompositeCommand)):
            # subcommands (might) exist
            options = list(namespace)
        else:
            # namespace is None or Command class: falls back to filesystem
            directory = last_arg.rstrip(text)
            if directory == '':
                directory = '.'
            options = os.listdir(directory)
            for i, thing in enumerate(options):
                if os.path.isdir(thing):
                    options[i] = thing + os.sep

        candidates = sorted(opt for opt in options if opt.startswith(text))
        if state < len(candidates):
            return candidates[state]
        else:
            return None

    @staticmethod
    def quit(rc=None):
        if rc is None:
            rc = 0
        raise SystemExit(rc)
