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

""" Plugin XEP-0297 """

from constants import Const as C
from sat.test import helpers
from sat.plugins.plugin_xep_0203 import XEP_0203
from sat.plugins.plugin_xep_0297 import XEP_0297
from twisted.words.protocols.jabber.jid import JID
from dateutil.tz import tzutc
import datetime
from wokkel.generic import parseXml


NS_PUBSUB = "http://jabber.org/protocol/pubsub"


class XEP_0297Test(helpers.SatTestCase):
    def setUp(self):
        self.host = helpers.FakeSAT()
        self.plugin = XEP_0297(self.host)
        self.host.plugins["XEP-0203"] = XEP_0203(self.host)

    def test_delay(self):
        stanza = parseXml(
            """
          <message from='juliet@capulet.lit/orchard'
                   id='0202197'
                   to='romeo@montague.lit'
                   type='chat'>
            <body>Yet I should kill thee with much cherishing.</body>
            <mood xmlns='http://jabber.org/protocol/mood'>
                <amorous/>
            </mood>
          </message>
        """.encode(
                "utf-8"
            )
        )
        output = """
          <message to='mercutio@verona.lit' type='chat'>
            <body>A most courteous exposition!</body>
            <forwarded xmlns='urn:xmpp:forward:0'>
              <delay xmlns='urn:xmpp:delay' stamp='2010-07-10T23:08:25Z'/>
              <message from='juliet@capulet.lit/orchard'
                       id='0202197'
                       to='romeo@montague.lit'
                       type='chat'
                       xmlns='jabber:client'>
                  <body>Yet I should kill thee with much cherishing.</body>
                  <mood xmlns='http://jabber.org/protocol/mood'>
                      <amorous/>
                  </mood>
              </message>
            </forwarded>
          </message>
        """
        stamp = datetime.datetime(2010, 7, 10, 23, 8, 25, tzinfo=tzutc())
        d = self.plugin.forward(
            stanza,
            JID("mercutio@verona.lit"),
            stamp,
            body="A most courteous exposition!",
            profile_key=C.PROFILE[0],
        )
        d.addCallback(
            lambda __: self.assertEqualXML(
                self.host.getSentMessageXml(0), output, True
            )
        )
        return d
