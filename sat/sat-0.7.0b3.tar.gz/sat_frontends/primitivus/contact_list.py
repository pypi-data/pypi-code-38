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
import urwid
from urwid_satext import sat_widgets
from sat_frontends.quick_frontend.quick_contact_list import QuickContactList
from sat_frontends.primitivus.status import StatusBar
from sat_frontends.primitivus.constants import Const as C
from sat_frontends.primitivus.keys import action_key_map as a_key
from sat_frontends.primitivus.widget import PrimitivusWidget
from sat_frontends.tools import jid
from sat.core import log as logging

log = logging.getLogger(__name__)
from sat_frontends.quick_frontend import quick_widgets


class ContactList(PrimitivusWidget, QuickContactList):
    PROFILES_MULTIPLE = False
    PROFILES_ALLOW_NONE = False
    signals = ["click", "change"]
    # FIXME: Only single profile is managed so far

    def __init__(
        self, host, target, on_click=None, on_change=None, user_data=None, profiles=None
    ):
        QuickContactList.__init__(self, host, profiles)
        self.contact_list = self.host.contact_lists[self.profile]

        # we now build the widget
        self.status_bar = StatusBar(host)
        self.frame = sat_widgets.FocusFrame(self._buildList(), None, self.status_bar)
        PrimitivusWidget.__init__(self, self.frame, _(u"Contacts"))
        if on_click:
            urwid.connect_signal(self, "click", on_click, user_data)
        if on_change:
            urwid.connect_signal(self, "change", on_change, user_data)
        self.host.addListener("notification", self.onNotification, [self.profile])
        self.host.addListener("notificationsClear", self.onNotification, [self.profile])
        self.postInit()

    def update(self, entities=None, type_=None, profile=None):
        """Update display, keep focus"""
        # FIXME: full update is done each time, must handle entities, type_ and profile
        widget, position = self.frame.body.get_focus()
        self.frame.body = self._buildList()
        if position:
            try:
                self.frame.body.focus_position = position
            except IndexError:
                pass
        self._invalidate()
        self.host.redraw()  # FIXME: check if can be avoided

    def keypress(self, size, key):
        # FIXME: we have a temporary behaviour here: FOCUS_SWITCH change focus globally in the parent,
        #        and FOCUS_UP/DOWN is transwmitter to parent if we are respectively on the first or last element
        if key in sat_widgets.FOCUS_KEYS:
            if (
                key == a_key["FOCUS_SWITCH"]
                or (key == a_key["FOCUS_UP"] and self.frame.focus_position == "body")
                or (key == a_key["FOCUS_DOWN"] and self.frame.focus_position == "footer")
            ):
                return key
        if key == a_key["STATUS_HIDE"]:  # user wants to (un)hide contacts' statuses
            self.contact_list.show_status = not self.contact_list.show_status
            self.update()
        elif (
            key == a_key["DISCONNECTED_HIDE"]
        ):  # user wants to (un)hide disconnected contacts
            self.host.bridge.setParam(
                C.SHOW_OFFLINE_CONTACTS,
                C.boolConst(not self.contact_list.show_disconnected),
                "General",
                profile_key=self.profile,
            )
        elif key == a_key["RESOURCES_HIDE"]:  # user wants to (un)hide contacts resources
            self.contact_list.showResources(not self.contact_list.show_resources)
            self.update()
        return super(ContactList, self).keypress(size, key)

    # QuickWidget methods

    @staticmethod
    def getWidgetHash(target, profiles):
        profiles = sorted(profiles)
        return tuple(profiles)

    # modify the contact list

    def setFocus(self, text, select=False):
        """give focus to the first element that matches the given text. You can also
        pass in text a sat_frontends.tools.jid.JID (it's a subclass of unicode).

        @param text: contact group name, contact or muc userhost, muc private dialog jid
        @param select: if True, the element is also clicked
        """
        idx = 0
        for widget in self.frame.body.body:
            try:
                if isinstance(widget, sat_widgets.ClickableText):
                    # contact group
                    value = widget.getValue()
                elif isinstance(widget, sat_widgets.SelectableText):
                    # contact or muc
                    value = widget.data
                else:
                    # Divider instance
                    continue
                # there's sometimes a leading space
                if text.strip() == value.strip():
                    self.frame.body.focus_position = idx
                    if select:
                        self._contactClicked(False, widget, True)
                    return
            except AttributeError:
                pass
            idx += 1

        log.debug(u"Not element found for {} in setFocus".format(text))

    # events

    def _groupClicked(self, group_wid):
        group = group_wid.getValue()
        data = self.contact_list.getGroupData(group)
        data[C.GROUP_DATA_FOLDED] = not data.setdefault(C.GROUP_DATA_FOLDED, False)
        self.setFocus(group)
        self.update()

    def _contactClicked(self, use_bare_jid, contact_wid, selected):
        """Method called when a contact is clicked

        @param use_bare_jid: True if use_bare_jid is set in self._buildEntityWidget.
        @param contact_wid: widget of the contact, must have the entity set in data attribute
        @param selected: boolean returned by the widget, telling if it is selected
        """
        entity = contact_wid.data
        self.host.modeHint(C.MODE_INSERTION)
        self._emit("click", entity)

    def onNotification(self, entity, notif, profile):
        notifs = list(self.host.getNotifs(C.ENTITY_ALL, profile=self.profile))
        if notifs:
            self.title_dynamic = u"({})".format(len(notifs))
        else:
            self.title_dynamic = None
        self.host.redraw()  # FIXME: should not be necessary

    # Methods to build the widget

    def _buildEntityWidget(
        self,
        entity,
        keys=None,
        use_bare_jid=False,
        with_notifs=True,
        with_show_attr=True,
        markup_prepend=None,
        markup_append=None,
        special=False,
    ):
        """Build one contact markup data

        @param entity (jid.JID): entity to build
        @param keys (iterable): value to markup, in preferred order.
            The first available key will be used.
            If key starts with "cache_", it will be checked in cache,
            else, getattr will be done on entity with the key (e.g. getattr(entity, 'node')).
            If nothing full or keys is None, full entity is used.
        @param use_bare_jid (bool): if True, use bare jid for selected comparisons
        @param with_notifs (bool): if True, show notification count
        @param with_show_attr (bool): if True, show color corresponding to presence status
        @param markup_prepend (list): markup to prepend to the generated one before building the widget
        @param markup_append (list): markup to append to the generated one before building the widget
        @param special (bool): True if entity is a special one
        @return (list): markup data are expected by Urwid text widgets
        """
        markup = []
        if use_bare_jid:
            selected = {entity.bare for entity in self.contact_list._selected}
        else:
            selected = self.contact_list._selected
        if keys is None:
            entity_txt = entity
        else:
            cache = self.contact_list.getCache(entity)
            for key in keys:
                if key.startswith("cache_"):
                    entity_txt = cache.get(key[6:])
                else:
                    entity_txt = getattr(entity, key)
                if entity_txt:
                    break
            if not entity_txt:
                entity_txt = entity

        if with_show_attr:
            show = self.contact_list.getCache(entity, C.PRESENCE_SHOW)
            if show is None:
                show = C.PRESENCE_UNAVAILABLE
            show_icon, entity_attr = C.PRESENCE.get(show, ("", "default"))
            markup.insert(0, u"{} ".format(show_icon))
        else:
            entity_attr = "default"

        notifs = list(
            self.host.getNotifs(entity, exact_jid=special, profile=self.profile)
        )
        if notifs:
            header = [("cl_notifs", u"({})".format(len(notifs))), u" "]
            if list(
                self.host.getNotifs(entity.bare, C.NOTIFY_MENTION, profile=self.profile)
            ):
                header = ("cl_mention", header)
        else:
            header = u""

        markup.append((entity_attr, entity_txt))
        if markup_prepend:
            markup.insert(0, markup_prepend)
        if markup_append:
            markup.extend(markup_append)

        widget = sat_widgets.SelectableText(
            markup, selected=entity in selected, header=header
        )
        widget.data = entity
        widget.comp = entity_txt.lower()  # value to use for sorting
        urwid.connect_signal(
            widget, "change", self._contactClicked, user_args=[use_bare_jid]
        )
        return widget

    def _buildEntities(self, content, entities):
        """Add entity representation in widget list

        @param content: widget list, e.g. SimpleListWalker
        @param entities (iterable): iterable of JID to display
        """
        if not entities:
            return
        widgets = []  # list of built widgets

        for entity in entities:
            if (
                entity in self.contact_list._specials
                or not self.contact_list.entityVisible(entity)
            ):
                continue
            markup_extra = []
            if self.contact_list.show_resources:
                for resource in self.contact_list.getCache(entity, C.CONTACT_RESOURCES):
                    resource_disp = (
                        "resource_main"
                        if resource
                        == self.contact_list.getCache(entity, C.CONTACT_MAIN_RESOURCE)
                        else "resource",
                        "\n  " + resource,
                    )
                    markup_extra.append(resource_disp)
                    if self.contact_list.show_status:
                        status = self.contact_list.getCache(
                            jid.JID("%s/%s" % (entity, resource)), "status"
                        )
                        status_disp = ("status", "\n    " + status) if status else ""
                        markup_extra.append(status_disp)

            else:
                if self.contact_list.show_status:
                    status = self.contact_list.getCache(entity, "status")
                    status_disp = ("status", "\n  " + status) if status else ""
                    markup_extra.append(status_disp)
            widget = self._buildEntityWidget(
                entity,
                ("cache_nick", "cache_name", "node"),
                use_bare_jid=True,
                markup_append=markup_extra,
            )
            widgets.append(widget)

        widgets.sort(key=lambda widget: widget.comp)

        for widget in widgets:
            content.append(widget)

    def _buildSpecials(self, content):
        """Build the special entities"""
        specials = sorted(self.contact_list.getSpecials())
        current = None
        for entity in specials:
            if current is not None and current.bare == entity.bare:
                # nested entity (e.g. MUC private conversations)
                widget = self._buildEntityWidget(
                    entity, ("resource",), markup_prepend="  ", special=True
                )
            else:
                # the special widgets
                if entity.resource:
                    widget = self._buildEntityWidget(entity, ("resource",), special=True)
                else:
                    widget = self._buildEntityWidget(
                        entity,
                        ("cache_nick", "cache_name", "node"),
                        with_show_attr=False,
                        special=True,
                    )
            content.append(widget)

    def _buildList(self):
        """Build the main contact list widget"""
        content = urwid.SimpleListWalker([])

        self._buildSpecials(content)
        if self.contact_list._specials:
            content.append(urwid.Divider("="))

        groups = list(self.contact_list._groups)
        groups.sort(key=lambda x: x.lower() if x else x)
        for group in groups:
            data = self.contact_list.getGroupData(group)
            folded = data.get(C.GROUP_DATA_FOLDED, False)
            jids = list(data["jids"])
            if group is not None and (
                self.contact_list.anyEntityVisible(jids)
                or self.contact_list.show_empty_groups
            ):
                header = "[-]" if not folded else "[+]"
                widget = sat_widgets.ClickableText(group, header=header + " ")
                content.append(widget)
                urwid.connect_signal(widget, "click", self._groupClicked)
            if not folded:
                self._buildEntities(content, jids)
        not_in_roster = (
            set(self.contact_list._cache)
            .difference(self.contact_list._roster)
            .difference(self.contact_list._specials)
            .difference((self.contact_list.whoami.bare,))
        )
        if not_in_roster:
            content.append(urwid.Divider("-"))
            self._buildEntities(content, not_in_roster)

        return urwid.ListBox(content)


quick_widgets.register(QuickContactList, ContactList)
