#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Primitivus: a SAT frontend
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

from sat.core.i18n import _, D_
from twisted.words.protocols.jabber import jid


class Const(object):

    PROF_KEY_NONE = "@NONE@"

    PROFILE = [
        "test_profile",
        "test_profile2",
        "test_profile3",
        "test_profile4",
        "test_profile5",
    ]
    JID_STR = [
        u"test@example.org/SàT",
        u"sender@example.net/house",
        u"sender@example.net/work",
        u"sender@server.net/res",
        u"xxx@server.net/res",
    ]
    JID = [jid.JID(jid_s) for jid_s in JID_STR]

    PROFILE_DICT = {}
    for i in xrange(0, len(PROFILE)):
        PROFILE_DICT[PROFILE[i]] = JID[i]

    MUC_STR = [u"room@chat.server.domain", u"sat_game@chat.server.domain"]
    MUC = [jid.JID(jid_s) for jid_s in MUC_STR]

    NO_SECURITY_LIMIT = -1
    SECURITY_LIMIT = 0

    # To test frontend parameters
    APP_NAME = "dummy_frontend"
    COMPOSITION_KEY = D_("Composition")
    ENABLE_UNIBOX_PARAM = D_("Enable unibox")
    PARAM_IN_QUOTES = D_("'Wysiwyg' edition")
