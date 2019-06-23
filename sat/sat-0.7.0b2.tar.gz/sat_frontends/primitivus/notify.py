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

import dbus


class Notify(object):
    """Used to send notification and detect if we have focus"""

    def __init__(self):

        # X11 stuff
        self.display = None
        self.X11_id = -1

        try:
            from Xlib import display as X_display

            self.display = X_display.Display()
            self.X11_id = self.getFocus()
        except:
            pass

        # Now we try to connect to Freedesktop D-Bus API
        try:
            bus = dbus.SessionBus()
            db_object = bus.get_object(
                "org.freedesktop.Notifications",
                "/org/freedesktop/Notifications",
                follow_name_owner_changes=True,
            )
            self.freedesktop_int = dbus.Interface(
                db_object, dbus_interface="org.freedesktop.Notifications"
            )
        except:
            self.freedesktop_int = None

    def getFocus(self):
        if not self.display:
            return 0
        return self.display.get_input_focus().focus.id

    def hasFocus(self):
        return (self.getFocus() == self.X11_id) if self.display else True

    def useX11(self):
        return bool(self.display)

    def sendNotification(self, summ_mess, body_mess=""):
        """Send notification to the user if possible"""
        # TODO: check options before sending notifications
        if self.freedesktop_int:
            self.sendFDNotification(summ_mess, body_mess)

    def sendFDNotification(self, summ_mess, body_mess=""):
        """Send notification with the FreeDesktop D-Bus API"""
        if self.freedesktop_int:
            app_name = "Primitivus"
            replaces_id = 0
            app_icon = ""
            summary = summ_mess
            body = body_mess
            actions = dbus.Array(signature="s")
            hints = dbus.Dictionary(signature="sv")
            expire_timeout = -1

            self.freedesktop_int.Notify(
                app_name,
                replaces_id,
                app_icon,
                summary,
                body,
                actions,
                hints,
                expire_timeout,
            )
