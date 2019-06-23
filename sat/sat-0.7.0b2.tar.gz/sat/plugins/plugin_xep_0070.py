#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT plugin for managing xep-0070
# Copyright (C) 2009-2016 Geoffrey POUZET (chteufleur@kingpenguin.tk)

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
from sat.core.constants import Const as C
from sat.core.log import getLogger
from twisted.words.protocols.jabber import xmlstream
from twisted.words.protocols import jabber

log = getLogger(__name__)
from sat.tools import xml_tools

from wokkel import disco, iwokkel
from zope.interface import implements

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler


NS_HTTP_AUTH = "http://jabber.org/protocol/http-auth"

IQ = "iq"
IQ_GET = "/" + IQ + '[@type="get"]'
IQ_HTTP_AUTH_REQUEST = IQ_GET + '/confirm[@xmlns="' + NS_HTTP_AUTH + '"]'

MSG = "message"
MSG_GET = "/" + MSG + '[@type="normal"]'
MSG_HTTP_AUTH_REQUEST = MSG_GET + '/confirm[@xmlns="' + NS_HTTP_AUTH + '"]'


PLUGIN_INFO = {
    C.PI_NAME: "XEP-0070 Plugin",
    C.PI_IMPORT_NAME: "XEP-0070",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0070"],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "XEP_0070",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of HTTP Requests via XMPP"""),
}


class XEP_0070(object):
    """
    Implementation for XEP 0070.
    """

    def __init__(self, host):
        log.info(_(u"Plugin XEP_0070 initialization"))
        self.host = host
        self._dictRequest = dict()

    def getHandler(self, client):
        return XEP_0070_handler(self, client.profile)

    def onHttpAuthRequestIQ(self, iq_elt, client):
        """This method is called on confirmation request received (XEP-0070 #4.5)

        @param iq_elt: IQ element
        @param client: %(doc_client)s
        """
        log.info(_("XEP-0070 Verifying HTTP Requests via XMPP (iq)"))
        self._treatHttpAuthRequest(iq_elt, IQ, client)

    def onHttpAuthRequestMsg(self, msg_elt, client):
        """This method is called on confirmation request received (XEP-0070 #4.5)

        @param msg_elt: message element
        @param client: %(doc_client)s
        """
        log.info(_("XEP-0070 Verifying HTTP Requests via XMPP (message)"))
        self._treatHttpAuthRequest(msg_elt, MSG, client)

    def _treatHttpAuthRequest(self, elt, stanzaType, client):
        elt.handled = True
        auth_elt = elt.elements(NS_HTTP_AUTH, "confirm").next()
        auth_id = auth_elt["id"]
        auth_method = auth_elt["method"]
        auth_url = auth_elt["url"]
        self._dictRequest[client] = (auth_id, auth_method, auth_url, stanzaType, elt)
        title = D_(u"Auth confirmation")
        message = D_(u"{auth_url} needs to validate your identity, do you agree?\n"
                     u"Validation code : {auth_id}\n\n"
                     u"Please check that this code is the same as on {auth_url}"
                    ).format(auth_url=auth_url, auth_id=auth_id)
        d = xml_tools.deferConfirm(self.host, message=message, title=title,
            profile=client.profile)
        d.addCallback(self._authRequestCallback, client)

    def _authRequestCallback(self, authorized, client):
        try:
            auth_id, auth_method, auth_url, stanzaType, elt = self._dictRequest.pop(
                client)
        except KeyError:
            authorized = False

        if authorized:
            if stanzaType == IQ:
                # iq
                log.debug(_(u"XEP-0070 reply iq"))
                iq_result_elt = xmlstream.toResponse(elt, "result")
                client.send(iq_result_elt)
            elif stanzaType == MSG:
                # message
                log.debug(_(u"XEP-0070 reply message"))
                msg_result_elt = xmlstream.toResponse(elt, "result")
                msg_result_elt.addChild(elt.elements(NS_HTTP_AUTH, "confirm").next())
                client.send(msg_result_elt)
        else:
            log.debug(_(u"XEP-0070 reply error"))
            result_elt = jabber.error.StanzaError("not-authorized").toResponse(elt)
            client.send(result_elt)


class XEP_0070_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent, profile):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host
        self.profile = profile

    def connectionInitialized(self):
        self.xmlstream.addObserver(
            IQ_HTTP_AUTH_REQUEST,
            self.plugin_parent.onHttpAuthRequestIQ,
            client=self.parent,
        )
        self.xmlstream.addObserver(
            MSG_HTTP_AUTH_REQUEST,
            self.plugin_parent.onHttpAuthRequestMsg,
            client=self.parent,
        )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_HTTP_AUTH)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
