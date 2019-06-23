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

""" Test the helper classes to see if they behave well"""

from sat.test import helpers
from sat.test import helpers_plugins


class FakeXEP_0045Test(helpers.SatTestCase):
    def setUp(self):
        self.host = helpers.FakeSAT()
        self.plugin = helpers_plugins.FakeXEP_0045(self.host)

    def test_joinRoom(self):
        self.plugin.joinRoom(0, 0)
        self.assertEqual("test", self.plugin.getNick(0, 0))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 0, 0))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 1, 0))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 2, 0))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 3, 0))
        self.assertEqual("", self.plugin.getNick(0, 1))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 0, 1))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 1, 1))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 2, 1))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 3, 1))
        self.assertEqual("", self.plugin.getNick(0, 2))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 0, 2))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 1, 2))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 2, 2))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 3, 2))
        self.assertEqual("", self.plugin.getNick(0, 3))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 0, 3))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 1, 3))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 2, 3))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 3, 3))
        self.plugin.joinRoom(0, 1)
        self.assertEqual("test", self.plugin.getNick(0, 0))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 0, 0))
        self.assertEqual("sender", self.plugin.getNickOfUser(0, 1, 0))
        self.assertEqual("sender", self.plugin.getNickOfUser(0, 2, 0))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 3, 0))
        self.assertEqual("sender", self.plugin.getNick(0, 1))
        self.assertEqual("test", self.plugin.getNickOfUser(0, 0, 1))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 1, 1))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 2, 1))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 3, 1))
        self.assertEqual("", self.plugin.getNick(0, 2))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 0, 2))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 1, 2))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 2, 2))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 3, 2))
        self.assertEqual("", self.plugin.getNick(0, 3))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 0, 3))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 1, 3))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 2, 3))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 3, 3))
        self.plugin.joinRoom(0, 2)
        self.assertEqual("test", self.plugin.getNick(0, 0))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 0, 0))
        self.assertEqual("sender", self.plugin.getNickOfUser(0, 1, 0))
        self.assertEqual("sender", self.plugin.getNickOfUser(0, 2, 0))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 3, 0))
        self.assertEqual("sender", self.plugin.getNick(0, 1))
        self.assertEqual("test", self.plugin.getNickOfUser(0, 0, 1))
        self.assertEqual(
            "sender", self.plugin.getNickOfUser(0, 1, 1)
        )  # Const.JID[2] is in the roster for Const.PROFILE[1]
        self.assertEqual("sender", self.plugin.getNickOfUser(0, 2, 1))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 3, 1))
        self.assertEqual("sender", self.plugin.getNick(0, 2))
        self.assertEqual("test", self.plugin.getNickOfUser(0, 0, 2))
        self.assertEqual("sender", self.plugin.getNickOfUser(0, 1, 2))
        self.assertEqual(
            "sender", self.plugin.getNickOfUser(0, 2, 2)
        )  # Const.JID[1] is in the roster for Const.PROFILE[2]
        self.assertEqual(None, self.plugin.getNickOfUser(0, 3, 2))
        self.assertEqual("", self.plugin.getNick(0, 3))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 0, 3))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 1, 3))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 2, 3))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 3, 3))
        self.plugin.joinRoom(0, 3)
        self.assertEqual("test", self.plugin.getNick(0, 0))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 0, 0))
        self.assertEqual("sender", self.plugin.getNickOfUser(0, 1, 0))
        self.assertEqual("sender", self.plugin.getNickOfUser(0, 2, 0))
        self.assertEqual("sender_", self.plugin.getNickOfUser(0, 3, 0))
        self.assertEqual("sender", self.plugin.getNick(0, 1))
        self.assertEqual("test", self.plugin.getNickOfUser(0, 0, 1))
        self.assertEqual(
            "sender", self.plugin.getNickOfUser(0, 1, 1)
        )  # Const.JID[2] is in the roster for Const.PROFILE[1]
        self.assertEqual("sender", self.plugin.getNickOfUser(0, 2, 1))
        self.assertEqual("sender_", self.plugin.getNickOfUser(0, 3, 1))
        self.assertEqual("sender", self.plugin.getNick(0, 2))
        self.assertEqual("test", self.plugin.getNickOfUser(0, 0, 2))
        self.assertEqual("sender", self.plugin.getNickOfUser(0, 1, 2))
        self.assertEqual(
            "sender", self.plugin.getNickOfUser(0, 2, 2)
        )  # Const.JID[1] is in the roster for Const.PROFILE[2]
        self.assertEqual("sender_", self.plugin.getNickOfUser(0, 3, 2))
        self.assertEqual("sender_", self.plugin.getNick(0, 3))
        self.assertEqual("test", self.plugin.getNickOfUser(0, 0, 3))
        self.assertEqual("sender", self.plugin.getNickOfUser(0, 1, 3))
        self.assertEqual("sender", self.plugin.getNickOfUser(0, 2, 3))
        self.assertEqual(None, self.plugin.getNickOfUser(0, 3, 3))
