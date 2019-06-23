#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Delayed Delivery (XEP-0199)
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

from sat.core.i18n import _, D_
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core.constants import Const as C
from wokkel import disco, iwokkel
from twisted.words.protocols.jabber import xmlstream, jid
from zope.interface import implements
import time


PLUGIN_INFO = {
    C.PI_NAME: u"XMPP PING",
    C.PI_IMPORT_NAME: u"XEP-0199",
    C.PI_TYPE: u"XEP",
    C.PI_PROTOCOLS: [u"XEP-199"],
    C.PI_MAIN: "XEP_0199",
    C.PI_HANDLER: u"yes",
    C.PI_DESCRIPTION: D_(u"""Implementation of XMPP Ping"""),
}

NS_PING = u"urn:xmpp:ping"
PING_REQUEST = C.IQ_GET + '/ping[@xmlns="' + NS_PING + '"]'


class XEP_0199(object):

    def __init__(self, host):
        log.info(_("XMPP Ping plugin initialization"))
        self.host = host
        host.bridge.addMethod(
            "ping", ".plugin", in_sign='ss', out_sign='d', method=self._ping, async=True)
        try:
            self.text_cmds = self.host.plugins[C.TEXT_CMDS]
        except KeyError:
            log.info(_(u"Text commands not available"))
        else:
            self.text_cmds.registerTextCommands(self)

    def getHandler(self, client):
        return XEP_0199_handler(self)

    def _pingRaiseIfFailure(self, pong):
        """If ping didn't succeed, raise the failure, else return pong delay"""
        if pong[0] != u"PONG":
            raise pong[0]
        return pong[1]

    def _ping(self, jid_s, profile):
        client = self.host.getClient(profile)
        entity_jid = jid.JID(jid_s)
        d = self.ping(client, entity_jid)
        d.addCallback(self._pingRaiseIfFailure)
        return d

    def _pingCb(self, iq_result, send_time):
        receive_time = time.time()
        return (u"PONG", receive_time - send_time)

    def _pingEb(self, failure_, send_time):
        receive_time = time.time()
        return (failure_.value, receive_time - send_time)

    def ping(self, client, entity_jid):
        """Ping an XMPP entity

        @param entity_jid(jid.JID): entity to ping
        @return (tuple[(unicode,failure), float]): pong data:
            - either u"PONG" if it was successful, or failure
            - delay between sending time and reception time
        """
        iq_elt = client.IQ("get")
        iq_elt["to"] = entity_jid.full()
        iq_elt.addElement((NS_PING, "ping"))
        d = iq_elt.send()
        send_time = time.time()
        d.addCallback(self._pingCb, send_time)
        d.addErrback(self._pingEb, send_time)
        return d

    def _cmd_ping_fb(self, pong, client, mess_data):
        """Send feedback to client when pong data is received"""
        txt_cmd = self.host.plugins[C.TEXT_CMDS]

        if pong[0] == u"PONG":
            txt_cmd.feedBack(client, u"PONG ({time} s)".format(time=pong[1]), mess_data)
        else:
            txt_cmd.feedBack(
                client, _(u"ping error ({err_msg}). Response time: {time} s")
                .format(err_msg=pong[0], time=pong[1]), mess_data)

    def cmd_ping(self, client, mess_data):
        """ping an entity

        @command (all): [JID]
            - JID: jid of the entity to ping
        """
        if mess_data["unparsed"].strip():
            try:
                entity_jid = jid.JID(mess_data["unparsed"].strip())
            except RuntimeError:
                txt_cmd = self.host.plugins[C.TEXT_CMDS]
                txt_cmd.feedBack(client, _(u'Invalid jid: "{entity_jid}"').format(
                    entity_jid=mess_data["unparsed"].strip()), mess_data)
                return False
        else:
            entity_jid = mess_data["to"]
        d = self.ping(client, entity_jid)
        d.addCallback(self._cmd_ping_fb, client, mess_data)

        return False

    def onPingRequest(self, iq_elt, client):
        log.info(_(u"XMPP PING received from {from_jid} [{profile}]").format(
            from_jid=iq_elt["from"], profile=client.profile))
        iq_elt.handled = True
        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        client.send(iq_result_elt)


class XEP_0199_handler(xmlstream.XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent

    def connectionInitialized(self):
        self.xmlstream.addObserver(
            PING_REQUEST, self.plugin_parent.onPingRequest, client=self.parent
        )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_PING)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
