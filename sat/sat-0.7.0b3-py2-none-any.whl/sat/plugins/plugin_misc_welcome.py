#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for file tansfer
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
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.tools import xml_tools


PLUGIN_INFO = {
    C.PI_NAME: "Welcome",
    C.PI_IMPORT_NAME: "WELCOME",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_MAIN: "Welcome",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(
        """Plugin which manage welcome message and things to to on first connection."""
    ),
}


WELCOME_PARAM_CATEGORY = "General"
WELCOME_PARAM_NAME = "welcome"
WELCOME_PARAM_LABEL = D_(u"Display welcome message")
WELCOME_MSG_TITLE = D_(u"Welcome to Libervia/Salut à Toi")
# XXX: this message is mainly targetting libervia new users for now
#      (i.e.: it may look weird on other frontends)
WELCOME_MSG = D_(
    u"""Welcome to a free (as in freedom) network!

If you have any trouble, or you want to help us for the bug hunting, you can contact us in real time chat by using the “Help / Official chat room”  menu.

To use Libervia, you'll need to add contacts, either people you know, or people you discover by using the “Contacts / Search directory” menu.

We hope that you'll enjoy using this project.

The Libervia/Salut à Toi Team
"""
)


PARAMS = """
    <params>
    <individual>
    <category name="{category}">
        <param name="{name}" label="{label}" type="bool" />
    </category>
    </individual>
    </params>
    """.format(
    category=WELCOME_PARAM_CATEGORY, name=WELCOME_PARAM_NAME, label=WELCOME_PARAM_LABEL
)


class Welcome(object):
    def __init__(self, host):
        log.info(_("plugin Welcome initialization"))
        self.host = host
        host.memory.updateParams(PARAMS)

    def profileConnected(self, client):
        # XXX: if you wan to try first_start again, you'll have to remove manually
        #      the welcome value from your profile params in sat.db
        welcome = self.host.memory.params.getParamA(
            WELCOME_PARAM_NAME,
            WELCOME_PARAM_CATEGORY,
            use_default=False,
            profile_key=client.profile,
        )
        if welcome is None:
            first_start = True
            welcome = True
        else:
            first_start = False

        if welcome:
            xmlui = xml_tools.note(WELCOME_MSG, WELCOME_MSG_TITLE)
            self.host.actionNew({"xmlui": xmlui.toXml()}, profile=client.profile)
            self.host.memory.setParam(
                WELCOME_PARAM_NAME,
                C.BOOL_FALSE,
                WELCOME_PARAM_CATEGORY,
                profile_key=client.profile,
            )

        self.host.trigger.point("WELCOME", first_start, welcome, client.profile)
