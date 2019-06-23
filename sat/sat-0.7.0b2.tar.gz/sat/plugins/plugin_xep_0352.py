#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Explicit Message Encryption
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

from twisted.words.xish import domish
from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)

PLUGIN_INFO = {
    C.PI_NAME: u"Client State Indication",
    C.PI_IMPORT_NAME: u"XEP-0352",
    C.PI_TYPE: C.PLUG_TYPE_XEP,
    C.PI_PROTOCOLS: [u"XEP-0352"],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: u"XEP_0352",
    C.PI_HANDLER: u"no",
    C.PI_DESCRIPTION: D_(u"Notify server when frontend is not actively used, to limit "
                         u"traffic and save bandwidth and battery life"),
}

NS_CSI = u"urn:xmpp:csi:0"


class XEP_0352(object):

    def __init__(self, host):
        log.info(_(u"Client State Indication plugin initialization"))
        self.host = host
        host.registerNamespace(u"csi", NS_CSI)

    def isActive(self, client):
        try:
            if not client._xep_0352_enabled:
                return True
            return client._xep_0352_active
        except AttributeError:
            # _xep_0352_active can not be set if isActive is called before
            # profileConnected has been called
            log.debug(u"isActive called when XEP-0352 plugin has not yet set the "
                      u"attributes")
            return True

    def profileConnected(self, client):
        if (NS_CSI, u'csi') in client.xmlstream.features:
            log.info(_(u"Client State Indication is available on this server"))
            client._xep_0352_enabled = True
            client._xep_0352_active = True
        else:
            log.warning(_(u"Client State Indication is not available on this server, some"
                          u" bandwidth optimisations can't be used."))
            client._xep_0352_enabled = False

    def setInactive(self, client):
        if self.isActive(client):
            inactive_elt = domish.Element((NS_CSI, u'inactive'))
            client.send(inactive_elt)
            client._xep_0352_active = False
            log.info(u"inactive state set")

    def setActive(self, client):
        if not self.isActive(client):
            active_elt = domish.Element((NS_CSI, u'active'))
            client.send(active_elt)
            client._xep_0352_active = True
            log.info(u"active state set")
