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

from sat.core import log as logging

log = logging.getLogger(__name__)
import urwid
from urwid_satext import sat_widgets
from sat_frontends.primitivus.keys import action_key_map as a_key


class PrimitivusWidget(urwid.WidgetWrap):
    """Base widget for Primitivus"""

    def __init__(self, w, title=""):
        self._title = title
        self._title_dynamic = None
        self._original_widget = w
        urwid.WidgetWrap.__init__(self, self._getDecoration(w))

    @property
    def title(self):
        """Text shown in title bar of the widget"""

        # profiles currently managed by frontend
        try:
            all_profiles = self.host.profiles
        except AttributeError:
            all_profiles = []

        # profiles managed by the widget
        try:
            profiles = self.profiles
        except AttributeError:
            try:
                profiles = [self.profile]
            except AttributeError:
                profiles = []

        title_elts = []
        if self._title:
            title_elts.append(self._title)
        if self._title_dynamic:
            title_elts.append(self._title_dynamic)
        if len(all_profiles) > 1 and profiles:
            title_elts.append(u"[{}]".format(u", ".join(profiles)))
        return sat_widgets.SurroundedText(u" ".join(title_elts))

    @title.setter
    def title(self, value):
        self._title = value
        if self.decorationVisible:
            self.showDecoration()

    @property
    def title_dynamic(self):
        """Dynamic part of title"""
        return self._title_dynamic

    @title_dynamic.setter
    def title_dynamic(self, value):
        self._title_dynamic = value
        if self.decorationVisible:
            self.showDecoration()

    @property
    def decorationVisible(self):
        """True if the decoration is visible"""
        return isinstance(self._w, sat_widgets.LabelLine)

    def keypress(self, size, key):
        if key == a_key["DECORATION_HIDE"]:  # user wants to (un)hide widget decoration
            show = not self.decorationVisible
            self.showDecoration(show)
        else:
            return super(PrimitivusWidget, self).keypress(size, key)

    def _getDecoration(self, widget):
        return sat_widgets.LabelLine(widget, self.title)

    def showDecoration(self, show=True):
        """Show/Hide the decoration around the window"""
        self._w = (
            self._getDecoration(self._original_widget) if show else self._original_widget
        )

    def getMenu(self):
        raise NotImplementedError
