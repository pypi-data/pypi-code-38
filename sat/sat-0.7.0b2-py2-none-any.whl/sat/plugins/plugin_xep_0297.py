#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Stanza Forwarding (XEP-0297)
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
from sat.core.i18n import _, D_
from sat.core.log import getLogger

log = getLogger(__name__)

from wokkel import disco, iwokkel

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler
from zope.interface import implements

from twisted.words.xish import domish

PLUGIN_INFO = {
    C.PI_NAME: u"Stanza Forwarding",
    C.PI_IMPORT_NAME: u"XEP-0297",
    C.PI_TYPE: u"XEP",
    C.PI_PROTOCOLS: [u"XEP-0297"],
    C.PI_MAIN: "XEP_0297",
    C.PI_HANDLER: u"yes",
    C.PI_DESCRIPTION: D_(u"""Implementation of Stanza Forwarding"""),
}


class XEP_0297(object):
    # FIXME: check this implementation which doesn't seems to be used

    def __init__(self, host):
        log.info(_(u"Stanza Forwarding plugin initialization"))
        self.host = host

    def getHandler(self, client):
        return XEP_0297_handler(self, client.profile)

    @classmethod
    def updateUri(cls, element, uri):
        """Update recursively the element URI.

        @param element (domish.Element): element to update
        @param uri (unicode): new URI
        """
        # XXX: we need this because changing the URI of an existing element
        # containing children doesn't update the children's blank URI.
        element.uri = uri
        element.defaultUri = uri
        for child in element.children:
            if isinstance(child, domish.Element) and not child.uri:
                XEP_0297.updateUri(child, uri)

    def forward(self, stanza, to_jid, stamp, body="", profile_key=C.PROF_KEY_NONE):
        """Forward a message to the given JID.

        @param stanza (domish.Element): original stanza to be forwarded.
        @param to_jid (JID): recipient JID.
        @param stamp (datetime): offset-aware timestamp of the original reception.
        @param body (unicode): optional description.
        @param profile_key (unicode): %(doc_profile_key)s
        @return: a Deferred when the message has been sent
        """
        # FIXME: this method is not used and doesn't use mess_data which should be used for client.sendMessageData
        #        should it be deprecated? A method constructing the element without sending it seems more natural
        log.warning(
            u"THIS METHOD IS DEPRECATED"
        )  #  FIXME: we use this warning until we check the method
        msg = domish.Element((None, "message"))
        msg["to"] = to_jid.full()
        msg["type"] = stanza["type"]

        body_elt = domish.Element((None, "body"))
        if body:
            body_elt.addContent(body)

        forwarded_elt = domish.Element((C.NS_FORWARD, "forwarded"))
        delay_elt = self.host.plugins["XEP-0203"].delay(stamp)
        forwarded_elt.addChild(delay_elt)
        if not stanza.uri:  # None or ''
            XEP_0297.updateUri(stanza, "jabber:client")
        forwarded_elt.addChild(stanza)

        msg.addChild(body_elt)
        msg.addChild(forwarded_elt)

        client = self.host.getClient(profile_key)
        return client.sendMessageData({u"xml": msg})


class XEP_0297_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent, profile):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host
        self.profile = profile

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(C.NS_FORWARD)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
