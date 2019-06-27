#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
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

""" Plugin chat states notification tests """

from constants import Const
from sat.test import helpers
from sat.core.constants import Const as C
from sat.plugins import plugin_xep_0085 as plugin
from copy import deepcopy
from twisted.internet import defer
from wokkel.generic import parseXml


class XEP_0085Test(helpers.SatTestCase):
    def setUp(self):
        self.host = helpers.FakeSAT()
        self.plugin = plugin.XEP_0085(self.host)
        self.host.memory.setParam(
            plugin.PARAM_NAME,
            True,
            plugin.PARAM_KEY,
            C.NO_SECURITY_LIMIT,
            Const.PROFILE[0],
        )

    def test_messageReceived(self):
        for state in plugin.CHAT_STATES:
            xml = u"""
            <message type="chat" from="%s" to="%s" id="test_1">
            %s
            <%s xmlns='%s'/>
            </message>
            """ % (
                Const.JID_STR[1],
                Const.JID_STR[0],
                "<body>test</body>" if state == "active" else "",
                state,
                plugin.NS_CHAT_STATES,
            )
            stanza = parseXml(xml.encode("utf-8"))
            self.host.bridge.expectCall(
                "chatStateReceived", Const.JID_STR[1], state, Const.PROFILE[0]
            )
            self.plugin.messageReceivedTrigger(
                self.host.getClient(Const.PROFILE[0]), stanza, None
            )

    def test_messageSendTrigger(self):
        def cb(data):
            xml = data["xml"].toXml().encode("utf-8")
            self.assertEqualXML(xml, expected.toXml().encode("utf-8"))

        d_list = []

        for state in plugin.CHAT_STATES:
            mess_data = {
                "to": Const.JID[0],
                "type": "chat",
                "message": "content",
                "extra": {} if state == "active" else {"chat_state": state},
            }
            stanza = u"""
            <message type="chat" from="%s" to="%s" id="test_1">
            %s
            </message>
            """ % (
                Const.JID_STR[1],
                Const.JID_STR[0],
                ("<body>%s</body>" % mess_data["message"]) if state == "active" else "",
            )
            mess_data["xml"] = parseXml(stanza.encode("utf-8"))
            expected = deepcopy(mess_data["xml"])
            expected.addElement(state, plugin.NS_CHAT_STATES)
            post_treatments = defer.Deferred()
            self.plugin.messageSendTrigger(
                self.host.getClient(Const.PROFILE[0]), mess_data, None, post_treatments
            )

            post_treatments.addCallback(cb)
            post_treatments.callback(mess_data)
            d_list.append(post_treatments)

        def cb_list(__):  # cancel the timer to not block the process
            self.plugin.map[Const.PROFILE[0]][Const.JID[0]].timer.cancel()

        return defer.DeferredList(d_list).addCallback(cb_list)
