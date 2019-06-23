#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin to export commands (experimental)
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

from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.words.protocols.jabber import jid
from twisted.internet import reactor, protocol

from sat.tools import trigger
from sat.tools.utils import clean_ustr

PLUGIN_INFO = {
    C.PI_NAME: "Command export plugin",
    C.PI_IMPORT_NAME: "EXP-COMMANS-EXPORT",
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "CommandExport",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Implementation of command export"""),
}


class ExportCommandProtocol(protocol.ProcessProtocol):
    """ Try to register an account with prosody """

    def __init__(self, parent, client, target, options):
        self.parent = parent
        self.target = target
        self.options = options
        self.client = client

    def _clean(self, data):
        if not data:
            log.error("data should not be empty !")
            return u""
        decoded = data.decode("utf-8", "ignore")[: -1 if data[-1] == "\n" else None]
        return clean_ustr(decoded)

    def connectionMade(self):
        log.info("connectionMade :)")

    def outReceived(self, data):
        self.client.sendMessage(self.target, {"": self._clean(data)}, no_trigger=True)

    def errReceived(self, data):
        self.client.sendMessage(self.target, {"": self._clean(data)}, no_trigger=True)

    def processEnded(self, reason):
        log.info(u"process finished: %d" % (reason.value.exitCode,))
        self.parent.removeProcess(self.target, self)

    def write(self, message):
        self.transport.write(message.encode("utf-8"))

    def boolOption(self, key):
        """ Get boolean value from options
        @param key: name of the option
        @return: True if key exists and set to "true" (case insensitive),
                 False in all other cases """
        value = self.options.get(key, "")
        return value.lower() == "true"


class CommandExport(object):
    """Command export plugin: export a command to an entity"""

    # XXX: This plugin can be potentially dangerous if we don't trust entities linked
    #      this is specially true if we have other triggers.
    # FIXME: spawned should be a client attribute, not a class one

    def __init__(self, host):
        log.info(_("Plugin command export initialization"))
        self.host = host
        self.spawned = {}  # key = entity
        host.trigger.add("MessageReceived", self.MessageReceivedTrigger, priority=10000)
        host.bridge.addMethod(
            "exportCommand",
            ".plugin",
            in_sign="sasasa{ss}s",
            out_sign="",
            method=self._exportCommand,
        )

    def removeProcess(self, entity, process):
        """ Called when the process is finished
        @param entity: jid.JID attached to the process
        @param process: process to remove"""
        try:
            processes_set = self.spawned[(entity, process.client.profile)]
            processes_set.discard(process)
            if not processes_set:
                del (self.spawned[(entity, process.client.profile)])
        except ValueError:
            pass

    def MessageReceivedTrigger(self, client, message_elt, post_treat):
        """ Check if source is linked and repeat message, else do nothing  """
        from_jid = jid.JID(message_elt["from"])
        spawned_key = (from_jid.userhostJID(), client.profile)

        if spawned_key in self.spawned:
            try:
                body = message_elt.elements(C.NS_CLIENT, "body").next()
            except StopIteration:
                # do not block message without body (chat state notification...)
                return True

            mess_data = unicode(body) + "\n"
            processes_set = self.spawned[spawned_key]
            _continue = False
            exclusive = False
            for process in processes_set:
                process.write(mess_data)
                _continue &= process.boolOption("continue")
                exclusive |= process.boolOption("exclusive")
            if exclusive:
                raise trigger.SkipOtherTriggers
            return _continue

        return True

    def _exportCommand(self, command, args, targets, options, profile_key):
        """ Export a commands to authorised targets
        @param command: full path of the command to execute
        @param args: list of arguments, with command name as first one
        @param targets: list of allowed entities
        @param options: export options, a dict which can have the following keys ("true" to set booleans):
                        - exclusive: if set, skip all other triggers
                        - loop: if set, restart the command once terminated #TODO
                        - pty: if set, launch in a pseudo terminal
                        - continue: continue normal MessageReceived handling
        """
        client = self.host.getClient(profile_key)
        for target in targets:
            try:
                _jid = jid.JID(target)
                if not _jid.user or not _jid.host:
                    raise jid.InvalidFormat
                _jid = _jid.userhostJID()
            except (RuntimeError, jid.InvalidFormat, AttributeError):
                log.info(u"invalid target ignored: %s" % (target,))
                continue
            process_prot = ExportCommandProtocol(self, client, _jid, options)
            self.spawned.setdefault((_jid, client.profile), set()).add(process_prot)
            reactor.spawnProcess(
                process_prot, command, args, usePTY=process_prot.boolOption("pty")
            )
