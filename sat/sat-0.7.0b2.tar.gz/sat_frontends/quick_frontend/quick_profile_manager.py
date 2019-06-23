#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# helper class for making a SAT frontend
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

from sat.core.i18n import _
from sat.core import log as logging

log = logging.getLogger(__name__)
from sat_frontends.primitivus.constants import Const as C


class ProfileRecord(object):
    """Class which manage data for one profile"""

    def __init__(self, profile=None, login=None, password=None):
        self._profile = profile
        self._login = login
        self._password = password

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, value):
        self._profile = value
        # if we change the profile,
        # we must have no login/password until backend give them
        self._login = self._password = None

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value):
        self._login = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value


class QuickProfileManager(object):
    """Class with manage profiles creation/deletion/connection"""

    def __init__(self, host, autoconnect=None):
        """Create the manager

        @param host: %(doc_host)s
        @param autoconnect(iterable): list of profiles to connect automatically
        """
        self.host = host
        self._autoconnect = bool(autoconnect)
        self.current = ProfileRecord()

    def go(self, autoconnect):
        if self._autoconnect:
            self.autoconnect(autoconnect)

    def autoconnect(self, profile_keys):
        """Automatically connect profiles

        @param profile_keys(iterable): list of profile keys to connect
        """
        if not profile_keys:
            log.warning("No profile given to autoconnect")
            return
        self._autoconnect = True
        self._autoconnect_profiles = []
        self._do_autoconnect(profile_keys)

    def _do_autoconnect(self, profile_keys):
        """Connect automatically given profiles

        @param profile_kes(iterable): profiles to connect
        """
        assert self._autoconnect

        def authenticate_cb(data, cb_id, profile):

            if C.bool(data.pop("validated", C.BOOL_FALSE)):
                self._autoconnect_profiles.append(profile)
                if len(self._autoconnect_profiles) == len(profile_keys):
                    # all the profiles have been validated
                    self.host.plug_profiles(self._autoconnect_profiles)
            else:
                # a profile is not validated, we go to manual mode
                self._autoconnect = False
            self.host.actionManager(data, callback=authenticate_cb, profile=profile)

        def getProfileNameCb(profile):
            if not profile:
                # FIXME: this method is not handling manual mode correclty anymore
                #        must be thought to be handled asynchronously
                self._autoconnect = False  # manual mode
                msg = _("Trying to plug an unknown profile key ({})".format(profile_key))
                log.warning(msg)
                self.host.showDialog(_("Profile plugging in error"), msg, "error")
            else:
                self.host.launchAction(
                    C.AUTHENTICATE_PROFILE_ID, callback=authenticate_cb, profile=profile
                )

        def getProfileNameEb(failure):
            log.error(u"Can't retrieve profile name: {}".format(failure))

        for profile_key in profile_keys:
            self.host.bridge.profileNameGet(
                profile_key, callback=getProfileNameCb, errback=getProfileNameEb
            )

    def getParamError(self, __):
        self.host.showDialog(_(u"Error"), _("Can't get profile parameter"), "error")

    ## Helping methods ##

    def _getErrorMessage(self, reason):
        """Return an error message corresponding to profile creation error

        @param reason (str): reason as returned by profileCreate
        @return (unicode): human readable error message
        """
        if reason == "ConflictError":
            message = _("A profile with this name already exists")
        elif reason == "CancelError":
            message = _("Profile creation cancelled by backend")
        elif reason == "ValueError":
            message = _(
                "You profile name is not valid"
            )  # TODO: print a more informative message (empty name, name starting with '@')
        else:
            message = _("Can't create profile ({})").format(reason)
        return message

    def _deleteProfile(self):
        """Delete the currently selected profile"""
        if self.current.profile:
            self.host.bridge.asyncDeleteProfile(
                self.current.profile, callback=self.refillProfiles
            )
            self.resetFields()

    ## workflow methods (events occuring during the profiles selection) ##

    # These methods must be called by the frontend at some point

    def _onConnectProfiles(self):
        """Connect the profiles and start the main widget"""
        if self._autoconnect:
            self.host.showDialog(
                _("Internal error"),
                _("You can't connect manually and automatically at the same time"),
                "error",
            )
            return
        self.updateConnectionParams()
        profiles = self.getProfiles()
        if not profiles:
            self.host.showDialog(
                _("No profile selected"),
                _("You need to create and select at least one profile before connecting"),
                "error",
            )
        else:
            # All profiles in the list are already validated, so we can plug them directly
            self.host.plug_profiles(profiles)

    def getConnectionParams(self, profile):
        """Get login and password and display them

        @param profile: %(doc_profile)s
        """
        self.host.bridge.asyncGetParamA(
            "JabberID",
            "Connection",
            profile_key=profile,
            callback=self.setJID,
            errback=self.getParamError,
        )
        self.host.bridge.asyncGetParamA(
            "Password",
            "Connection",
            profile_key=profile,
            callback=self.setPassword,
            errback=self.getParamError,
        )

    def updateConnectionParams(self):
        """Check if connection parameters have changed, and update them if so"""
        if self.current.profile:
            login = self.getJID()
            password = self.getPassword()
            if login != self.current.login and self.current.login is not None:
                self.current.login = login
                self.host.bridge.setParam(
                    "JabberID", login, "Connection", profile_key=self.current.profile
                )
                log.info(u"login updated for profile [{}]".format(self.current.profile))
            if password != self.current.password and self.current.password is not None:
                self.current.password = password
                self.host.bridge.setParam(
                    "Password", password, "Connection", profile_key=self.current.profile
                )
                log.info(
                    u"password updated for profile [{}]".format(self.current.profile)
                )

    ## graphic updates (should probably be overriden in frontends) ##

    def resetFields(self):
        """Set profile to None, and reset fields"""
        self.current.profile = None
        self.setJID("")
        self.setPassword("")

    def refillProfiles(self):
        """Rebuild the list of profiles"""
        profiles = self.host.bridge.profilesListGet()
        profiles.sort()
        self.setProfiles(profiles)

    ## Method which must be implemented by frontends ##

    # get/set data

    def getProfiles(self):
        """Return list of selected profiles

        Must be implemented by frontends
        @return (list): list of profiles
        """
        raise NotImplementedError

    def setProfiles(self, profiles):
        """Update the list of profiles"""
        raise NotImplementedError

    def getJID(self):
        """Get current jid

        Must be implemented by frontends
        @return (unicode): current jabber id
        """
        raise NotImplementedError

    def getPassword(self):
        """Get current password

        Must be implemented by frontends
        @return (unicode): current password
        """
        raise NotImplementedError

    def setJID(self, jid_):
        """Set current jid

        Must be implemented by frontends
        @param jid_(unicode): jabber id to set
        """
        raise NotImplementedError

    def setPassword(self, password):
        """Set current password

        Must be implemented by frontends
        """
        raise NotImplementedError

    # dialogs

    # Note: a method which check profiles change must be implemented too
