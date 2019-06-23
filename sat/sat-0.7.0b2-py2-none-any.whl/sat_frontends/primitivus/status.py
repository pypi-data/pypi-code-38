#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Primitivus: a SAT frontend
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

from sat.core.i18n import _
import urwid
from urwid_satext import sat_widgets
from sat_frontends.quick_frontend.constants import Const as commonConst
from sat_frontends.primitivus.constants import Const as C


class StatusBar(urwid.Columns):
    def __init__(self, host):
        self.host = host
        self.presence = sat_widgets.ClickableText("")
        status_prefix = urwid.Text("[")
        status_suffix = urwid.Text("]")
        self.status = sat_widgets.ClickableText("")
        self.setPresenceStatus(C.PRESENCE_UNAVAILABLE, "")
        urwid.Columns.__init__(
            self,
            [
                ("weight", 1, self.presence),
                ("weight", 1, status_prefix),
                ("weight", 9, self.status),
                ("weight", 1, status_suffix),
            ],
        )
        urwid.connect_signal(self.presence, "click", self.onPresenceClick)
        urwid.connect_signal(self.status, "click", self.onStatusClick)

    def onPresenceClick(self, sender=None):
        if not self.host.bridge.isConnected(
            self.host.current_profile
        ):  # FIXME: manage multi-profiles
            return
        options = [commonConst.PRESENCE[presence] for presence in commonConst.PRESENCE]
        list_widget = sat_widgets.GenericList(
            options=options, option_type=sat_widgets.ClickableText, on_click=self.onChange
        )
        decorated = sat_widgets.LabelLine(
            list_widget, sat_widgets.SurroundedText(_("Set your presence"))
        )
        self.host.showPopUp(decorated)

    def onStatusClick(self, sender=None):
        if not self.host.bridge.isConnected(
            self.host.current_profile
        ):  # FIXME: manage multi-profiles
            return
        pop_up_widget = sat_widgets.InputDialog(
            _("Set your status"),
            _("New status"),
            default_txt=self.status.get_text(),
            cancel_cb=self.host.removePopUp,
            ok_cb=self.onChange,
        )
        self.host.showPopUp(pop_up_widget)

    def onChange(self, sender=None, user_data=None):
        new_value = user_data.get_text()
        previous = (
            [key for key in C.PRESENCE if C.PRESENCE[key][0] == self.presence.get_text()][
                0
            ],
            self.status.get_text(),
        )
        if isinstance(user_data, sat_widgets.ClickableText):
            new = (
                [
                    key
                    for key in commonConst.PRESENCE
                    if commonConst.PRESENCE[key] == new_value
                ][0],
                previous[1],
            )
        elif isinstance(user_data, sat_widgets.AdvancedEdit):
            new = (previous[0], new_value[0])
        if new != previous:
            statuses = {
                C.PRESENCE_STATUSES_DEFAULT: new[1]
            }  # FIXME: manage multilingual statuses
            for (
                profile
            ) in (
                self.host.profiles
            ):  # FIXME: for now all the profiles share the same status
                self.host.bridge.setPresence(
                    show=new[0], statuses=statuses, profile_key=profile
                )
            self.setPresenceStatus(new[0], new[1])
        self.host.removePopUp()

    def setPresenceStatus(self, show, status):
        show_icon, show_attr = C.PRESENCE.get(show)
        self.presence.set_text(("show_normal", show_icon))
        if status is not None:
            self.status.set_text((show_attr, status))
        self.host.redraw()
