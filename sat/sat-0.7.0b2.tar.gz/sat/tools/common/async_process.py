#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""tools to launch process in a async way (using Twisted)"""

import os.path
from twisted.internet import defer, reactor, protocol
from twisted.python.failure import Failure
from sat.core.i18n import _
from sat.core import exceptions
from sat.core.log import getLogger
log = getLogger(__name__)


class CommandProtocol(protocol.ProcessProtocol):
    """handle an external command"""
    # name of the command (unicode)
    name = None
    # full path to the command (bytes)
    command = None
    # True to activate logging of command outputs (bool)
    log = False

    def __init__(self, deferred, stdin=None):
        """
        @param deferred(defer.Deferred): will be called when command is completed
        @param stdin(str, None): if not None, will be push to standard input
        """
        self._stdin = stdin
        self._deferred = deferred
        self.data = []
        self.err_data = []

    @property
    def command_name(self):
        """returns command name or empty string if it can't be guessed"""
        if self.name is not None:
            return self.name
        elif self.command is not None:
            return os.path.splitext(os.path.basename(self.command))[0].decode('utf-8',
                                                                              'ignore')
        else:
            return u''

    def connectionMade(self):
        if self._stdin is not None:
            self.transport.write(self._stdin)
            self.transport.closeStdin()

    def outReceived(self, data):
        if self.log:
            log.info(data.decode('utf-8', 'replace'))
        self.data.append(data)

    def errReceived(self, data):
        if self.log:
            log.warning(data.decode('utf-8', 'replace'))
        self.err_data.append(data)

    def processEnded(self, reason):
        data = ''.join(self.data)
        if (reason.value.exitCode == 0):
            log.debug(_(u'{name} command succeed').format(name=self.command_name))
            # we don't use "replace" on purpose, we want an exception if decoding
            # is not working properly
            self._deferred.callback(data.encode('utf-8'))
        else:
            err_data = u''.join(self.err_data)

            msg = (_(u"Can't complete {name} command (error code: {code}):\n"
                     u"stderr:\n{stderr}\n{stdout}\n")
                   .format(name = self.command_name,
                           code = reason.value.exitCode,
                           stderr= err_data.encode('utf-8', 'replace'),
                           stdout = "stdout: " + data.encode('utf-8', 'replace')
                                    if data else u'',
                           ))
            self._deferred.errback(Failure(exceptions.CommandException(
                msg, data, err_data)))

    @classmethod
    def run(cls, *args, **kwargs):
        """Create a new CommandProtocol and execute the given command.

        @param *args(unicode): command arguments
            if cls.command is specified, it will be the path to the command to execture
            otherwise, first argument must be the path
        @param **kwargs: can be:
            - stdin(unicode, None): data to push to standard input
            - verbose(bool): if True stdout and stderr will be logged
            other keyword arguments will be used in reactor.spawnProcess
        @return ((D)): stdout in case of success
        @raise RuntimeError: command returned a non zero status
            stdin and stdout will be given as arguments

        """
        stdin = kwargs.pop('stdin', None)
        if stdin is not None:
            stdin = stdin.encode('utf-8')
        verbose = kwargs.pop('verbose', False)
        if u'path' in kwargs:
            kwargs[u'path'] = kwargs[u'path'].encode('utf-8')
        args = [a.encode('utf-8') for a in args]
        kwargs = {k:v.encode('utf-8') for k,v in kwargs.items()}
        d = defer.Deferred()
        prot = cls(d, stdin=stdin)
        if verbose:
            prot.log = True
        if cls.command is None:
            if not args:
                raise ValueError(
                    u"You must either specify cls.command or use a full path to command "
                    u"to execute as first argument")
            command = args.pop(0)
            if prot.name is None:
                name = os.path.splitext(os.path.basename(command))[0]
                prot.name = name.encode(u'utf-8', u'ignore')
        else:
            command = cls.command
        cmd_args = [os.path.basename(command)] + args
        reactor.spawnProcess(prot,
                             command,
                             cmd_args,
                             **kwargs)
        return d
