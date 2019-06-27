#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for parrot mode (experimental)
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

from sat.core.exceptions import UnknownEntityError

# from sat.tools import trigger

PLUGIN_INFO = {
    C.PI_NAME: "Parrot Plugin",
    C.PI_IMPORT_NAME: "EXP-PARROT",
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0045"],
    C.PI_RECOMMENDATIONS: [C.TEXT_CMDS],
    C.PI_MAIN: "Exp_Parrot",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(
        u"""Implementation of parrot mode (repeat messages between 2 entities)"""
    ),
}


class Exp_Parrot(object):
    """Parrot mode plugin: repeat messages from one entity or MUC room to another one"""

    # XXX: This plugin can be potentially dangerous if we don't trust entities linked
    #      this is specially true if we have other triggers.
    #      sendMessageTrigger avoid other triggers execution, it's deactivated to allow
    #      /unparrot command in text commands plugin.
    # FIXME: potentially unsecure, specially with e2e encryption

    def __init__(self, host):
        log.info(_("Plugin Parrot initialization"))
        self.host = host
        host.trigger.add("MessageReceived", self.MessageReceivedTrigger, priority=100)
        # host.trigger.add("sendMessage", self.sendMessageTrigger, priority=100)
        try:
            self.host.plugins[C.TEXT_CMDS].registerTextCommands(self)
        except KeyError:
            log.info(_(u"Text commands not available"))

    # def sendMessageTrigger(self, client, mess_data, treatments):
    #    """ Deactivate other triggers if recipient is in parrot links """
    #    try:
    #        _links = client.parrot_links
    #    except AttributeError:
    #        return True
    #
    #    if mess_data['to'].userhostJID() in _links.values():
    #        log.debug("Parrot link detected, skipping other triggers")
    #        raise trigger.SkipOtherTriggers

    def MessageReceivedTrigger(self, client, message_elt, post_treat):
        """ Check if source is linked and repeat message, else do nothing  """
        # TODO: many things are not repeated (subject, thread, etc)
        profile = client.profile
        client = self.host.getClient(profile)
        from_jid = message_elt["from"]

        try:
            _links = client.parrot_links
        except AttributeError:
            return True

        if not from_jid.userhostJID() in _links:
            return True

        message = {}
        for e in message_elt.elements(C.NS_CLIENT, "body"):
            body = unicode(e)
            lang = e.getAttribute("lang") or ""

            try:
                entity_type = self.host.memory.getEntityData(from_jid, ["type"], profile)[
                    "type"
                ]
            except (UnknownEntityError, KeyError):
                entity_type = "contact"
            if entity_type == "chatroom":
                src_txt = from_jid.resource
                if src_txt == self.host.plugins["XEP-0045"].getRoomNick(
                    client, from_jid.userhostJID()
                ):
                    # we won't repeat our own messages
                    return True
            else:
                src_txt = from_jid.user
            message[lang] = u"[{}] {}".format(src_txt, body)

            linked = _links[from_jid.userhostJID()]

            client.sendMessage(
                jid.JID(unicode(linked)), message, None, "auto", no_trigger=True
            )

        return True

    def addParrot(self, client, source_jid, dest_jid):
        """Add a parrot link from one entity to another one

        @param source_jid: entity from who messages will be repeated
        @param dest_jid: entity where the messages will be repeated
        """
        try:
            _links = client.parrot_links
        except AttributeError:
            _links = client.parrot_links = {}

        _links[source_jid.userhostJID()] = dest_jid
        log.info(
            u"Parrot mode: %s will be repeated to %s"
            % (source_jid.userhost(), unicode(dest_jid))
        )

    def removeParrot(self, client, source_jid):
        """Remove parrot link

        @param source_jid: this entity will no more be repeated
        """
        try:
            del client.parrot_links[source_jid.userhostJID()]
        except (AttributeError, KeyError):
            pass

    def cmd_parrot(self, client, mess_data):
        """activate Parrot mode between 2 entities, in both directions."""
        log.debug("Catched parrot command")
        txt_cmd = self.host.plugins[C.TEXT_CMDS]

        try:
            link_left_jid = jid.JID(mess_data["unparsed"].strip())
            if not link_left_jid.user or not link_left_jid.host:
                raise jid.InvalidFormat
        except (RuntimeError, jid.InvalidFormat, AttributeError):
            txt_cmd.feedBack(
                client, "Can't activate Parrot mode for invalid jid", mess_data
            )
            return False

        link_right_jid = mess_data["to"]

        self.addParrot(client, link_left_jid, link_right_jid)
        self.addParrot(client, link_right_jid, link_left_jid)

        txt_cmd.feedBack(
            client,
            "Parrot mode activated for {}".format(unicode(link_left_jid)),
            mess_data,
        )

        return False

    def cmd_unparrot(self, client, mess_data):
        """remove Parrot mode between 2 entities, in both directions."""
        log.debug("Catched unparrot command")
        txt_cmd = self.host.plugins[C.TEXT_CMDS]

        try:
            link_left_jid = jid.JID(mess_data["unparsed"].strip())
            if not link_left_jid.user or not link_left_jid.host:
                raise jid.InvalidFormat
        except jid.InvalidFormat:
            txt_cmd.feedBack(
                client, u"Can't deactivate Parrot mode for invalid jid", mess_data
            )
            return False

        link_right_jid = mess_data["to"]

        self.removeParrot(client, link_left_jid)
        self.removeParrot(client, link_right_jid)

        txt_cmd.feedBack(
            client,
            u"Parrot mode deactivated for {} and {}".format(
                unicode(link_left_jid), unicode(link_right_jid)
            ),
            mess_data,
        )

        return False
