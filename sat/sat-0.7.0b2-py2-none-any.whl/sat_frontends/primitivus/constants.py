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

from sat_frontends.quick_frontend import constants


class Const(constants.Const):

    APP_NAME = "Primitivus"
    SECTION_NAME = APP_NAME.lower()
    PALETTE = [
        ("title", "black", "light gray", "standout,underline"),
        ("title_focus", "white,bold", "light gray", "standout,underline"),
        ("selected", "default", "dark red"),
        ("selected_focus", "default,bold", "dark red"),
        ("default", "default", "default"),
        ("default_focus", "default,bold", "default"),
        ("cl_notifs", "yellow", "default"),
        ("cl_notifs_focus", "yellow,bold", "default"),
        ("cl_mention", "dark red", "default"),
        ("cl_mention_focus", "dark red,bold", "default"),
        # Messages
        ("date", "light gray", "default"),
        ("my_nick", "dark red,bold", "default"),
        ("other_nick", "dark cyan,bold", "default"),
        ("info_msg", "yellow", "default", "bold"),
        ("msg_lang", "dark cyan", "default"),
        ("msg_mention", "dark red, bold", "default"),
        ("msg_status_received", "light green, bold", "default"),
        ("menubar", "light gray,bold", "dark red"),
        ("menubar_focus", "light gray,bold", "dark green"),
        ("selected_menu", "light gray,bold", "dark green"),
        ("menuitem", "light gray,bold", "dark red"),
        ("menuitem_focus", "light gray,bold", "dark green"),
        ("notifs", "black,bold", "yellow"),
        ("notifs_focus", "dark red", "yellow"),
        ("card_neutral", "dark gray", "white", "standout,underline"),
        ("card_neutral_selected", "dark gray", "dark green", "standout,underline"),
        ("card_special", "brown", "white", "standout,underline"),
        ("card_special_selected", "brown", "dark green", "standout,underline"),
        ("card_red", "dark red", "white", "standout,underline"),
        ("card_red_selected", "dark red", "dark green", "standout,underline"),
        ("card_black", "black", "white", "standout,underline"),
        ("card_black_selected", "black", "dark green", "standout,underline"),
        ("directory", "dark cyan, bold", "default"),
        ("directory_focus", "dark cyan, bold", "dark green"),
        ("separator", "brown", "default"),
        ("warning", "light red", "default"),
        ("progress_normal", "default", "brown"),
        ("progress_complete", "default", "dark green"),
        ("show_disconnected", "dark gray", "default"),
        ("show_normal", "default", "default"),
        ("show_normal_focus", "default, bold", "default"),
        ("show_chat", "dark green", "default"),
        ("show_chat_focus", "dark green, bold", "default"),
        ("show_away", "brown", "default"),
        ("show_away_focus", "brown, bold", "default"),
        ("show_dnd", "dark red", "default"),
        ("show_dnd_focus", "dark red, bold", "default"),
        ("show_xa", "dark red", "default"),
        ("show_xa_focus", "dark red, bold", "default"),
        ("resource", "light blue", "default"),
        ("resource_main", "dark blue", "default"),
        ("status", "yellow", "default"),
        ("status_focus", "yellow, bold", "default"),
        ("param_selected", "default, bold", "dark red"),
        ("table_selected", "default, bold", "default"),
    ]
    PRESENCE = {
        "unavailable": (u"⨯", "show_disconnected"),
        "": (u"✔", "show_normal"),
        "chat": (u"✆", "show_chat"),
        "away": (u"✈", "show_away"),
        "dnd": (u"✖", "show_dnd"),
        "xa": (u"☄", "show_xa"),
    }
    LOG_OPT_SECTION = APP_NAME.lower()
    LOG_OPT_OUTPUT = (
        "output",
        constants.Const.LOG_OPT_OUTPUT_SEP + constants.Const.LOG_OPT_OUTPUT_MEMORY,
    )

    CONFIG_SECTION = APP_NAME.lower()
    CONFIG_OPT_KEY_PREFIX = "KEY_"

    MENU_ID_MAIN = "MAIN_MENU"
    MENU_ID_WIDGET = "WIDGET_MENU"

    MODE_NORMAL = "NORMAL"
    MODE_INSERTION = "INSERTION"
    MODE_COMMAND = "COMMAND"

    GROUP_DATA_FOLDED = "folded"
