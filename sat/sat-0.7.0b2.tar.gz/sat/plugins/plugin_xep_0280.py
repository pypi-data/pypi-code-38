#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing xep-0280
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

from sat.core.i18n import _, D_
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core import exceptions
from sat.core.constants import Const as C
from twisted.words.protocols.jabber.error import StanzaError
from twisted.internet import defer
from wokkel import disco, iwokkel
from zope.interface import implements

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler


PARAM_CATEGORY = "Misc"
PARAM_NAME = "carbon"
PARAM_LABEL = D_(u"Message carbons")
NS_CARBONS = "urn:xmpp:carbons:2"

PLUGIN_INFO = {
    C.PI_NAME: u"XEP-0280 Plugin",
    C.PI_IMPORT_NAME: u"XEP-0280",
    C.PI_TYPE: u"XEP",
    C.PI_PROTOCOLS: [u"XEP-0280"],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: u"XEP_0280",
    C.PI_HANDLER: u"yes",
    C.PI_DESCRIPTION: D_(u"""Implementation of Message Carbons"""),
}


class XEP_0280(object):
    #  TODO: param is only checked at profile connection
    #       activate carbons on param change even after profile connection
    # TODO: chat state notifications are not handled yet (and potentially other XEPs?)

    params = """
    <params>
    <individual>
    <category name="{category_name}" label="{category_label}">
        <param name="{param_name}" label="{param_label}" value="true" type="bool" security="0" />
     </category>
    </individual>
    </params>
    """.format(
        category_name=PARAM_CATEGORY,
        category_label=D_(PARAM_CATEGORY),
        param_name=PARAM_NAME,
        param_label=PARAM_LABEL,
    )

    def __init__(self, host):
        log.info(_("Plugin XEP_0280 initialization"))
        self.host = host
        host.memory.updateParams(self.params)
        host.trigger.add("MessageReceived", self.messageReceivedTrigger, priority=200000)

    def getHandler(self, client):
        return XEP_0280_handler()

    def setPrivate(self, message_elt):
        """Add a <private/> element to a message

        this method is intented to be called on final domish.Element by other plugins
        (in particular end 2 end encryption plugins)
        @param message_elt(domish.Element): <message> stanza
        """
        if message_elt.name != u"message":
            log.error(u"addPrivateElt must be used with <message> stanzas")
            return
        message_elt.addElement((NS_CARBONS, u"private"))

    @defer.inlineCallbacks
    def profileConnected(self, client):
        """activate message carbons on connection if possible and activated in config"""
        activate = self.host.memory.getParamA(
            PARAM_NAME, PARAM_CATEGORY, profile_key=client.profile
        )
        if not activate:
            log.info(_(u"Not activating message carbons as requested in params"))
            return
        try:
            yield self.host.checkFeatures(client, (NS_CARBONS,))
        except exceptions.FeatureNotFound:
            log.warning(_(u"server doesn't handle message carbons"))
        else:
            log.info(_(u"message carbons available, enabling it"))
            iq_elt = client.IQ()
            iq_elt.addElement((NS_CARBONS, "enable"))
            try:
                yield iq_elt.send()
            except StanzaError as e:
                log.warning(u"Can't activate message carbons: {}".format(e))
            else:
                log.info(_(u"message carbons activated"))

    def messageReceivedTrigger(self, client, message_elt, post_treat):
        """get message and handle it if carbons namespace is present"""
        carbons_elt = None
        for e in message_elt.elements():
            if e.uri == NS_CARBONS:
                carbons_elt = e
                break

        if carbons_elt is None:
            # this is not a message carbons,
            # we continue normal behaviour
            return True

        if message_elt["from"] != client.jid.userhost():
            log.warning(
                u"The message carbon received is not from our server, hack attempt?\n{xml}".format(
                    xml=message_elt.toXml()
                )
            )
            return
        forwarded_elt = next(carbons_elt.elements(C.NS_FORWARD, "forwarded"))
        cc_message_elt = next(forwarded_elt.elements(C.NS_CLIENT, "message"))

        # we replace the wrapping message with the CCed one
        # and continue the normal behaviour
        if carbons_elt.name == "received":
            message_elt["from"] = cc_message_elt["from"]
        elif carbons_elt.name == "sent":
            message_elt["to"] = cc_message_elt["to"]
        else:
            log.warning(
                u"invalid message carbons received:\n{xml}".format(
                    xml=message_elt.toXml()
                )
            )
            return False

        del message_elt.children[:]
        for c in cc_message_elt.children:
            message_elt.addChild(c)

        return True

class XEP_0280_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_CARBONS)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
