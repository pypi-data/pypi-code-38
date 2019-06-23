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

""" Plugin XEP-0313 """

from constants import Const as C
from sat.test import helpers
from sat.plugins.plugin_xep_0313 import XEP_0313
from twisted.words.protocols.jabber.jid import JID
from twisted.words.xish import domish
from wokkel.data_form import Field
from dateutil.tz import tzutc
import datetime

# TODO: change this when RSM and MAM are in wokkel
from sat_tmp.wokkel.rsm import RSMRequest
from sat_tmp.wokkel.mam import buildForm, MAMRequest

NS_PUBSUB = "http://jabber.org/protocol/pubsub"
SERVICE = "sat-pubsub.tazar.int"
SERVICE_JID = JID(SERVICE)


class XEP_0313Test(helpers.SatTestCase):
    def setUp(self):
        self.host = helpers.FakeSAT()
        self.plugin = XEP_0313(self.host)
        self.client = self.host.getClient(C.PROFILE[0])
        mam_client = self.plugin.getHandler(C.PROFILE[0])
        mam_client.makeConnection(self.host.getClient(C.PROFILE[0]).xmlstream)

    def test_queryArchive(self):
        xml = """
        <iq type='set' id='%s' to='%s'>
          <query xmlns='urn:xmpp:mam:1'/>
        </iq>
        """ % (
            ("H_%d" % domish.Element._idCounter),
            SERVICE,
        )
        d = self.plugin.queryArchive(self.client, MAMRequest(), SERVICE_JID)
        d.addCallback(
            lambda __: self.assertEqualXML(self.host.getSentMessageXml(0), xml, True)
        )
        return d

    def test_queryArchivePubsub(self):
        xml = """
        <iq type='set' id='%s' to='%s'>
          <query xmlns='urn:xmpp:mam:1' node='fdp/submitted/capulet.lit/sonnets' />
        </iq>
        """ % (
            ("H_%d" % domish.Element._idCounter),
            SERVICE,
        )
        d = self.plugin.queryArchive(
            self.client, MAMRequest(node="fdp/submitted/capulet.lit/sonnets"), SERVICE_JID
        )
        d.addCallback(
            lambda __: self.assertEqualXML(self.host.getSentMessageXml(0), xml, True)
        )
        return d

    def test_queryArchiveWith(self):
        xml = """
        <iq type='set' id='%s' to='%s'>
          <query xmlns='urn:xmpp:mam:1'>
            <x xmlns='jabber:x:data' type='submit'>
              <field var='FORM_TYPE' type='hidden'>
                <value>urn:xmpp:mam:1</value>
              </field>
              <field var='with' type='jid-single'>
                <value>juliet@capulet.lit</value>
              </field>
            </x>
          </query>
        </iq>
        """ % (
            ("H_%d" % domish.Element._idCounter),
            SERVICE,
        )
        form = buildForm(with_jid=JID("juliet@capulet.lit"))
        d = self.plugin.queryArchive(self.client, MAMRequest(form), SERVICE_JID)
        d.addCallback(
            lambda __: self.assertEqualXML(self.host.getSentMessageXml(0), xml, True)
        )
        return d

    def test_queryArchiveStartEnd(self):
        xml = """
        <iq type='set' id='%s' to='%s'>
          <query xmlns='urn:xmpp:mam:1'>
            <x xmlns='jabber:x:data' type='submit'>
              <field var='FORM_TYPE' type='hidden'>
                <value>urn:xmpp:mam:1</value>
              </field>
              <field var='start' type='text-single'>
                <value>2010-06-07T00:00:00Z</value>
              </field>
              <field var='end' type='text-single'>
                <value>2010-07-07T13:23:54Z</value>
              </field>
            </x>
          </query>
        </iq>
        """ % (
            ("H_%d" % domish.Element._idCounter),
            SERVICE,
        )
        start = datetime.datetime(2010, 6, 7, 0, 0, 0, tzinfo=tzutc())
        end = datetime.datetime(2010, 7, 7, 13, 23, 54, tzinfo=tzutc())
        form = buildForm(start=start, end=end)
        d = self.plugin.queryArchive(self.client, MAMRequest(form), SERVICE_JID)
        d.addCallback(
            lambda __: self.assertEqualXML(self.host.getSentMessageXml(0), xml, True)
        )
        return d

    def test_queryArchiveStart(self):
        xml = """
        <iq type='set' id='%s' to='%s'>
          <query xmlns='urn:xmpp:mam:1'>
            <x xmlns='jabber:x:data' type='submit'>
              <field var='FORM_TYPE' type='hidden'>
                <value>urn:xmpp:mam:1</value>
              </field>
              <field var='start' type='text-single'>
                <value>2010-08-07T00:00:00Z</value>
              </field>
            </x>
          </query>
        </iq>
        """ % (
            ("H_%d" % domish.Element._idCounter),
            SERVICE,
        )
        start = datetime.datetime(2010, 8, 7, 0, 0, 0, tzinfo=tzutc())
        form = buildForm(start=start)
        d = self.plugin.queryArchive(self.client, MAMRequest(form), SERVICE_JID)
        d.addCallback(
            lambda __: self.assertEqualXML(self.host.getSentMessageXml(0), xml, True)
        )
        return d

    def test_queryArchiveRSM(self):
        xml = """
        <iq type='set' id='%s' to='%s'>
          <query xmlns='urn:xmpp:mam:1'>
            <x xmlns='jabber:x:data' type='submit'>
              <field var='FORM_TYPE' type='hidden'>
                <value>urn:xmpp:mam:1</value>
              </field>
              <field var='start' type='text-single'>
                <value>2010-08-07T00:00:00Z</value>
              </field>
            </x>
            <set xmlns='http://jabber.org/protocol/rsm'>
              <max>10</max>
            </set>
          </query>
        </iq>
        """ % (
            ("H_%d" % domish.Element._idCounter),
            SERVICE,
        )
        start = datetime.datetime(2010, 8, 7, 0, 0, 0, tzinfo=tzutc())
        form = buildForm(start=start)
        rsm = RSMRequest(max_=10)
        d = self.plugin.queryArchive(self.client, MAMRequest(form, rsm), SERVICE_JID)
        d.addCallback(
            lambda __: self.assertEqualXML(self.host.getSentMessageXml(0), xml, True)
        )
        return d

    def test_queryArchiveRSMPaging(self):
        xml = """
        <iq type='set' id='%s' to='%s'>
          <query xmlns='urn:xmpp:mam:1'>
              <x xmlns='jabber:x:data' type='submit'>
                <field var='FORM_TYPE' type='hidden'><value>urn:xmpp:mam:1</value></field>
                <field var='start' type='text-single'><value>2010-08-07T00:00:00Z</value></field>
              </x>
              <set xmlns='http://jabber.org/protocol/rsm'>
                 <max>10</max>
                 <after>09af3-cc343-b409f</after>
              </set>
          </query>
        </iq>
        """ % (
            ("H_%d" % domish.Element._idCounter),
            SERVICE,
        )
        start = datetime.datetime(2010, 8, 7, 0, 0, 0, tzinfo=tzutc())
        form = buildForm(start=start)
        rsm = RSMRequest(max_=10, after=u"09af3-cc343-b409f")
        d = self.plugin.queryArchive(self.client, MAMRequest(form, rsm), SERVICE_JID)
        d.addCallback(
            lambda __: self.assertEqualXML(self.host.getSentMessageXml(0), xml, True)
        )
        return d

    def test_queryFields(self):
        xml = """
        <iq type='get' id="%s" to='%s'>
          <query xmlns='urn:xmpp:mam:1'/>
        </iq>
        """ % (
            ("H_%d" % domish.Element._idCounter),
            SERVICE,
        )
        d = self.plugin.queryFields(self.client, SERVICE_JID)
        d.addCallback(
            lambda __: self.assertEqualXML(self.host.getSentMessageXml(0), xml, True)
        )
        return d

    def test_queryArchiveFields(self):
        xml = """
        <iq type='set' id='%s' to='%s'>
          <query xmlns='urn:xmpp:mam:1'>
            <x xmlns='jabber:x:data' type='submit'>
              <field type='hidden' var='FORM_TYPE'>
                <value>urn:xmpp:mam:1</value>
              </field>
              <field type='text-single' var='urn:example:xmpp:free-text-search'>
                <value>Where arth thou, my Juliet?</value>
              </field>
              <field type='text-single' var='urn:example:xmpp:stanza-content'>
                <value>{http://jabber.org/protocol/mood}mood/lonely</value>
              </field>
            </x>
          </query>
        </iq>
        """ % (
            ("H_%d" % domish.Element._idCounter),
            SERVICE,
        )
        extra_fields = [
            Field(
                "text-single",
                "urn:example:xmpp:free-text-search",
                "Where arth thou, my Juliet?",
            ),
            Field(
                "text-single",
                "urn:example:xmpp:stanza-content",
                "{http://jabber.org/protocol/mood}mood/lonely",
            ),
        ]
        form = buildForm(extra_fields=extra_fields)
        d = self.plugin.queryArchive(self.client, MAMRequest(form), SERVICE_JID)
        d.addCallback(
            lambda __: self.assertEqualXML(self.host.getSentMessageXml(0), xml, True)
        )
        return d

    def test_queryPrefs(self):
        xml = """
        <iq type='get' id='%s' to='%s'>
          <prefs xmlns='urn:xmpp:mam:1'>
            <always/>
            <never/>
          </prefs>
        </iq>
        """ % (
            ("H_%d" % domish.Element._idCounter),
            SERVICE,
        )
        d = self.plugin.getPrefs(self.client, SERVICE_JID)
        d.addCallback(
            lambda __: self.assertEqualXML(self.host.getSentMessageXml(0), xml, True)
        )
        return d

    def test_setPrefs(self):
        xml = """
        <iq type='set' id='%s' to='%s'>
          <prefs xmlns='urn:xmpp:mam:1' default='roster'>
            <always>
              <jid>romeo@montague.lit</jid>
            </always>
            <never>
              <jid>montague@montague.lit</jid>
            </never>
          </prefs>
        </iq>
        """ % (
            ("H_%d" % domish.Element._idCounter),
            SERVICE,
        )
        always = [JID("romeo@montague.lit")]
        never = [JID("montague@montague.lit")]
        d = self.plugin.setPrefs(self.client, SERVICE_JID, always=always, never=never)
        d.addCallback(
            lambda __: self.assertEqualXML(self.host.getSentMessageXml(0), xml, True)
        )
        return d
