#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin to be notified on some entities presence
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
from sat.core import exceptions
from sat.tools import xml_tools


PLUGIN_INFO = {
    C.PI_NAME: "Watched",
    C.PI_IMPORT_NAME: "WATCHED",
    C.PI_TYPE: "Misc",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "Watched",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(
        """Watch for entities presence, and send notification accordingly"""
    ),
}


CATEGORY = D_("Misc")
NAME = "Watched"
NOTIF = D_("Watched entity {entity} is connected")


class Watched(object):
    params = """
    <params>
    <individual>
    <category name="{category_name}" label="{category_label}">
        <param name="{name}" label="{label}" type="jids_list" security="0" />
    </category>
    </individual>
    </params>
    """.format(
        category_name=CATEGORY, category_label=_(CATEGORY), name=NAME, label=_(NAME)
    )

    def __init__(self, host):
        log.info(_("Watched initialisation"))
        self.host = host
        host.memory.updateParams(self.params)
        host.trigger.add("presence_received", self._presenceReceivedTrigger)

    def _presenceReceivedTrigger(self, client, entity, show, priority, statuses):
        if show == C.PRESENCE_UNAVAILABLE:
            return True

        # we check that the previous presence was unavailable (no notification else)
        try:
            old_show = self.host.memory.getEntityDatum(
                entity, "presence", client.profile).show
        except (KeyError, exceptions.UnknownEntityError):
            old_show = C.PRESENCE_UNAVAILABLE

        if old_show == C.PRESENCE_UNAVAILABLE:
            watched = self.host.memory.getParamA(
                NAME, CATEGORY, profile_key=client.profile)
            if entity in watched or entity.userhostJID() in watched:
                self.host.actionNew(
                    {
                        "xmlui": xml_tools.note(
                            _(NOTIF).format(entity=entity.full())
                        ).toXml()
                    },
                    profile=client.profile,
                )

        return True
