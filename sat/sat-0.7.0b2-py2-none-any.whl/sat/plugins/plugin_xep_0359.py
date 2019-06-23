#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Message Archive Management (XEP-0359)
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)
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

from sat.core.constants import Const as C
from sat.core import exceptions
from sat.core.i18n import _
from sat.core.log import getLogger
from twisted.words.protocols.jabber import xmlstream
from zope.interface import implements
from wokkel import disco

log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: u"Unique and Stable Stanza IDs",
    C.PI_IMPORT_NAME: u"XEP-0359",
    C.PI_TYPE: u"XEP",
    C.PI_PROTOCOLS: [u"XEP-0359"],
    C.PI_MAIN: u"XEP_0359",
    C.PI_HANDLER: u"yes",
    C.PI_DESCRIPTION: _(u"""Implementation of Unique and Stable Stanza IDs"""),
}

NS_SID = u"urn:xmpp:sid:0"


class XEP_0359(object):

    def __init__(self, host):
        log.info(_(u"Unique and Stable Stanza IDs plugin initialization"))
        self.host = host
        host.registerNamespace(u"stanza_id", NS_SID)
        host.trigger.add(u"message_parse", self._message_parseTrigger)

    def _message_parseTrigger(self, client, message_elt, mess_data):
        """Check if message has a stanza-id"""
        stanza_id = self.getStanzaId(message_elt, client.jid.userhostJID())
        if stanza_id is not None:
            mess_data[u'extra'][u'stanza_id'] = stanza_id
        return True

    def getStanzaId(self, element, by):
        """Return stanza-id if found in element

        @param element(domish.Element): element to parse
        @param by(jid.JID): entity which should have set a stanza-id
        @return (unicode, None): stanza-id if found
        """
        stanza_id = None
        for stanza_elt in element.elements(NS_SID, u"stanza-id"):
            if stanza_elt.getAttribute(u"by") == by.full():
                if stanza_id is not None:
                    # we must not have more than one element (§3 #4)
                    raise exceptions.DataError(
                        u"More than one corresponding stanza-id found!")
                stanza_id = stanza_elt.getAttribute(u"id")
                # we don't break to be sure that there is no more than one element
                # with this "by" attribute

        return stanza_id

    def addStanzaId(self, client, element, stanza_id, by=None):
        """Add a <stanza-id/> to a stanza

        @param element(domish.Element): stanza where the <stanza-id/> must be added
        @param stanza_id(unicode): id to use
        @param by(jid.JID, None): jid to use or None to use client.jid
        """
        sid_elt = element.addElement((NS_SID, u"stanza-id"))
        sid_elt[u"by"] = client.jid.userhost() if by is None else by.userhost()
        sid_elt[u"id"] = stanza_id

    def getHandler(self, client):
        return XEP_0359_handler()


class XEP_0359_handler(xmlstream.XMPPHandler):
    implements(disco.IDisco)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_SID)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
