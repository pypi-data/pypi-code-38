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

from sat.core.i18n import _
from sat.core import log as logging

log = logging.getLogger(__name__)
from sat_frontends.quick_frontend.quick_profile_manager import QuickProfileManager
from sat_frontends.primitivus.constants import Const as C
from sat_frontends.primitivus.keys import action_key_map as a_key
from urwid_satext import sat_widgets
import urwid


class ProfileManager(QuickProfileManager, urwid.WidgetWrap):
    def __init__(self, host, autoconnect=None):
        QuickProfileManager.__init__(self, host, autoconnect)

        # login & password box must be created before list because of onProfileChange
        self.login_wid = sat_widgets.AdvancedEdit(_("Login:"), align="center")
        self.pass_wid = sat_widgets.Password(_("Password:"), align="center")

        style = ["no_first_select"]
        profiles = host.bridge.profilesListGet()
        profiles.sort()
        self.list_profile = sat_widgets.List(
            profiles, style=style, align="center", on_change=self.onProfileChange
        )

        # new & delete buttons
        buttons = [
            urwid.Button(_("New"), self.onNewProfile),
            urwid.Button(_("Delete"), self.onDeleteProfile),
        ]
        buttons_flow = urwid.GridFlow(
            buttons,
            max([len(button.get_label()) for button in buttons]) + 4,
            1,
            1,
            "center",
        )

        # second part: login information:
        divider = urwid.Divider("-")

        # connect button
        connect_button = sat_widgets.CustomButton(
            _("Connect"), self.onConnectProfiles, align="center"
        )

        # we now build the widget
        list_walker = urwid.SimpleFocusListWalker(
            [
                buttons_flow,
                self.list_profile,
                divider,
                self.login_wid,
                self.pass_wid,
                connect_button,
            ]
        )
        frame_body = urwid.ListBox(list_walker)
        frame = urwid.Frame(
            frame_body,
            urwid.AttrMap(urwid.Text(_("Profile Manager"), align="center"), "title"),
        )
        self.main_widget = urwid.LineBox(frame)
        urwid.WidgetWrap.__init__(self, self.main_widget)

        self.go(autoconnect)

    def keypress(self, size, key):
        if key == a_key["APP_QUIT"]:
            self.host.onExit()
            raise urwid.ExitMainLoop()
        elif key in (a_key["FOCUS_UP"], a_key["FOCUS_DOWN"]):
            focus_diff = 1 if key == a_key["FOCUS_DOWN"] else -1
            list_box = self.main_widget.base_widget.body
            current_focus = list_box.body.get_focus()[1]
            if current_focus is None:
                return
            while True:
                current_focus += focus_diff
                if current_focus < 0 or current_focus >= len(list_box.body):
                    break
                if list_box.body[current_focus].selectable():
                    list_box.set_focus(
                        current_focus, "above" if focus_diff == 1 else "below"
                    )
                    list_box._invalidate()
                    return
        return super(ProfileManager, self).keypress(size, key)

    def cancelDialog(self, button):
        self.host.removePopUp()

    def newProfile(self, button, edit):
        """Create the profile"""
        name = edit.get_edit_text()
        self.host.bridge.profileCreate(
            name,
            callback=lambda: self.newProfileCreated(name),
            errback=self.profileCreationFailure,
        )

    def newProfileCreated(self, profile):
        # new profile will be selected, and a selected profile assume the session is started
        self.host.bridge.profileStartSession(
            "",
            profile,
            callback=lambda __: self.newProfileSessionStarted(profile),
            errback=self.profileCreationFailure,
        )

    def newProfileSessionStarted(self, profile):
        self.host.removePopUp()
        self.refillProfiles()
        self.list_profile.selectValue(profile)
        self.current.profile = profile
        self.getConnectionParams(profile)
        self.host.redraw()

    def profileCreationFailure(self, reason):
        self.host.removePopUp()
        message = self._getErrorMessage(reason)
        self.host.alert(_("Can't create profile"), message)

    def deleteProfile(self, button):
        self._deleteProfile()
        self.host.removePopUp()

    def onNewProfile(self, e):
        pop_up_widget = sat_widgets.InputDialog(
            _("New profile"),
            _("Please enter a new profile name"),
            cancel_cb=self.cancelDialog,
            ok_cb=self.newProfile,
        )
        self.host.showPopUp(pop_up_widget)

    def onDeleteProfile(self, e):
        if self.current.profile:
            pop_up_widget = sat_widgets.ConfirmDialog(
                _("Are you sure you want to delete the profile {} ?").format(
                    self.current.profile
                ),
                no_cb=self.cancelDialog,
                yes_cb=self.deleteProfile,
            )
            self.host.showPopUp(pop_up_widget)

    def onConnectProfiles(self, button):
        """Connect the profiles and start the main widget

        @param button: the connect button
        """
        self._onConnectProfiles()

    def resetFields(self):
        """Set profile to None, and reset fields"""
        super(ProfileManager, self).resetFields()
        self.list_profile.unselectAll(invisible=True)

    def setProfiles(self, profiles):
        """Update the list of profiles"""
        self.list_profile.changeValues(profiles)
        self.host.redraw()

    def getProfiles(self):
        return self.list_profile.getSelectedValues()

    def getJID(self):
        return self.login_wid.get_edit_text()

    def getPassword(self):
        return self.pass_wid.get_edit_text()

    def setJID(self, jid_):
        self.login_wid.set_edit_text(jid_)
        self.current.login = jid_
        self.host.redraw()  # FIXME: redraw should be avoided

    def setPassword(self, password):
        self.pass_wid.set_edit_text(password)
        self.current.password = password
        self.host.redraw()

    def onProfileChange(self, list_wid, widget=None, selected=None):
        """This is called when a profile is selected in the profile list.

        @param list_wid: the List widget who sent the event
        """
        self.updateConnectionParams()
        focused = list_wid.focus
        selected = focused.getState() if focused is not None else False
        if not selected:  # profile was just unselected
            return
        focused.setState(
            False, invisible=True
        )  # we don't want the widget to be selected until we are sure we can access it

        def authenticate_cb(data, cb_id, profile):
            if C.bool(data.pop("validated", C.BOOL_FALSE)):
                self.current.profile = profile
                focused.setState(True, invisible=True)
                self.getConnectionParams(profile)
                self.host.redraw()
            self.host.actionManager(data, callback=authenticate_cb, profile=profile)

        self.host.launchAction(
            C.AUTHENTICATE_PROFILE_ID, callback=authenticate_cb, profile=focused.text
        )
