#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin for registering a new XMPP account
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

from sat.core.i18n import _, D_
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core.constants import Const as C
from twisted.words.protocols.jabber import jid
from sat.memory.memory import Sessions
from sat.tools import xml_tools
from sat.tools.xml_tools import SAT_FORM_PREFIX, SAT_PARAM_SEPARATOR


PLUGIN_INFO = {
    C.PI_NAME: "Register Account Plugin",
    C.PI_IMPORT_NAME: "REGISTER-ACCOUNT",
    C.PI_TYPE: "MISC",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0077"],
    C.PI_RECOMMENDATIONS: [],
    C.PI_MAIN: "RegisterAccount",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(u"""Register XMPP account"""),
}


class RegisterAccount(object):
    # FIXME: this plugin is messy and difficult to read, it needs to be cleaned up and documented

    def __init__(self, host):
        log.info(_(u"Plugin Register Account initialization"))
        self.host = host
        self._sessions = Sessions()
        host.registerCallback(
            self.registerNewAccountCB, with_data=True, force_id="registerNewAccount"
        )
        self.__register_account_id = host.registerCallback(
            self._registerConfirmation, with_data=True
        )

    def registerNewAccountCB(self, data, profile):
        """Called when the user click on the "New account" button."""
        session_data = {}

        # FIXME: following loop is overcomplicated, hard to read
        # FIXME: while used with parameters, hashed password is used and overwrite clear one
        for param in (u"JabberID", u"Password", C.FORCE_PORT_PARAM, C.FORCE_SERVER_PARAM):
            try:
                session_data[param] = data[
                    SAT_FORM_PREFIX + u"Connection" + SAT_PARAM_SEPARATOR + param
                ]
            except KeyError:
                if param in (C.FORCE_PORT_PARAM, C.FORCE_SERVER_PARAM):
                    session_data[param] = ""

        for param in (u"JabberID", u"Password"):
            if not session_data[param]:
                form_ui = xml_tools.XMLUI(u"popup", title=D_(u"Missing values"))
                form_ui.addText(
                    D_(u"No user JID or password given: can't register new account.")
                )
                return {u"xmlui": form_ui.toXml()}

        session_data["user"], host, resource = jid.parse(session_data["JabberID"])
        session_data["server"] = session_data[C.FORCE_SERVER_PARAM] or host
        session_id, __ = self._sessions.newSession(session_data, profile=profile)
        form_ui = xml_tools.XMLUI(
            "form",
            title=D_("Register new account"),
            submit_id=self.__register_account_id,
            session_id=session_id,
        )
        form_ui.addText(
            D_(u"Do you want to register a new XMPP account {jid}?").format(
                jid=session_data["JabberID"]
            )
        )
        return {"xmlui": form_ui.toXml()}

    def _registerConfirmation(self, data, profile):
        """Save the related parameters and proceed the registration."""
        session_data = self._sessions.profileGet(data["session_id"], profile)

        self.host.memory.setParam(
            "JabberID", session_data["JabberID"], "Connection", profile_key=profile
        )
        self.host.memory.setParam(
            "Password", session_data["Password"], "Connection", profile_key=profile
        )
        self.host.memory.setParam(
            C.FORCE_SERVER_PARAM,
            session_data[C.FORCE_SERVER_PARAM],
            "Connection",
            profile_key=profile,
        )
        self.host.memory.setParam(
            C.FORCE_PORT_PARAM,
            session_data[C.FORCE_PORT_PARAM],
            "Connection",
            profile_key=profile,
        )

        d = self._registerNewAccount(
            jid.JID(session_data["JabberID"]),
            session_data["Password"],
            None,
            session_data["server"],
        )
        del self._sessions[data["session_id"]]
        return d

    def _registerNewAccount(self, client, jid_, password, email, server):
        #  FIXME: port is not set here
        def registeredCb(__):
            xmlui = xml_tools.XMLUI(u"popup", title=D_(u"Confirmation"))
            xmlui.addText(D_("Registration successful."))
            return {"xmlui": xmlui.toXml()}

        def registeredEb(failure):
            xmlui = xml_tools.XMLUI("popup", title=D_("Failure"))
            xmlui.addText(D_("Registration failed: %s") % failure.getErrorMessage())
            try:
                if failure.value.condition == "conflict":
                    xmlui.addText(
                        D_("Username already exists, please choose an other one.")
                    )
            except AttributeError:
                pass
            return {"xmlui": xmlui.toXml()}

        registered_d = self.host.plugins["XEP-0077"].registerNewAccount(
            client, jid_, password, email=email, host=server, port=C.XMPP_C2S_PORT
        )
        registered_d.addCallbacks(registeredCb, registeredEb)
        return registered_d
