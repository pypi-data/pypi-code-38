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

""" Plugin extended addressing stanzas """

from constants import Const
from sat.test import helpers
from sat.plugins import plugin_xep_0033 as plugin
from sat.core.exceptions import CancelError
from twisted.internet import defer
from wokkel.generic import parseXml
from twisted.words.protocols.jabber.jid import JID

PROFILE_INDEX = 0
PROFILE = Const.PROFILE[PROFILE_INDEX]
JID_STR_FROM = Const.JID_STR[1]
JID_STR_TO = Const.PROFILE_DICT[PROFILE].host
JID_STR_X_TO = Const.JID_STR[0]
JID_STR_X_CC = Const.JID_STR[1]
JID_STR_X_BCC = Const.JID_STR[2]

ADDRS = ("to", JID_STR_X_TO, "cc", JID_STR_X_CC, "bcc", JID_STR_X_BCC)


class XEP_0033Test(helpers.SatTestCase):
    def setUp(self):
        self.host = helpers.FakeSAT()
        self.plugin = plugin.XEP_0033(self.host)

    def test_messageReceived(self):
        self.host.memory.reinit()
        xml = u"""
        <message type="chat" from="%s" to="%s" id="test_1">
            <body>test</body>
            <addresses xmlns='http://jabber.org/protocol/address'>
                <address type='to' jid='%s'/>
                <address type='cc' jid='%s'/>
                <address type='bcc' jid='%s'/>
            </addresses>
        </message>
        """ % (
            JID_STR_FROM,
            JID_STR_TO,
            JID_STR_X_TO,
            JID_STR_X_CC,
            JID_STR_X_BCC,
        )
        stanza = parseXml(xml.encode("utf-8"))
        treatments = defer.Deferred()
        self.plugin.messageReceivedTrigger(
            self.host.getClient(PROFILE), stanza, treatments
        )
        data = {"extra": {}}

        def cb(data):
            expected = ("to", JID_STR_X_TO, "cc", JID_STR_X_CC, "bcc", JID_STR_X_BCC)
            msg = "Expected: %s\nGot:      %s" % (expected, data["extra"]["addresses"])
            self.assertEqual(
                data["extra"]["addresses"], "%s:%s\n%s:%s\n%s:%s\n" % expected, msg
            )

        treatments.addCallback(cb)
        return treatments.callback(data)

    def _get_mess_data(self):
        mess_data = {
            "to": JID(JID_STR_TO),
            "type": "chat",
            "message": "content",
            "extra": {},
        }
        mess_data["extra"]["address"] = "%s:%s\n%s:%s\n%s:%s\n" % ADDRS
        original_stanza = u"""
        <message type="chat" from="%s" to="%s" id="test_1">
            <body>content</body>
        </message>
        """ % (
            JID_STR_FROM,
            JID_STR_TO,
        )
        mess_data["xml"] = parseXml(original_stanza.encode("utf-8"))
        return mess_data

    def _assertAddresses(self, mess_data):
        """The mess_data that we got here has been modified by self.plugin.messageSendTrigger,
        check that the addresses element has been added to the stanza."""
        expected = self._get_mess_data()["xml"]
        addresses_extra = (
            """
        <addresses xmlns='http://jabber.org/protocol/address'>
            <address type='%s' jid='%s'/>
            <address type='%s' jid='%s'/>
            <address type='%s' jid='%s'/>
        </addresses>"""
            % ADDRS
        )
        addresses_element = parseXml(addresses_extra.encode("utf-8"))
        expected.addChild(addresses_element)
        self.assertEqualXML(
            mess_data["xml"].toXml().encode("utf-8"), expected.toXml().encode("utf-8")
        )

    def _checkSentAndStored(self):
        """Check that all the recipients got their messages and that the history has been filled.
        /!\ see the comments in XEP_0033.sendAndStoreMessage"""
        sent = []
        stored = []
        d_list = []

        def cb(entities, to_jid):
            if host in entities:
                if (
                    host not in sent
                ):  # send the message to the entity offering the feature
                    sent.append(host)
                    stored.append(host)
                stored.append(to_jid)  # store in history for each recipient
            else:  # feature not supported, use normal behavior
                sent.append(to_jid)
                stored.append(to_jid)
            helpers.unmuteLogging()

        for to_s in (JID_STR_X_TO, JID_STR_X_CC, JID_STR_X_BCC):
            to_jid = JID(to_s)
            host = JID(to_jid.host)
            helpers.muteLogging()
            d = self.host.findFeaturesSet([plugin.NS_ADDRESS], jid_=host, profile=PROFILE)
            d.addCallback(cb, to_jid)
            d_list.append(d)

        def cb_list(__):
            msg = "/!\ see the comments in XEP_0033.sendAndStoreMessage"
            sent_recipients = [
                JID(elt["to"]) for elt in self.host.getSentMessages(PROFILE_INDEX)
            ]
            self.assertEqualUnsortedList(sent_recipients, sent, msg)
            self.assertEqualUnsortedList(self.host.stored_messages, stored, msg)

        return defer.DeferredList(d_list).addCallback(cb_list)

    def _trigger(self, data):
        """Execute self.plugin.messageSendTrigger with a different logging
        level to not pollute the output, then check that the plugin did its
        job. It should abort sending the message or add the extended
        addressing information to the stanza.
        @param data: the data to be processed by self.plugin.messageSendTrigger
        """
        pre_treatments = defer.Deferred()
        post_treatments = defer.Deferred()
        helpers.muteLogging()
        self.plugin.messageSendTrigger(
            self.host.getClient[PROFILE], data, pre_treatments, post_treatments
        )
        post_treatments.callback(data)
        helpers.unmuteLogging()
        post_treatments.addCallbacks(
            self._assertAddresses, lambda failure: failure.trap(CancelError)
        )
        return post_treatments

    def test_messageSendTriggerFeatureNotSupported(self):
        # feature is not supported, abort the message
        self.host.memory.reinit()
        data = self._get_mess_data()
        return self._trigger(data)

    def test_messageSendTriggerFeatureSupported(self):
        # feature is supported by the main target server
        self.host.reinit()
        self.host.addFeature(JID(JID_STR_TO), plugin.NS_ADDRESS, PROFILE)
        data = self._get_mess_data()
        d = self._trigger(data)
        return d.addCallback(lambda __: self._checkSentAndStored())

    def test_messageSendTriggerFeatureFullySupported(self):
        # feature is supported by all target servers
        self.host.reinit()
        self.host.addFeature(JID(JID_STR_TO), plugin.NS_ADDRESS, PROFILE)
        for dest in (JID_STR_X_TO, JID_STR_X_CC, JID_STR_X_BCC):
            self.host.addFeature(JID(JID(dest).host), plugin.NS_ADDRESS, PROFILE)
        data = self._get_mess_data()
        d = self._trigger(data)
        return d.addCallback(lambda __: self._checkSentAndStored())

    def test_messageSendTriggerFixWrongEntity(self):
        # check that a wrong recipient entity is fixed by the backend
        self.host.reinit()
        self.host.addFeature(JID(JID_STR_TO), plugin.NS_ADDRESS, PROFILE)
        for dest in (JID_STR_X_TO, JID_STR_X_CC, JID_STR_X_BCC):
            self.host.addFeature(JID(JID(dest).host), plugin.NS_ADDRESS, PROFILE)
        data = self._get_mess_data()
        data["to"] = JID(JID_STR_X_TO)
        d = self._trigger(data)
        return d.addCallback(lambda __: self._checkSentAndStored())
