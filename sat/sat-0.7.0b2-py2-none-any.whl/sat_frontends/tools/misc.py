#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT helpers methods for plugins
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


class InputHistory(object):
    def _updateInputHistory(self, text=None, step=None, callback=None, mode=""):
        """Update the lists of previously sent messages. Several lists can be
        handled as they are stored in a dictionary, the argument "mode" being
        used as the entry key. There's also a temporary list to allow you play
        with previous entries before sending a new message. Parameters values
        can be combined: text is None and step is None to initialize a main
        list and the temporary one, step is None to update a list and
        reinitialize the temporary one, step is not None to update
        the temporary list between two messages.
        @param text: text to be saved.
        @param step: step to move the temporary index.
        @param callback: method to display temporary entries.
        @param mode: the dictionary key for main lists.
        """
        if not hasattr(self, "input_histories"):
            self.input_histories = {}
        history = self.input_histories.setdefault(mode, [])
        if step is None and text is not None:
            # update the main list
            if text in history:
                history.remove(text)
            history.append(text)
        length = len(history)
        if step is None or length == 0:
            # prepare the temporary list and index
            self.input_history_tmp = history[:]
            self.input_history_tmp.append("")
            self.input_history_index = length
        if step is None:
            return
        # update the temporary list
        if text is not None:
            # save the current entry
            self.input_history_tmp[self.input_history_index] = text
        # move to another entry if possible
        index_tmp = self.input_history_index + step
        if index_tmp >= 0 and index_tmp < len(self.input_history_tmp):
            if callback is not None:
                callback(self.input_history_tmp[index_tmp])
            self.input_history_index = index_tmp


class FlagsHandler(object):
    """Small class to handle easily option flags

    the instance is initialized with an iterable
    then attribute return True if flag is set, False else.
    """

    def __init__(self, flags):
        self.flags = set(flags or [])
        self._used_flags = set()

    def __getattr__(self, flag):
        self._used_flags.add(flag)
        return flag in self.flags

    def __len__(self):
        return len(self.flags)

    def __iter__(self):
        return self.flags.__iter__()

    @property
    def all_used(self):
        """Return True if all flags have been used"""
        return self._used_flags.issuperset(self.flags)

    @property
    def unused(self):
        """Return flags which has not been used yet"""
        return self.flags.difference(self._used_flags)
