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

""" Plugin XEP-0334 """

from constants import Const as C
from sat.test import helpers
from sat.plugins.plugin_xep_0334 import XEP_0334
from twisted.internet import defer
from wokkel.generic import parseXml
from sat.core import exceptions

HINTS = ("no-permanent-storage", "no-storage", "no-copy")


class XEP_0334Test(helpers.SatTestCase):
    def setUp(self):
        self.host = helpers.FakeSAT()
        self.plugin = XEP_0334(self.host)

    def test_messageSendTrigger(self):
        template_xml = """
        <message
            from='romeo@montague.net/orchard'
            to='juliet@capulet.com'
            type='chat'>
          <body>text</body>
          %s
        </message>
        """
        original_xml = template_xml % ""

        d_list = []

        def cb(data, expected_xml):
            result_xml = data["xml"].toXml().encode("utf-8")
            self.assertEqualXML(result_xml, expected_xml, True)

        for key in HINTS + ("", "dummy_hint"):
            mess_data = {
                "xml": parseXml(original_xml.encode("utf-8")),
                "extra": {key: True},
            }
            treatments = defer.Deferred()
            self.plugin.messageSendTrigger(
                self.host.getClient(C.PROFILE[0]), mess_data, defer.Deferred(), treatments
            )
            if treatments.callbacks:  # the trigger added a callback
                expected_xml = template_xml % ('<%s xmlns="urn:xmpp:hints"/>' % key)
                treatments.addCallback(cb, expected_xml)
                treatments.callback(mess_data)
                d_list.append(treatments)

        return defer.DeferredList(d_list)

    def test_messageReceivedTrigger(self):
        template_xml = """
        <message
            from='romeo@montague.net/orchard'
            to='juliet@capulet.com'
            type='chat'>
          <body>text</body>
          %s
        </message>
        """

        def cb(__):
            raise Exception("Errback should not be ran instead of callback!")

        def eb(failure):
            failure.trap(exceptions.SkipHistory)

        d_list = []

        for key in HINTS + ("dummy_hint",):
            message = parseXml(template_xml % ('<%s xmlns="urn:xmpp:hints"/>' % key))
            post_treat = defer.Deferred()
            self.plugin.messageReceivedTrigger(
                self.host.getClient(C.PROFILE[0]), message, post_treat
            )
            if post_treat.callbacks:
                assert key in ("no-permanent-storage", "no-storage")
                post_treat.addCallbacks(cb, eb)
                post_treat.callback(None)
                d_list.append(post_treat)
            else:
                assert key not in ("no-permanent-storage", "no-storage")

        return defer.DeferredList(d_list)
