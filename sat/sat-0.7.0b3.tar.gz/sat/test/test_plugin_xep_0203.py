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

""" Plugin XEP-0203 """

from sat.test import helpers
from sat.plugins.plugin_xep_0203 import XEP_0203
from twisted.words.xish import domish
from twisted.words.protocols.jabber.jid import JID
from dateutil.tz import tzutc
import datetime

NS_PUBSUB = "http://jabber.org/protocol/pubsub"


class XEP_0203Test(helpers.SatTestCase):
    def setUp(self):
        self.host = helpers.FakeSAT()
        self.plugin = XEP_0203(self.host)

    def test_delay(self):
        delay_xml = """
          <delay xmlns='urn:xmpp:delay'
             from='capulet.com'
             stamp='2002-09-10T23:08:25Z'>
            Offline Storage
          </delay>
        """
        message_xml = (
            """
        <message
            from='romeo@montague.net/orchard'
            to='juliet@capulet.com'
            type='chat'>
          <body>text</body>
          %s
        </message>
        """
            % delay_xml
        )

        parent = domish.Element((None, "message"))
        parent["from"] = "romeo@montague.net/orchard"
        parent["to"] = "juliet@capulet.com"
        parent["type"] = "chat"
        parent.addElement("body", None, "text")
        stamp = datetime.datetime(2002, 9, 10, 23, 8, 25, tzinfo=tzutc())
        elt = self.plugin.delay(stamp, JID("capulet.com"), "Offline Storage", parent)
        self.assertEqualXML(elt.toXml(), delay_xml, True)
        self.assertEqualXML(parent.toXml(), message_xml, True)
