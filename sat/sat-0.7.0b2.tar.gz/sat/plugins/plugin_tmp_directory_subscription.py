#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for directory subscription
# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2015, 2016 Adrien Cossa (souliane@mailoo.org)

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


PLUGIN_INFO = {
    C.PI_NAME: "Directory subscription plugin",
    C.PI_IMPORT_NAME: "DIRECTORY-SUBSCRIPTION",
    C.PI_TYPE: "TMP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0050", "XEP-0055"],
    C.PI_RECOMMENDATIONS: [],
    C.PI_MAIN: "DirectorySubscription",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Implementation of directory subscription"""),
}


NS_COMMANDS = "http://jabber.org/protocol/commands"
CMD_UPDATE_SUBSCRIBTION = "update"


class DirectorySubscription(object):
    def __init__(self, host):
        log.info(_("Directory subscription plugin initialization"))
        self.host = host
        host.importMenu(
            (D_("Service"), D_("Directory subscription")),
            self.subscribe,
            security_limit=1,
            help_string=D_("User directory subscription"),
        )

    def subscribe(self, raw_data, profile):
        """Request available commands on the jabber search service associated to profile's host.

        @param raw_data (dict): data received from the frontend
        @param profile (unicode): %(doc_profile)s
        @return: a deferred dict{unicode: unicode}
        """
        d = self.host.plugins["XEP-0055"]._getHostServices(profile)

        def got_services(services):
            service_jid = services[0]
            session_id, session_data = self.host.plugins[
                "XEP-0050"
            ].requesting.newSession(profile=profile)
            session_data["jid"] = service_jid
            session_data["node"] = CMD_UPDATE_SUBSCRIBTION
            data = {"session_id": session_id}
            return self.host.plugins["XEP-0050"]._requestingEntity(data, profile)

        return d.addCallback(got_services)
