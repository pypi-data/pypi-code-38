#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT plugin for managing xep-0184
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
from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core.log import getLogger
from twisted.internet import reactor
from twisted.words.protocols.jabber import xmlstream, jid
from twisted.words.xish import domish

log = getLogger(__name__)

from wokkel import disco, iwokkel
from zope.interface import implements

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler


NS_MESSAGE_DELIVERY_RECEIPTS = "urn:xmpp:receipts"

MSG = "message"

MSG_CHAT = "/" + MSG + '[@type="chat"]'
MSG_CHAT_MESSAGE_DELIVERY_RECEIPTS_REQUEST = (
    MSG_CHAT + '/request[@xmlns="' + NS_MESSAGE_DELIVERY_RECEIPTS + '"]'
)
MSG_CHAT_MESSAGE_DELIVERY_RECEIPTS_RECEIVED = (
    MSG_CHAT + '/received[@xmlns="' + NS_MESSAGE_DELIVERY_RECEIPTS + '"]'
)

MSG_NORMAL = "/" + MSG + '[@type="normal"]'
MSG_NORMAL_MESSAGE_DELIVERY_RECEIPTS_REQUEST = (
    MSG_NORMAL + '/request[@xmlns="' + NS_MESSAGE_DELIVERY_RECEIPTS + '"]'
)
MSG_NORMAL_MESSAGE_DELIVERY_RECEIPTS_RECEIVED = (
    MSG_NORMAL + '/received[@xmlns="' + NS_MESSAGE_DELIVERY_RECEIPTS + '"]'
)


PARAM_KEY = "Privacy"
PARAM_NAME = "Enable message delivery receipts"
ENTITY_KEY = PARAM_KEY + "_" + PARAM_NAME


PLUGIN_INFO = {
    C.PI_NAME: "XEP-0184 Plugin",
    C.PI_IMPORT_NAME: "XEP-0184",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0184"],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "XEP_0184",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Message Delivery Receipts"""),
}


STATUS_MESSAGE_DELIVERY_RECEIVED = "delivered"
TEMPO_DELETE_WAITING_ACK_S = 300  # 5 min


class XEP_0184(object):
    """
    Implementation for XEP 0184.
    """

    params = """
    <params>
    <individual>
    <category name="%(category_name)s" label="%(category_label)s">
        <param name="%(param_name)s" label="%(param_label)s" value="true" type="bool" security="0"/>
     </category>
    </individual>
    </params>
    """ % {
        "category_name": PARAM_KEY,
        "category_label": _(PARAM_KEY),
        "param_name": PARAM_NAME,
        "param_label": _("Enable message delivery receipts"),
    }

    def __init__(self, host):
        log.info(_("Plugin XEP_0184 (message delivery receipts) initialization"))
        self.host = host
        self._dictRequest = dict()

        # parameter value is retrieved before each use
        host.memory.updateParams(self.params)

        host.trigger.add("sendMessage", self.sendMessageTrigger)
        host.bridge.addSignal(
            "messageState", ".plugin", signature="sss"
        )  # message_uid, status, profile

    def getHandler(self, client):
        return XEP_0184_handler(self, client.profile)

    def sendMessageTrigger(
        self, client, mess_data, pre_xml_treatments, post_xml_treatments
    ):
        """Install SendMessage command hook """

        def treatment(mess_data):
            message = mess_data["xml"]
            message_type = message.getAttribute("type")

            if self._isActif(client.profile) and (
                message_type == "chat" or message_type == "normal"
            ):
                message.addElement("request", NS_MESSAGE_DELIVERY_RECEIPTS)
                uid = mess_data["uid"]
                msg_id = message.getAttribute("id")
                self._dictRequest[msg_id] = uid
                reactor.callLater(
                    TEMPO_DELETE_WAITING_ACK_S, self._clearDictRequest, msg_id
                )
                log.debug(
                    _(
                        "[XEP-0184] Request acknowledgment for message id {}".format(
                            msg_id
                        )
                    )
                )

            return mess_data

        post_xml_treatments.addCallback(treatment)
        return True

    def onMessageDeliveryReceiptsRequest(self, msg_elt, client):
        """This method is called on message delivery receipts **request** (XEP-0184 #7)
        @param msg_elt: message element
        @param client: %(doc_client)s"""
        from_jid = jid.JID(msg_elt["from"])

        if self._isActif(client.profile) and client.roster.isPresenceAuthorised(from_jid):
            received_elt_ret = domish.Element((NS_MESSAGE_DELIVERY_RECEIPTS, "received"))
            received_elt_ret["id"] = msg_elt["id"]

            msg_result_elt = xmlstream.toResponse(msg_elt, "result")
            msg_result_elt.addChild(received_elt_ret)
            client.send(msg_result_elt)

    def onMessageDeliveryReceiptsReceived(self, msg_elt, client):
        """This method is called on message delivery receipts **received** (XEP-0184 #7)
        @param msg_elt: message element
        @param client: %(doc_client)s"""
        msg_elt.handled = True
        rcv_elt = msg_elt.elements(NS_MESSAGE_DELIVERY_RECEIPTS, "received").next()
        msg_id = rcv_elt["id"]

        try:
            uid = self._dictRequest[msg_id]
            del self._dictRequest[msg_id]
            self.host.bridge.messageState(
                uid, STATUS_MESSAGE_DELIVERY_RECEIVED, client.profile
            )
            log.debug(
                _("[XEP-0184] Receive acknowledgment for message id {}".format(msg_id))
            )
        except KeyError:
            pass

    def _clearDictRequest(self, msg_id):
        try:
            del self._dictRequest[msg_id]
            log.debug(
                _(
                    "[XEP-0184] Delete waiting acknowledgment for message id {}".format(
                        msg_id
                    )
                )
            )
        except KeyError:
            pass

    def _isActif(self, profile):
        return self.host.memory.getParamA(PARAM_NAME, PARAM_KEY, profile_key=profile)


class XEP_0184_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent, profile):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host
        self.profile = profile

    def connectionInitialized(self):
        self.xmlstream.addObserver(
            MSG_CHAT_MESSAGE_DELIVERY_RECEIPTS_REQUEST,
            self.plugin_parent.onMessageDeliveryReceiptsRequest,
            client=self.parent,
        )
        self.xmlstream.addObserver(
            MSG_CHAT_MESSAGE_DELIVERY_RECEIPTS_RECEIVED,
            self.plugin_parent.onMessageDeliveryReceiptsReceived,
            client=self.parent,
        )

        self.xmlstream.addObserver(
            MSG_NORMAL_MESSAGE_DELIVERY_RECEIPTS_REQUEST,
            self.plugin_parent.onMessageDeliveryReceiptsRequest,
            client=self.parent,
        )
        self.xmlstream.addObserver(
            MSG_NORMAL_MESSAGE_DELIVERY_RECEIPTS_RECEIVED,
            self.plugin_parent.onMessageDeliveryReceiptsReceived,
            client=self.parent,
        )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_MESSAGE_DELIVERY_RECEIPTS)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
