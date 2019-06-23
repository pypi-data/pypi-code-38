#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
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

from sat.test import helpers
from constants import Const
from twisted.trial import unittest
from sat.core import xmpp
from twisted.words.protocols.jabber.jid import JID
from wokkel.generic import parseXml
from wokkel.xmppim import RosterItem


class SatXMPPClientTest(unittest.TestCase):

    def setUp(self):
        self.host = helpers.FakeSAT()
        self.client = xmpp.SatXMPPClient(self.host, Const.PROFILE[0], JID("test@example.org"), "test")

    def test_init(self):
        """Check that init values are correctly initialised"""
        self.assertEqual(self.client.profile, Const.PROFILE[0])
        print self.client.host
        self.assertEqual(self.client.host_app, self.host)


class SatMessageProtocolTest(unittest.TestCase):

    def setUp(self):
        self.host = helpers.FakeSAT()
        self.message = xmpp.SatMessageProtocol(self.host)
        self.message.parent = helpers.FakeClient(self.host)

    def test_onMessage(self):
        xml = """
        <message type="chat" from="sender@example.net/house" to="test@example.org/SàT" id="test_1">
        <body>test</body>
        </message>
        """
        stanza = parseXml(xml)
        self.host.bridge.expectCall("messageNew", u"sender@example.net/house", u"test", u"chat", u"test@example.org/SàT", {}, profile=Const.PROFILE[0])
        self.message.onMessage(stanza)


class SatRosterProtocolTest(unittest.TestCase):

    def setUp(self):
        self.host = helpers.FakeSAT()
        self.roster = xmpp.SatRosterProtocol(self.host)
        self.roster.parent = helpers.FakeClient(self.host)

    def test__registerItem(self):
        roster_item = RosterItem(Const.JID[0])
        roster_item.name = u"Test Man"
        roster_item.subscriptionTo = True
        roster_item.subscriptionFrom = True
        roster_item.ask = False
        roster_item.groups = set([u"Test Group 1", u"Test Group 2", u"Test Group 3"])
        self.host.bridge.expectCall("newContact", Const.JID_STR[0], {'to': 'True', 'from': 'True', 'ask': 'False', 'name': u'Test Man'}, set([u"Test Group 1", u"Test Group 2", u"Test Group 3"]), Const.PROFILE[0])
        self.roster._registerItem(roster_item)


class SatPresenceProtocolTest(unittest.TestCase):

    def setUp(self):
        self.host = helpers.FakeSAT()
        self.presence = xmpp.SatPresenceProtocol(self.host)
        self.presence.parent = helpers.FakeClient(self.host)

    def test_availableReceived(self):
        self.host.bridge.expectCall("presenceUpdate", Const.JID_STR[0], "xa", 15, {'default': "test status", 'fr': 'statut de test'}, Const.PROFILE[0])
        self.presence.availableReceived(Const.JID[0], 'xa', {None: "test status", 'fr': 'statut de test'}, 15)

    def test_availableReceived_empty_statuses(self):
        self.host.bridge.expectCall("presenceUpdate", Const.JID_STR[0], "xa", 15, {}, Const.PROFILE[0])
        self.presence.availableReceived(Const.JID[0], 'xa', None, 15)

    def test_unavailableReceived(self):
        self.host.bridge.expectCall("presenceUpdate", Const.JID_STR[0], "unavailable", 0, {}, Const.PROFILE[0])
        self.presence.unavailableReceived(Const.JID[0], None)

    def test_subscribedReceived(self):
        self.host.bridge.expectCall("subscribe", "subscribed", Const.JID[0].userhost(), Const.PROFILE[0])
        self.presence.subscribedReceived(Const.JID[0])

    def test_unsubscribedReceived(self):
        self.host.bridge.expectCall("subscribe", "unsubscribed", Const.JID[0].userhost(), Const.PROFILE[0])
        self.presence.unsubscribedReceived(Const.JID[0])

    def test_subscribeReceived(self):
        self.host.bridge.expectCall("subscribe", "subscribe", Const.JID[0].userhost(), Const.PROFILE[0])
        self.presence.subscribeReceived(Const.JID[0])

    def test_unsubscribeReceived(self):
        self.host.bridge.expectCall("subscribe", "unsubscribe", Const.JID[0].userhost(), Const.PROFILE[0])
        self.presence.unsubscribeReceived(Const.JID[0])
