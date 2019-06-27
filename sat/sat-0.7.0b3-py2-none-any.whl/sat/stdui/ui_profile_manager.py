#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT standard user interface for managing contacts
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

from sat.core.i18n import D_
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core import exceptions
from sat.tools import xml_tools
from sat.memory.memory import ProfileSessions
from twisted.words.protocols.jabber import jid


class ProfileManager(object):
    """Manage profiles."""

    def __init__(self, host):
        self.host = host
        self.profile_ciphers = {}
        self._sessions = ProfileSessions()
        host.registerCallback(
            self._authenticateProfile, force_id=C.AUTHENTICATE_PROFILE_ID, with_data=True
        )
        host.registerCallback(
            self._changeXMPPPassword, force_id=C.CHANGE_XMPP_PASSWD_ID, with_data=True
        )
        self.__new_xmpp_passwd_id = host.registerCallback(
            self._changeXMPPPasswordCb, with_data=True
        )

    def _startSessionEb(self, fail, first, profile):
        """Errback method for startSession during profile authentication

        @param first(bool): if True, this is the first try and we have tryied empty password
            in this case we ask for a password to the user.
        @param profile(unicode, None): %(doc_profile)s
            must only be used if first is True
        """
        if first:
            # first call, we ask for the password
            form_ui = xml_tools.XMLUI(
                "form", title=D_("Profile password for {}").format(profile), submit_id=""
            )
            form_ui.addPassword("profile_password", value="")
            d = xml_tools.deferredUI(self.host, form_ui, chained=True)
            d.addCallback(self._authenticateProfile, profile)
            return {"xmlui": form_ui.toXml()}

        assert profile is None

        if fail.check(exceptions.PasswordError):
            dialog = xml_tools.XMLUI("popup", title=D_("Connection error"))
            dialog.addText(D_("The provided profile password doesn't match."))
        else:
            log.error(u"Unexpected exceptions: {}".format(fail))
            dialog = xml_tools.XMLUI("popup", title=D_("Internal error"))
            dialog.addText(D_(u"Internal error: {}".format(fail)))
        return {"xmlui": dialog.toXml(), "validated": C.BOOL_FALSE}

    def _authenticateProfile(self, data, profile):
        if C.bool(data.get("cancelled", "false")):
            return {}
        if self.host.memory.isSessionStarted(profile):
            return {"validated": C.BOOL_TRUE}
        try:
            password = data[xml_tools.formEscape("profile_password")]
        except KeyError:
            # first request, we try empty password
            password = ""
            first = True
            eb_profile = profile
        else:
            first = False
            eb_profile = None
        d = self.host.memory.startSession(password, profile)
        d.addCallback(lambda __: {"validated": C.BOOL_TRUE})
        d.addErrback(self._startSessionEb, first, eb_profile)
        return d

    def _changeXMPPPassword(self, data, profile):
        session_data = self._sessions.profileGetUnique(profile)
        if not session_data:
            server = self.host.memory.getParamA(
                C.FORCE_SERVER_PARAM, "Connection", profile_key=profile
            )
            if not server:
                server = jid.parse(
                    self.host.memory.getParamA(
                        "JabberID", "Connection", profile_key=profile
                    )
                )[1]
            session_id, session_data = self._sessions.newSession(
                {"count": 0, "server": server}, profile=profile
            )
        if (
            session_data["count"] > 2
        ):  # 3 attempts with a new password after the initial try
            self._sessions.profileDelUnique(profile)
            _dialog = xml_tools.XMLUI("popup", title=D_("Connection error"))
            _dialog.addText(
                D_("Can't connect to %s. Please check your connection details.")
                % session_data["server"]
            )
            return {"xmlui": _dialog.toXml()}
        session_data["count"] += 1
        counter = " (%d)" % session_data["count"] if session_data["count"] > 1 else ""
        title = D_("XMPP password for %(profile)s%(counter)s") % {
            "profile": profile,
            "counter": counter,
        }
        form_ui = xml_tools.XMLUI(
            "form", title=title, submit_id=self.__new_xmpp_passwd_id
        )
        form_ui.addText(
            D_(
                "Can't connect to %s. Please check your connection details or try with another password."
            )
            % session_data["server"]
        )
        form_ui.addPassword("xmpp_password", value="")
        return {"xmlui": form_ui.toXml()}

    def _changeXMPPPasswordCb(self, data, profile):
        xmpp_password = data[xml_tools.formEscape("xmpp_password")]
        d = self.host.memory.setParam(
            "Password", xmpp_password, "Connection", profile_key=profile
        )
        d.addCallback(lambda __: self.host.connect(profile))
        d.addCallback(lambda __: {})
        d.addErrback(lambda __: self._changeXMPPPassword({}, profile))
        return d
