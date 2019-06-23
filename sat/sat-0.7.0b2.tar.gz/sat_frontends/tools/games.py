#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
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

"""This library help manage general games (e.g. card games) and it is shared by the frontends"""

SUITS_ORDER = [
    "pique",
    "coeur",
    "trefle",
    "carreau",
    "atout",
]  # I have switched the usual order 'trefle' and 'carreau' because card are more easy to see if suit colour change (black, red, black, red)
VALUES_ORDER = [str(i) for i in xrange(1, 11)] + ["valet", "cavalier", "dame", "roi"]


class TarotCard(object):
    """This class is used to represent a car logically"""

    def __init__(self, tuple_card):
        """@param tuple_card: tuple (suit, value)"""
        self.suit, self.value = tuple_card
        self.bout = self.suit == "atout" and self.value in ["1", "21", "excuse"]
        if self.bout or self.value == "roi":
            self.points = 4.5
        elif self.value == "dame":
            self.points = 3.5
        elif self.value == "cavalier":
            self.points = 2.5
        elif self.value == "valet":
            self.points = 1.5
        else:
            self.points = 0.5

    def get_tuple(self):
        return (self.suit, self.value)

    @staticmethod
    def from_tuples(tuple_list):
        result = []
        for card_tuple in tuple_list:
            result.append(TarotCard(card_tuple))
        return result

    def __cmp__(self, other):
        if other is None:
            return 1
        if self.suit != other.suit:
            idx1 = SUITS_ORDER.index(self.suit)
            idx2 = SUITS_ORDER.index(other.suit)
            return idx1.__cmp__(idx2)
        if self.suit == "atout":
            if self.value == other.value == "excuse":
                return 0
            if self.value == "excuse":
                return -1
            if other.value == "excuse":
                return 1
            return int(self.value).__cmp__(int(other.value))
        # at this point we have the same suit which is not 'atout'
        idx1 = VALUES_ORDER.index(self.value)
        idx2 = VALUES_ORDER.index(other.value)
        return idx1.__cmp__(idx2)

    def __str__(self):
        return "[%s,%s]" % (self.suit, self.value)


# These symbols are diplayed by Libervia next to the player's nicknames
SYMBOLS = {"Radiocol": [u"♬"], "Tarot": [u"♠", u"♣", u"♥", u"♦"]}
