#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Delayed Delivery (XEP-0203)
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

from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)

from wokkel import disco, iwokkel, delay

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler
from zope.interface import implements


NS_DD = "urn:xmpp:delay"

PLUGIN_INFO = {
    C.PI_NAME: "Delayed Delivery",
    C.PI_IMPORT_NAME: "XEP-0203",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0203"],
    C.PI_MAIN: "XEP_0203",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Delayed Delivery"""),
}


class XEP_0203(object):
    def __init__(self, host):
        log.info(_("Delayed Delivery plugin initialization"))
        self.host = host

    def getHandler(self, client):
        return XEP_0203_handler(self, client.profile)

    def delay(self, stamp, sender=None, desc="", parent=None):
        """Build a delay element, eventually append it to the given parent element.

        @param stamp (datetime): offset-aware timestamp of the original sending.
        @param sender (JID): entity that originally sent or delayed the message.
        @param desc (unicode): optional natural language description.
        @param parent (domish.Element): add the delay element to this element.
        @return: the delay element (domish.Element)
        """
        elt = delay.Delay(stamp, sender).toElement()
        if desc:
            elt.addContent(desc)
        if parent:
            parent.addChild(elt)
        return elt


class XEP_0203_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent, profile):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host
        self.profile = profile

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_DD)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
