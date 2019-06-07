# -*- coding: utf-8 -*-
# Copyright (c) 2003-2012 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

"""
A Module that contains usefull utilities.
"""

import shlex
import fnmatch

from urwid.command_map import CommandMap
from hgviewlib.curses.exceptions import UnknownCommand, RegisterCommandError

__all__ = ['register_command', 'unregister_command', 'connect_command',
           'disconnect_command', 'emit_command', 'help_command',
           'complete_command', 'CommandArg',  'hg_command_map',
           'History',
          ]


# ____________________________________________________________________ commands
class CommandArg(object):
    def __init__(self, name, parser, help):
        self.name = name
        self.parser = parser
        self.help = help

class Commands(object):
    """A class that handle commands using a signal-like system.

    * You shall *register* a command before using it.
    * Then you may want to *connect* callbacks to commands and call.
    * They will be processed while *emitting* the cammands.
    * Note that you can pick up *help* about commands.

    You can fix callback arguments when connecting and/or emmitting a command.

    Emit method accept a command line string. This command line can only be a
    command name if all arguments for all callbacks have been fixed (or if they
    are optionals). Otherwise the command options can be automatically parsed
    by giving `CommandArg`s to register.

    """
    def __init__(self):
        self._args = {}
        self._helps = {}
        self._calls = {}

    def register(self, names, help, *args):
        """Register a command to make it available for connecting/emitting.

        :names: the command name or a list of aliases.
        :args: `CommandArg` instances.

        >>> from hgviewlib.curses import utils
        >>> import urwid
        >>> args = (utils.CommandArg('arg1', int, 'argument1'),
        ...         utils.CommandArg('arg2', float, 'argument2'),)
        >>> utils.register_command('foo', 'A command', *args)
        >>> out = utils.unregister_command('foo')

        """
        if isinstance(names, str):
            names = [names]
        for name in names:
            if name in self._helps:
                raise RegisterCommandError(
                        'Command "%s" already registered' % name)
        for arg in args:
            if not isinstance(arg, CommandArg):
                raise RegisterCommandError(
                    'Command arguments description type must be a CommandArg')
        calls = []
        # all points to the same values
        for name in names:
            self._args[name] = args
            self._helps[name] = help
            self._calls[name] = calls

    def __contains__(self, name):
        """Do not use"""
        return name in self._helps

    def unregister(self, name):
        """Unregister a command."""
        if name not in self:
            return
        help = self._helps.pop(name)
        args = self._args.pop(name)
        calls = self._calls.pop(name)
        return help, args, calls

    def connect(self, name, callback, args=None, kwargs=None):
        """Disconnect the ``callback`` associated to the given ``args`` and
        ``kwargs`` from the command ``name``.

        See documentation of ``emit_command`` for details about ``args`` and
        ``kwarg``.
        """
        if name not in self:
            raise RegisterCommandError(
            'You must register the command "%s" before connecting a callback.'
            % name)
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        self._calls[name].append((callback, args, kwargs))

    def disconnect(self, name, callback, args=None, kwargs=None):
        """Disconnect the ``callback`` associated to the given ``args`` and
        ``kwargs`` from the command ``name``.

        >>> from hgviewlib.curses import utils
        >>> utils.register_command('foo', 'A command')
        >>> func = lambda *a, **k: True
        >>> utils.connect_command('foo', func, (1,2), {'a':0})
        >>> utils.disconnect_command('foo', func, (1,2), {'a':0})
        >>> out = utils.unregister_command('foo')

        """
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        try:
            self._calls[name].remove((callback, args, kwargs))
        except KeyError:
            raise RegisterCommandError('Command not registered: %s' % name)
        except ValueError:
            raise RegisterCommandError('Callbacks not connected.')

    def emit(self, cmdline, args=None, kwargs=None):
        """Call all callbacks connected to the command previously registered.

        Callbacks are processed as following::

          registered_callback(*args, **kwargs)

        where ``args = connect_args + emit_args + commandline_args``
        and ``kwargs = connect_kwargs.copy(); kwargs.update(emit_kwargs)``

        :cmdline: a string that contains the complete command line.

        :return: True is a callback return True, else False

        """
        result = False
        name, rawargs = (cmdline.strip().split(None, 1) + [''])[:2]
        if not name in self:
            raise UnknownCommand(name)

        cmdargs = []
        if rawargs and self._args[name]:
            data = self._args[name]
            # shlex does not support unicode, so we have to encode/decode the
            # command line
            arguments = (item.decode('utf-8')
                         for item in shlex.split(rawargs.encode('utf-8')))
            for idx, arg in enumerate(arguments):
                try:
                    parser = data[idx].parser
                except IndexError:
                    parser = str
                cmdargs.append(parser(arg))
        cmdargs = tuple(cmdargs)

        result = False
        for _func_, _args_, _kwargs_  in self._calls[name]:
            ags = _args_ + (args or ()) + cmdargs
            kws = _kwargs_.copy()
            kws.update(kwargs or {})
            result |= bool(_func_(*ags, **kws))
        return result

    def help(self, name):
        """Return help for command ``name`` suitable for urwid.Text.

        >>> from hgviewlib.curses import utils
        >>> import urwid
        >>> args = (utils.CommandArg('arg1', int, 'argument1'),
        ...         utils.CommandArg('arg2', float, 'argument2'),)
        >>> utils.register_command('foo', 'A command', *args)
        >>> data = urwid.Text(utils.help_command('foo')).render((20,)).text
        >>> print '|%s|' % '|\\n|'.join(data)
        |usage: foo arg1 arg2|
        |A command           |
        |:arg1: argument1    |
        |:arg2: argument2    |
        |                    |
        >>> out = utils.unregister_command('foo')

        """
        if name not in self._helps:
            raise RegisterCommandError(
                    'Unknown command "%s"' % name)
        help = self._helps[name]
        args = self._args[name]
        message = [('default', 'usage: '), ('WARNING', name)] \
                + [('DEBUG', ' ' + a.name) for a in args] \
                + [('default', '\n%s\n' % help)]
        for arg in args:
            message.append(('default', ':'))
            message.append(('DEBUG', arg.name))
            message.append(('default', ': '))
            message.append(arg.help + '\n')
        return message

    def helps(self):
        """Return a generator that gives (name, help) for each command"""
        for name in sorted(self._helps.keys()):
            yield name, self.help(name)

    def complete(self, line):
        """
        Return  command name candidates that complete ``line``.
        It uses fnmatch to match candidates, so ``line`` may contains
        wildcards.
        """
        if not line:
            return self._helps.keys()
        line = tuple(line.split(None, 1))
        out = line
        if len(line) == 1:
            cmd = line[0] + '*'
            return tuple(sorted(fnmatch.filter(self._args, cmd)))

# Instanciate a Commands object to handle command from a global scope.
#pylint: disable=C0103
_commands = Commands()
register_command = _commands.register
unregister_command = _commands.unregister
connect_command = _commands.connect
disconnect_command = _commands.disconnect
emit_command = _commands.emit
help_command = _commands.help
help_commands = _commands.helps
complete_command = _commands.complete
#pylint: enable=C0103

class History(list):
    def __init__(self, list=None, current=None):
        super(History, self).__init__(list or ())
        self.insert(0, current)
        self.position = 0

    def get(self, position, default=None):
        """
        Return the history entry at `position` or `default` if not found.
        """
        try:
            return self[position]
        except IndexError:
            return default

    def get_next(self, default=None):
        """Return the next entry of the history"""
        self.position += 1
        self.position %= len(self)
        return self.get(self.position, default)

    def get_prev(self, default=None):
        """Return the previous entry of the history"""
        self.position -= 1
        self.position %= len(self)
        return self.get(self.position, default)

    def reset_position(self):
        """reset the position of the history pointer"""
        self.position = 0

    def set_current(self, current):
        self[0] = current

# _________________________________________________________________ command map


class HgCommandMap(object):
    """Map keys to more explicit action names."""
    _command_defaults = (

        ('f1', '@help'),
        ('enter', 'validate'),
        ('m', '@maximize-context'),
        ('.', '@toggle-hidden'),

        # Qt interface
        ('f5', 'command key'),
        ('esc', 'escape'),
        ('ctrl l', '@refresh'),
        ('ctrl w', 'close pane'),

        ('up', 'graphlog up'),
        ('down', 'graphlog down'),
        ('left', 'manifest up'),
        ('right', 'manifest down'),
        ('meta up', 'source up'),
        ('meta down', 'source down'),

        ('page up', 'graphlog page up'),
        ('page down', 'graphlog page down'),
        ('home', 'manifest page up'),
        ('end', 'manifest page down'),
        ('insert', 'source page up'),
        ('delete', 'source page down'),

        # vim interface
        (':', 'command key'),
        #'esc','escape', already set in Qt interface
        ('r', '@refresh'),
        ('q', 'close pane'),

        ('k', 'graphlog up'),
        ('j', 'graphlog down'),
        ('h', 'manifest up'),
        ('l', 'manifest down'),
        ('p', 'source up'),
        ('n', 'source down'),

        ('K', 'graphlog page up'),
        ('J', 'graphlog page down'),
        ('H', 'manifest page up'),
        ('L', 'manifest page down'),
        ('P', 'source page up'),
        ('N', 'source page down'),

        # emacs interface
        ('meta x', 'command key'),
        ('ctrl g', 'escape'),
        ('ctrl v', '@refresh'),
        ('ctrl k', 'close pane'),

        ('ctrl p', 'graphlog up'),
        ('ctrl n', 'graphlog down'),
        ('ctrl b', 'manifest up'),
        ('ctrl f', 'manifest down'),
        ('ctrl a', 'source up'),
        ('ctrl e', 'source down'),

        ('meta p', 'graphlog page up'),
        ('meta n', 'graphlog page down'),
        ('meta b', 'manifest page up'),
        ('meta f', 'manifest page down'),
        ('meta a', 'source page up'),
        ('meta e', 'source page down'),
    )
    def __init__(self):
        self._map = dict(self._command_defaults)
    def __getitem__(self, key):
        """a.__getitem__(key) <=> a[key]
        return an explicit name associated to the key or None if not found.
        """
        return self._map.get(key)
    def items(self):
        """return the list of (registered keys, associated name)"""
        return self._command_defaults
    def keys(self):
        """return the list of registered keys"""
        return self._map.keys()

hg_command_map = HgCommandMap()

