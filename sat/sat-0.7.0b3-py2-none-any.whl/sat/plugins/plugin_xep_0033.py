#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Extended Stanza Addressing (xep-0033)
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

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
from sat.core import exceptions
from wokkel import disco, iwokkel
from zope.interface import implements
from twisted.words.protocols.jabber.jid import JID
from twisted.python import failure
import copy

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler
from twisted.words.xish import domish
from twisted.internet import defer

from sat.tools import trigger
from time import time

# TODO: fix Prosody "addressing" plugin to leave the concerned bcc according to the spec:
#
# http://xmpp.org/extensions/xep-0033.html#addr-type-bcc
# "This means that the server MUST remove these addresses before the stanza is delivered to anyone other than the given bcc addressee or the multicast service of the bcc addressee."
#
# http://xmpp.org/extensions/xep-0033.html#multicast
# "Each 'bcc' recipient MUST receive only the <address type='bcc'/> associated with that addressee."

# TODO: fix Prosody "addressing" plugin to determine itself if remote servers supports this XEP


NS_XMPP_CLIENT = "jabber:client"
NS_ADDRESS = "http://jabber.org/protocol/address"
ATTRIBUTES = ["jid", "uri", "node", "desc", "delivered", "type"]
ADDRESS_TYPES = ["to", "cc", "bcc", "replyto", "replyroom", "noreply"]

PLUGIN_INFO = {
    C.PI_NAME: "Extended Stanza Addressing Protocol Plugin",
    C.PI_IMPORT_NAME: "XEP-0033",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0033"],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "XEP_0033",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Extended Stanza Addressing"""),
}


class XEP_0033(object):
    """
    Implementation for XEP 0033
    """

    def __init__(self, host):
        log.info(_("Extended Stanza Addressing plugin initialization"))
        self.host = host
        self.internal_data = {}
        host.trigger.add(
            "sendMessage", self.sendMessageTrigger, trigger.TriggerManager.MIN_PRIORITY
        )
        host.trigger.add("MessageReceived", self.messageReceivedTrigger)

    def sendMessageTrigger(
        self, client, mess_data, pre_xml_treatments, post_xml_treatments
    ):
        """Process the XEP-0033 related data to be sent"""
        profile = client.profile

        def treatment(mess_data):
            if not "address" in mess_data["extra"]:
                return mess_data

            def discoCallback(entities):
                if not entities:
                    log.warning(
                        _("XEP-0033 is being used but the server doesn't support it!")
                    )
                    raise failure.Failure(
                        exceptions.CancelError(u"Cancelled by XEP-0033")
                    )
                if mess_data["to"] not in entities:
                    expected = _(" or ").join([entity.userhost() for entity in entities])
                    log.warning(
                        _(
                            u"Stanzas using XEP-0033 should be addressed to %(expected)s, not %(current)s!"
                        )
                        % {"expected": expected, "current": mess_data["to"]}
                    )
                    log.warning(
                        _(
                            u"TODO: addressing has been fixed by the backend... fix it in the frontend!"
                        )
                    )
                    mess_data["to"] = list(entities)[0].userhostJID()
                element = mess_data["xml"].addElement("addresses", NS_ADDRESS)
                entries = [
                    entry.split(":")
                    for entry in mess_data["extra"]["address"].split("\n")
                    if entry != ""
                ]
                for type_, jid_ in entries:
                    element.addChild(
                        domish.Element(
                            (None, "address"), None, {"type": type_, "jid": jid_}
                        )
                    )
                # when the prosody plugin is completed, we can immediately return mess_data from here
                self.sendAndStoreMessage(mess_data, entries, profile)
                log.debug("XEP-0033 took over")
                raise failure.Failure(exceptions.CancelError(u"Cancelled by XEP-0033"))

            d = self.host.findFeaturesSet(client, [NS_ADDRESS])
            d.addCallbacks(discoCallback, lambda __: discoCallback(None))
            return d

        post_xml_treatments.addCallback(treatment)
        return True

    def sendAndStoreMessage(self, mess_data, entries, profile):
        """Check if target servers support XEP-0033, send and store the messages
        @return: a friendly failure to let the core know that we sent the message already

        Later we should be able to remove this method because:
        # XXX: sending the messages should be done by the local server
        # FIXME: for now we duplicate the messages in the history for each recipient, this should change
        # FIXME: for now we duplicate the echoes to the sender, this should also change
        Ideas:
        - fix Prosody plugin to check if target server support the feature
        - redesign the database to save only one entry to the database
        - change the messageNew signal to eventually pass more than one recipient
        """
        client = self.host.getClient(profile)

        def send(mess_data, skip_send=False):
            d = defer.Deferred()
            if not skip_send:
                d.addCallback(client.sendMessageData)
            d.addCallback(client.messageAddToHistory)
            d.addCallback(client.messageSendToBridge)
            d.addErrback(lambda failure: failure.trap(exceptions.CancelError))
            return d.callback(mess_data)

        def discoCallback(entities, to_jid_s):
            history_data = copy.deepcopy(mess_data)
            history_data["to"] = JID(to_jid_s)
            history_data["xml"]["to"] = to_jid_s
            if entities:
                if entities not in self.internal_data[timestamp]:
                    sent_data = copy.deepcopy(mess_data)
                    sent_data["to"] = JID(JID(to_jid_s).host)
                    sent_data["xml"]["to"] = JID(to_jid_s).host
                    send(sent_data)
                    self.internal_data[timestamp].append(entities)
                # we still need to fill the history and signal the echo...
                send(history_data, skip_send=True)
            else:
                # target server misses the addressing feature
                send(history_data)

        def errback(failure, to_jid):
            discoCallback(None, to_jid)

        timestamp = time()
        self.internal_data[timestamp] = []
        defer_list = []
        for type_, jid_ in entries:
            d = defer.Deferred()
            d.addCallback(
                self.host.findFeaturesSet, client=client, jid_=JID(JID(jid_).host)
            )
            d.addCallbacks(
                discoCallback, errback, callbackArgs=[jid_], errbackArgs=[jid_]
            )
            d.callback([NS_ADDRESS])
            defer_list.append(d)
        d = defer.Deferred().addCallback(lambda __: self.internal_data.pop(timestamp))
        defer.DeferredList(defer_list).chainDeferred(d)

    def messageReceivedTrigger(self, client, message, post_treat):
        """In order to save the addressing information in the history"""

        def post_treat_addr(data, addresses):
            data["extra"]["addresses"] = ""
            for address in addresses:
                # Depending how message has been constructed, we could get here
                # some noise like "\n        " instead of an address element.
                if isinstance(address, domish.Element):
                    data["extra"]["addresses"] += "%s:%s\n" % (
                        address["type"],
                        address["jid"],
                    )
            return data

        try:
            addresses = message.elements(NS_ADDRESS, "addresses").next()
        except StopIteration:
            pass  # no addresses
        else:
            post_treat.addCallback(post_treat_addr, addresses.children)
        return True

    def getHandler(self, client):
        return XEP_0033_handler(self, client.profile)


class XEP_0033_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent, profile):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host
        self.profile = profile

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_ADDRESS)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
