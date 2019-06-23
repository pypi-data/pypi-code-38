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

"""This file manage the action <=> key map"""

from urwid_satext.keys import action_key_map


action_key_map.update(
    {
        # Edit bar
        ("edit", "MODE_INSERTION"): "i",
        ("edit", "MODE_COMMAND"): ":",
        ("edit", "HISTORY_PREV"): "up",
        ("edit", "HISTORY_NEXT"): "down",
        # global
        ("global", "MENU_HIDE"): "meta m",
        ("global", "NOTIFICATION_NEXT"): "ctrl n",
        ("global", "OVERLAY_HIDE"): "ctrl s",
        ("global", "DEBUG"): "ctrl d",
        ("global", "CONTACTS_HIDE"): "f2",
        (
            "global",
            "REFRESH_SCREEN",
        ): "ctrl l",  # ctrl l is used by Urwid to refresh screen
        # global menu
        ("menu_global", "APP_QUIT"): "ctrl x",
        ("menu_global", "ROOM_JOIN"): "meta j",
        # primitivus widgets
        ("primitivus_widget", "DECORATION_HIDE"): "meta l",
        # contact list
        ("contact_list", "STATUS_HIDE"): "meta s",
        ("contact_list", "DISCONNECTED_HIDE"): "meta d",
        ("contact_list", "RESOURCES_HIDE"): "meta r",
        # chat panel
        ("chat_panel", "OCCUPANTS_HIDE"): "meta p",
        ("chat_panel", "TIMESTAMP_HIDE"): "meta t",
        ("chat_panel", "SHORT_NICKNAME"): "meta n",
        ("chat_panel", "SUBJECT_SWITCH"): "meta s",
        ("chat_panel", "GOTO_BOTTOM"): "G",
        # card game
        ("card_game", "CARD_SELECT"): " ",
        # focus
        ("focus", "FOCUS_EXTRA"): "ctrl f",
    }
)


action_key_map.set_close_namespaces(tuple(), ("global", "focus", "menu_global"))
action_key_map.check_namespaces()
