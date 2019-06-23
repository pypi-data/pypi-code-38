#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Libervia: a Salut à Toi frontend
# Copyright (C) 2013-2016 Adrien Cossa <souliane@mailoo.org>

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


class QuickTagList(object):
    """This class manages a sorted list of tagged items, and a complementary sorted list of suggested but non tagged items."""

    def __init__(self, items=None):
        """

        @param items (list): the suggested list of non tagged items
        """
        self.tagged = []
        self.original = (
            items[:] if items else []
        )  # XXX: copy the list! It will be modified
        self.untagged = (
            items[:] if items else []
        )  # XXX: copy the list! It will be modified
        self.untagged.sort()

    @property
    def items(self):
        """Return a sorted list of all items, tagged or untagged.
        
        @return list
        """
        res = list(set(self.tagged).union(self.untagged))
        res.sort()
        return res

    def tag(self, items):
        """Tag some items.

        @param items (list): items to be tagged
        """
        for item in items:
            if item not in self.tagged:
                self.tagged.append(item)
            if item in self.untagged:
                self.untagged.remove(item)
        self.tagged.sort()
        self.untagged.sort()

    def untag(self, items):
        """Untag some items.
  
        @param items (list): items to be untagged
        """
        for item in items:
            if item not in self.untagged and item in self.original:
                self.untagged.append(item)
            if item in self.tagged:
                self.tagged.remove(item)
        self.tagged.sort()
        self.untagged.sort()
