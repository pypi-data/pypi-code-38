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

from sat.core import constants
from sat.core.i18n import _
from collections import OrderedDict  # only available from python 2.7


class Const(constants.Const):

    PRESENCE = OrderedDict(
        [
            ("", _("Online")),
            ("chat", _("Free for chat")),
            ("away", _("Away from keyboard")),
            ("dnd", _("Do not disturb")),
            ("xa", _("Extended away")),
        ]
    )

    # from plugin_misc_text_syntaxes
    SYNTAX_XHTML = "XHTML"
    SYNTAX_CURRENT = "@CURRENT@"
    SYNTAX_TEXT = "text"

    # XMLUI
    SAT_FORM_PREFIX = "SAT_FORM_"
    SAT_PARAM_SEPARATOR = "_XMLUI_PARAM_"  # used to have unique elements names
    XMLUI_STATUS_VALIDATED = "validated"
    XMLUI_STATUS_CANCELLED = constants.Const.XMLUI_DATA_CANCELLED

    # Roster
    CONTACT_GROUPS = "groups"
    CONTACT_RESOURCES = "resources"
    CONTACT_MAIN_RESOURCE = "main_resource"
    CONTACT_SPECIAL = "special"
    CONTACT_SPECIAL_GROUP = "group"  # group chat special entity
    CONTACT_SELECTED = "selected"
    # used in handler to track where the contact is coming from
    CONTACT_PROFILE = "profile"
    CONTACT_SPECIAL_ALLOWED = (CONTACT_SPECIAL_GROUP,)  # allowed values for special flag
    # set of forbidden names for contact data
    CONTACT_DATA_FORBIDDEN = {
        CONTACT_GROUPS,
        CONTACT_RESOURCES,
        CONTACT_MAIN_RESOURCE,
        CONTACT_SELECTED,
        CONTACT_PROFILE,
    }

    # Chats
    CHAT_STATE_ICON = {
        "": u" ",
        "active": u"✔",
        "inactive": u"☄",
        "gone": u"✈",
        "composing": u"✎",
        "paused": u"…",
    }

    # Blogs
    ENTRY_MODE_TEXT = "text"
    ENTRY_MODE_RICH = "rich"
    ENTRY_MODE_XHTML = "xhtml"

    # Widgets management
    # FIXME: should be in quick_frontend.constant, but Libervia doesn't inherit from it
    WIDGET_NEW = "NEW"
    WIDGET_KEEP = "KEEP"
    WIDGET_RAISE = "RAISE"
    WIDGET_RECREATE = "RECREATE"

    # Updates (generic)
    UPDATE_DELETE = "DELETE"
    UPDATE_MODIFY = "MODIFY"
    UPDATE_ADD = "ADD"
    UPDATE_SELECTION = "SELECTION"
    # high level update (i.e. not item level but organisation of items)
    UPDATE_STRUCTURE = "STRUCTURE"

    LISTENERS = {
        "avatar",
        "nick",
        "presence",
        "profilePlugged",
        "disconnect",
        "gotMenus",
        "menu",
        "notification",
        "notificationsClear",
        "progressFinished",
        "progressError",
    }

    # Notifications
    NOTIFY_MESSAGE = "MESSAGE"  # a message has been received
    NOTIFY_MENTION = "MENTION"  # user has been mentionned
    NOTIFY_PROGRESS_END = "PROGRESS_END"  # a progression has finised
    NOTIFY_GENERIC = "GENERIC"  # a notification which has not its own type
    NOTIFY_ALL = (NOTIFY_MESSAGE, NOTIFY_MENTION, NOTIFY_PROGRESS_END, NOTIFY_GENERIC)
