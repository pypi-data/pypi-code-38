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
from sat_frontends.tools.games import TarotCard
from sat_frontends.quick_frontend.quick_game_tarot import QuickTarotGame
from sat_frontends.primitivus import xmlui
from sat_frontends.primitivus.keys import action_key_map as a_key


class CardDisplayer(urwid.Text):
    """Show a card"""

    signals = ["click"]

    def __init__(self, card):
        self.__selected = False
        self.card = card
        urwid.Text.__init__(self, card.getAttrText())

    def selectable(self):
        return True

    def keypress(self, size, key):
        if key == a_key["CARD_SELECT"]:
            self.select(not self.__selected)
            self._emit("click")
        return key

    def mouse_event(self, size, event, button, x, y, focus):
        if urwid.is_mouse_event(event) and button == 1:
            self.select(not self.__selected)
            self._emit("click")
            return True

        return False

    def select(self, state=True):
        self.__selected = state
        attr, txt = self.card.getAttrText()
        if self.__selected:
            attr += "_selected"
        self.set_text((attr, txt))
        self._invalidate()

    def isSelected(self):
        return self.__selected

    def getCard(self):
        return self.card

    def render(self, size, focus=False):
        canvas = urwid.CompositeCanvas(urwid.Text.render(self, size, focus))
        if focus:
            canvas.set_cursor((0, 0))
        return canvas


class Hand(urwid.WidgetWrap):
    """Used to display several cards, and manage a hand"""

    signals = ["click"]

    def __init__(self, hand=[], selectable=False, on_click=None, user_data=None):
        """@param hand: list of Card"""
        self.__selectable = selectable
        self.columns = urwid.Columns([], dividechars=1)
        if on_click:
            urwid.connect_signal(self, "click", on_click, user_data)
        if hand:
            self.update(hand)
        urwid.WidgetWrap.__init__(self, self.columns)

    def selectable(self):
        return self.__selectable

    def keypress(self, size, key):

        if CardDisplayer in [wid.__class__ for wid in self.columns.widget_list]:
            return self.columns.keypress(size, key)
        else:
            # No card displayed, we still have to manage the clicks
            if key == a_key["CARD_SELECT"]:
                self._emit("click", None)
            return key

    def getSelected(self):
        """Return a list of selected cards"""
        _selected = []
        for wid in self.columns.widget_list:
            if isinstance(wid, CardDisplayer) and wid.isSelected():
                _selected.append(wid.getCard())
        return _selected

    def update(self, hand):
        """Update the hand displayed in this widget
        @param hand: list of Card"""
        try:
            del self.columns.widget_list[:]
            del self.columns.column_types[:]
        except IndexError:
            pass
        self.columns.contents.append((urwid.Text(""), ("weight", 1, False)))
        for card in hand:
            widget = CardDisplayer(card)
            self.columns.widget_list.append(widget)
            self.columns.column_types.append(("fixed", 3))
            urwid.connect_signal(widget, "click", self.__onClick)
        self.columns.contents.append((urwid.Text(""), ("weight", 1, False)))
        self.columns.focus_position = 1

    def __onClick(self, card_wid):
        self._emit("click", card_wid)


class Card(TarotCard):
    """This class is used to represent a card, logically
    and give a text representation with attributes"""

    SIZE = 3  # size of a displayed card

    def __init__(self, suit, value):
        """@param file: path of the PNG file"""
        TarotCard.__init__(self, (suit, value))

    def getAttrText(self):
        """return text representation of the card with attributes"""
        try:
            value = "%02i" % int(self.value)
        except ValueError:
            value = self.value[0].upper() + self.value[1]
        if self.suit == "atout":
            if self.value == "excuse":
                suit = "c"
            else:
                suit = "A"
            color = "neutral"
        elif self.suit == "pique":
            suit = u"♠"
            color = "black"
        elif self.suit == "trefle":
            suit = u"♣"
            color = "black"
        elif self.suit == "coeur":
            suit = u"♥"
            color = "red"
        elif self.suit == "carreau":
            suit = u"♦"
            color = "red"
        if self.bout:
            color = "special"
        return ("card_%s" % color, u"%s%s" % (value, suit))

    def getWidget(self):
        """Return a widget representing the card"""
        return CardDisplayer(self)


class Table(urwid.FlowWidget):
    """Represent the cards currently on the table"""

    def __init__(self):
        self.top = self.left = self.bottom = self.right = None

    def putCard(self, location, card):
        """Put a card on the table
        @param location: where to put the card (top, left, bottom or right)
        @param card: Card to play or None"""
        assert location in ["top", "left", "bottom", "right"]
        assert isinstance(card, Card) or card == None
        if [getattr(self, place) for place in ["top", "left", "bottom", "right"]].count(
            None
        ) == 0:
            # If the table is full of card, we remove them
            self.top = self.left = self.bottom = self.right = None
        setattr(self, location, card)
        self._invalidate()

    def rows(self, size, focus=False):
        return self.display_widget(size, focus).rows(size, focus)

    def render(self, size, focus=False):
        return self.display_widget(size, focus).render(size, focus)

    def display_widget(self, size, focus):
        cards = {}
        max_col, = size
        separator = " - "
        margin = max((max_col - Card.SIZE) / 2, 0) * " "
        margin_center = max((max_col - Card.SIZE * 2 - len(separator)) / 2, 0) * " "
        for location in ["top", "left", "bottom", "right"]:
            card = getattr(self, location)
            cards[location] = card.getAttrText() if card else Card.SIZE * " "
        render_wid = [
            urwid.Text([margin, cards["top"]]),
            urwid.Text([margin_center, cards["left"], separator, cards["right"]]),
            urwid.Text([margin, cards["bottom"]]),
        ]
        return urwid.Pile(render_wid)


class TarotGame(QuickTarotGame, urwid.WidgetWrap):
    """Widget for card games"""

    def __init__(self, parent, referee, players):
        QuickTarotGame.__init__(self, parent, referee, players)
        self.loadCards()
        self.top = urwid.Pile([urwid.Padding(urwid.Text(self.top_nick), "center")])
        # self.parent.host.debug()
        self.table = Table()
        self.center = urwid.Columns(
            [
                ("fixed", len(self.left_nick), urwid.Filler(urwid.Text(self.left_nick))),
                urwid.Filler(self.table),
                (
                    "fixed",
                    len(self.right_nick),
                    urwid.Filler(urwid.Text(self.right_nick)),
                ),
            ]
        )
        """urwid.Pile([urwid.Padding(self.top_card_wid,'center'),
                             urwid.Columns([('fixed',len(self.left_nick),urwid.Text(self.left_nick)),
                                            urwid.Padding(self.center_cards_wid,'center'),
                                            ('fixed',len(self.right_nick),urwid.Text(self.right_nick))
                                           ]),
                             urwid.Padding(self.bottom_card_wid,'center')
                             ])"""
        self.hand_wid = Hand(selectable=True, on_click=self.onClick)
        self.main_frame = urwid.Frame(
            self.center, header=self.top, footer=self.hand_wid, focus_part="footer"
        )
        urwid.WidgetWrap.__init__(self, self.main_frame)
        self.parent.host.bridge.tarotGameReady(
            self.player_nick, referee, self.parent.profile
        )

    def loadCards(self):
        """Load all the cards in memory"""
        QuickTarotGame.loadCards(self)
        for value in map(str, range(1, 22)) + ["excuse"]:
            card = Card("atout", value)
            self.cards[card.suit, card.value] = card
            self.deck.append(card)
        for suit in ["pique", "coeur", "carreau", "trefle"]:
            for value in map(str, range(1, 11)) + ["valet", "cavalier", "dame", "roi"]:
                card = Card(suit, value)
                self.cards[card.suit, card.value] = card
                self.deck.append(card)

    def tarotGameNewHandler(self, hand):
        """Start a new game, with given hand"""
        if hand is []:  # reset the display after the scores have been showed
            self.resetRound()
            for location in ["top", "left", "bottom", "right"]:
                self.table.putCard(location, None)
            self.parent.host.redraw()
            self.parent.host.bridge.tarotGameReady(
                self.player_nick, self.referee, self.parent.profile
            )
            return
        QuickTarotGame.tarotGameNewHandler(self, hand)
        self.hand_wid.update(self.hand)
        self.parent.host.redraw()

    def tarotGameChooseContratHandler(self, xml_data):
        """Called when the player has to select his contrat
        @param xml_data: SàT xml representation of the form"""
        form = xmlui.create(
            self.parent.host,
            xml_data,
            title=_("Please choose your contrat"),
            flags=["NO_CANCEL"],
            profile=self.parent.profile,
        )
        form.show(valign="top")

    def tarotGameShowCardsHandler(self, game_stage, cards, data):
        """Display cards in the middle of the game (to show for e.g. chien ou poignée)"""
        QuickTarotGame.tarotGameShowCardsHandler(self, game_stage, cards, data)
        self.center.widget_list[1] = urwid.Filler(Hand(self.to_show))
        self.parent.host.redraw()

    def tarotGameYourTurnHandler(self):
        QuickTarotGame.tarotGameYourTurnHandler(self)

    def tarotGameScoreHandler(self, xml_data, winners, loosers):
        """Called when the round is over, display the scores
        @param xml_data: SàT xml representation of the form"""
        if not winners and not loosers:
            title = _("Draw game")
        else:
            title = _("You win \o/") if self.player_nick in winners else _("You loose :(")
        form = xmlui.create(
            self.parent.host,
            xml_data,
            title=title,
            flags=["NO_CANCEL"],
            profile=self.parent.profile,
        )
        form.show()

    def tarotGameInvalidCardsHandler(self, phase, played_cards, invalid_cards):
        """Invalid cards have been played
        @param phase: phase of the game
        @param played_cards: all the cards played
        @param invalid_cards: cards which are invalid"""
        QuickTarotGame.tarotGameInvalidCardsHandler(
            self, phase, played_cards, invalid_cards
        )
        self.hand_wid.update(self.hand)
        if self._autoplay == None:  # No dialog if there is autoplay
            self.parent.host.barNotify(_("Cards played are invalid !"))
        self.parent.host.redraw()

    def tarotGameCardsPlayedHandler(self, player, cards):
        """A card has been played by player"""
        QuickTarotGame.tarotGameCardsPlayedHandler(self, player, cards)
        self.table.putCard(self.getPlayerLocation(player), self.played[player])
        self._checkState()
        self.parent.host.redraw()

    def _checkState(self):
        if isinstance(
            self.center.widget_list[1].original_widget, Hand
        ):  # if we have a hand displayed
            self.center.widget_list[1] = urwid.Filler(
                self.table
            )  # we show again the table
            if self.state == "chien":
                self.to_show = []
                self.state = "wait"
            elif self.state == "wait_for_ecart":
                self.state = "ecart"
                self.hand.extend(self.to_show)
                self.hand.sort()
                self.to_show = []
                self.hand_wid.update(self.hand)

    ##EVENTS##
    def onClick(self, hand, card_wid):
        """Called when user do an action on the hand"""
        if not self.state in ["play", "ecart", "wait_for_ecart"]:
            # it's not our turn, we ignore the click
            card_wid.select(False)
            return
        self._checkState()
        if self.state == "ecart":
            if len(self.hand_wid.getSelected()) == 6:
                pop_up_widget = sat_widgets.ConfirmDialog(
                    _("Do you put these cards in chien ?"),
                    yes_cb=self.onEcartDone,
                    no_cb=self.parent.host.removePopUp,
                )
                self.parent.host.showPopUp(pop_up_widget)
        elif self.state == "play":
            card = card_wid.getCard()
            self.parent.host.bridge.tarotGamePlayCards(
                self.player_nick,
                self.referee,
                [(card.suit, card.value)],
                self.parent.profile,
            )
            self.hand.remove(card)
            self.hand_wid.update(self.hand)
            self.state = "wait"

    def onEcartDone(self, button):
        """Called when player has finished his écart"""
        ecart = []
        for card in self.hand_wid.getSelected():
            ecart.append((card.suit, card.value))
            self.hand.remove(card)
        self.hand_wid.update(self.hand)
        self.parent.host.bridge.tarotGamePlayCards(
            self.player_nick, self.referee, ecart, self.parent.profile
        )
        self.state = "wait"
        self.parent.host.removePopUp()
