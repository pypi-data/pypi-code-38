#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing French Tarot game
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
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.words.xish import domish
from twisted.words.protocols.jabber import jid
from twisted.internet import defer
from wokkel import data_form

from sat.memory import memory
from sat.tools import xml_tools
from sat_frontends.tools.games import TarotCard
import random


NS_CG = "http://www.goffi.org/protocol/card_game"
CG_TAG = "card_game"

PLUGIN_INFO = {
    C.PI_NAME: "Tarot cards plugin",
    C.PI_IMPORT_NAME: "Tarot",
    C.PI_TYPE: "Misc",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0045", "XEP-0249", "ROOM-GAME"],
    C.PI_MAIN: "Tarot",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Tarot card game"""),
}


class Tarot(object):
    def inheritFromRoomGame(self, host):
        global RoomGame
        RoomGame = host.plugins["ROOM-GAME"].__class__
        self.__class__ = type(
            self.__class__.__name__, (self.__class__, RoomGame, object), {}
        )

    def __init__(self, host):
        log.info(_("Plugin Tarot initialization"))
        self._sessions = memory.Sessions()
        self.inheritFromRoomGame(host)
        RoomGame._init_(
            self,
            host,
            PLUGIN_INFO,
            (NS_CG, CG_TAG),
            game_init={
                "hand_size": 18,
                "init_player": 0,
                "current_player": None,
                "contrat": None,
                "stage": None,
            },
            player_init={"score": 0},
        )
        self.contrats = [
            _("Passe"),
            _("Petite"),
            _("Garde"),
            _("Garde Sans"),
            _("Garde Contre"),
        ]
        host.bridge.addMethod(
            "tarotGameLaunch",
            ".plugin",
            in_sign="asss",
            out_sign="",
            method=self._prepareRoom,
            async=True,
        )  # args: players, room_jid, profile
        host.bridge.addMethod(
            "tarotGameCreate",
            ".plugin",
            in_sign="sass",
            out_sign="",
            method=self._createGame,
        )  # args: room_jid, players, profile
        host.bridge.addMethod(
            "tarotGameReady",
            ".plugin",
            in_sign="sss",
            out_sign="",
            method=self._playerReady,
        )  # args: player, referee, profile
        host.bridge.addMethod(
            "tarotGamePlayCards",
            ".plugin",
            in_sign="ssa(ss)s",
            out_sign="",
            method=self.play_cards,
        )  # args: player, referee, cards, profile
        host.bridge.addSignal(
            "tarotGamePlayers", ".plugin", signature="ssass"
        )  # args: room_jid, referee, players, profile
        host.bridge.addSignal(
            "tarotGameStarted", ".plugin", signature="ssass"
        )  # args: room_jid, referee, players, profile
        host.bridge.addSignal(
            "tarotGameNew", ".plugin", signature="sa(ss)s"
        )  # args: room_jid, hand, profile
        host.bridge.addSignal(
            "tarotGameChooseContrat", ".plugin", signature="sss"
        )  # args: room_jid, xml_data, profile
        host.bridge.addSignal(
            "tarotGameShowCards", ".plugin", signature="ssa(ss)a{ss}s"
        )  # args: room_jid, type ["chien", "poignée",...], cards, data[dict], profile
        host.bridge.addSignal(
            "tarotGameCardsPlayed", ".plugin", signature="ssa(ss)s"
        )  # args: room_jid, player, type ["chien", "poignée",...], cards, data[dict], profile
        host.bridge.addSignal(
            "tarotGameYourTurn", ".plugin", signature="ss"
        )  # args: room_jid, profile
        host.bridge.addSignal(
            "tarotGameScore", ".plugin", signature="ssasass"
        )  # args: room_jid, xml_data, winners (list of nicks), loosers (list of nicks), profile
        host.bridge.addSignal(
            "tarotGameInvalidCards", ".plugin", signature="ssa(ss)a(ss)s"
        )  # args: room_jid, game phase, played_cards, invalid_cards, profile
        self.deck_ordered = []
        for value in ["excuse"] + map(str, range(1, 22)):
            self.deck_ordered.append(TarotCard(("atout", value)))
        for suit in ["pique", "coeur", "carreau", "trefle"]:
            for value in map(str, range(1, 11)) + ["valet", "cavalier", "dame", "roi"]:
                self.deck_ordered.append(TarotCard((suit, value)))
        self.__choose_contrat_id = host.registerCallback(
            self._contratChoosed, with_data=True
        )
        self.__score_id = host.registerCallback(self._scoreShowed, with_data=True)

    def __card_list_to_xml(self, cards_list, elt_name):
        """Convert a card list to domish element"""
        cards_list_elt = domish.Element((None, elt_name))
        for card in cards_list:
            card_elt = domish.Element((None, "card"))
            card_elt["suit"] = card.suit
            card_elt["value"] = card.value
            cards_list_elt.addChild(card_elt)
        return cards_list_elt

    def __xml_to_list(self, cards_list_elt):
        """Convert a domish element with cards to a list of tuples"""
        cards_list = []
        for card in cards_list_elt.elements():
            cards_list.append((card["suit"], card["value"]))
        return cards_list

    def __ask_contrat(self):
        """Create a element for asking contrat"""
        contrat_elt = domish.Element((None, "contrat"))
        form = data_form.Form("form", title=_("contrat selection"))
        field = data_form.Field(
            "list-single",
            "contrat",
            options=map(data_form.Option, self.contrats),
            required=True,
        )
        form.addField(field)
        contrat_elt.addChild(form.toElement())
        return contrat_elt

    def __give_scores(self, scores, winners, loosers):
        """Create an element to give scores
        @param scores: unicode (can contain line feed)
        @param winners: list of unicode nicks of winners
        @param loosers: list of unicode nicks of loosers"""

        score_elt = domish.Element((None, "score"))
        form = data_form.Form("form", title=_("scores"))
        for line in scores.split("\n"):
            field = data_form.Field("fixed", value=line)
            form.addField(field)
        score_elt.addChild(form.toElement())
        for winner in winners:
            winner_elt = domish.Element((None, "winner"))
            winner_elt.addContent(winner)
            score_elt.addChild(winner_elt)
        for looser in loosers:
            looser_elt = domish.Element((None, "looser"))
            looser_elt.addContent(looser)
            score_elt.addChild(looser_elt)
        return score_elt

    def __invalid_cards_elt(self, played_cards, invalid_cards, game_phase):
        """Create a element for invalid_cards error
        @param list_cards: list of Card
        @param game_phase: phase of the game ['ecart', 'play']"""
        error_elt = domish.Element((None, "error"))
        played_elt = self.__card_list_to_xml(played_cards, "played")
        invalid_elt = self.__card_list_to_xml(invalid_cards, "invalid")
        error_elt["type"] = "invalid_cards"
        error_elt["phase"] = game_phase
        error_elt.addChild(played_elt)
        error_elt.addChild(invalid_elt)
        return error_elt

    def __next_player(self, game_data, next_pl=None):
        """Increment player number & return player name
        @param next_pl: if given, then next_player is forced to this one
        """
        if next_pl:
            game_data["current_player"] = game_data["players"].index(next_pl)
            return next_pl
        else:
            pl_idx = game_data["current_player"] = (
                game_data["current_player"] + 1
            ) % len(game_data["players"])
            return game_data["players"][pl_idx]

    def __winner(self, game_data):
        """give the nick of the player who win this trick"""
        players_data = game_data["players_data"]
        first = game_data["first_player"]
        first_idx = game_data["players"].index(first)
        suit_asked = None
        strongest = None
        winner = None
        for idx in [(first_idx + i) % 4 for i in range(4)]:
            player = game_data["players"][idx]
            card = players_data[player]["played"]
            if card.value == "excuse":
                continue
            if suit_asked is None:
                suit_asked = card.suit
            if (card.suit == suit_asked or card.suit == "atout") and card > strongest:
                strongest = card
                winner = player
        assert winner
        return winner

    def __excuse_hack(self, game_data, played, winner):
        """give a low card to other team and keep excuse if trick is lost
        @param game_data: data of the game
        @param played: cards currently on the table
        @param winner: nick of the trick winner"""
        # TODO: manage the case where excuse is played on the last trick (and lost)
        players_data = game_data["players_data"]
        excuse = TarotCard(("atout", "excuse"))

        # we first check if the Excuse was already played
        # and if somebody is waiting for a card
        for player in game_data["players"]:
            if players_data[player]["wait_for_low"]:
                # the excuse owner has to give a card to somebody
                if winner == player:
                    # the excuse owner win the trick, we check if we have something to give
                    for card in played:
                        if card.points == 0.5:
                            pl_waiting = players_data[player]["wait_for_low"]
                            played.remove(card)
                            players_data[pl_waiting]["levees"].append(card)
                            log.debug(
                                _(
                                    u"Player %(excuse_owner)s give %(card_waited)s to %(player_waiting)s for Excuse compensation"
                                )
                                % {
                                    "excuse_owner": player,
                                    "card_waited": card,
                                    "player_waiting": pl_waiting,
                                }
                            )
                            return
                return

        if excuse not in played:
            # the Excuse is not on the table, nothing to do
            return

        excuse_player = None  # Who has played the Excuse ?
        for player in game_data["players"]:
            if players_data[player]["played"] == excuse:
                excuse_player = player
                break

        if excuse_player == winner:
            return  # the excuse player win the trick, nothing to do

        # first we remove the excuse from played cards
        played.remove(excuse)
        # then we give it back to the original owner
        owner_levees = players_data[excuse_player]["levees"]
        owner_levees.append(excuse)
        # finally we give a low card to the trick winner
        low_card = None
        # We look backward in cards won by the Excuse owner to
        # find a low value card
        for card_idx in range(len(owner_levees) - 1, -1, -1):
            if owner_levees[card_idx].points == 0.5:
                low_card = owner_levees[card_idx]
                del owner_levees[card_idx]
                players_data[winner]["levees"].append(low_card)
                log.debug(
                    _(
                        u"Player %(excuse_owner)s give %(card_waited)s to %(player_waiting)s for Excuse compensation"
                    )
                    % {
                        "excuse_owner": excuse_player,
                        "card_waited": low_card,
                        "player_waiting": winner,
                    }
                )
                break
        if not low_card:  # The player has no low card yet
            # TODO: manage case when player never win a trick with low card
            players_data[excuse_player]["wait_for_low"] = winner
            log.debug(
                _(
                    u"%(excuse_owner)s keep the Excuse but has not card to give, %(winner)s is waiting for one"
                )
                % {"excuse_owner": excuse_player, "winner": winner}
            )

    def __draw_game(self, game_data):
        """The game is draw, no score change
        @param game_data: data of the game
        @return: tuple with (string victory message, list of winners, list of loosers)"""
        players_data = game_data["players_data"]
        scores_str = _("Draw game")
        scores_str += "\n"
        for player in game_data["players"]:
            scores_str += _(
                u"\n--\n%(player)s:\nscore for this game ==> %(score_game)i\ntotal score ==> %(total_score)i"
            ) % {
                "player": player,
                "score_game": 0,
                "total_score": players_data[player]["score"],
            }
        log.debug(scores_str)

        return (scores_str, [], [])

    def __calculate_scores(self, game_data):
        """The game is finished, time to know who won :)
        @param game_data: data of the game
        @return: tuple with (string victory message, list of winners, list of loosers)"""
        players_data = game_data["players_data"]
        levees = players_data[game_data["attaquant"]]["levees"]
        score = 0
        nb_bouts = 0
        bouts = []
        for card in levees:
            if card.bout:
                nb_bouts += 1
                bouts.append(card.value)
            score += card.points

        # We do a basic check on score calculation
        check_score = 0
        defenseurs = game_data["players"][:]
        defenseurs.remove(game_data["attaquant"])
        for defenseur in defenseurs:
            for card in players_data[defenseur]["levees"]:
                check_score += card.points
        if game_data["contrat"] == "Garde Contre":
            for card in game_data["chien"]:
                check_score += card.points
        assert score + check_score == 91

        point_limit = None
        if nb_bouts == 3:
            point_limit = 36
        elif nb_bouts == 2:
            point_limit = 41
        elif nb_bouts == 1:
            point_limit = 51
        else:
            point_limit = 56
        if game_data["contrat"] == "Petite":
            contrat_mult = 1
        elif game_data["contrat"] == "Garde":
            contrat_mult = 2
        elif game_data["contrat"] == "Garde Sans":
            contrat_mult = 4
        elif game_data["contrat"] == "Garde Contre":
            contrat_mult = 6
        else:
            log.error(_("INTERNAL ERROR: contrat not managed (mispelled ?)"))
            assert False

        victory = score >= point_limit
        margin = abs(score - point_limit)
        points_defenseur = (margin + 25) * contrat_mult * (-1 if victory else 1)
        winners = []
        loosers = []
        player_score = {}
        for player in game_data["players"]:
            # TODO: adjust this for 3 and 5 players variants
            # TODO: manage bonuses (petit au bout, poignée, chelem)
            player_score[player] = (
                points_defenseur
                if player != game_data["attaquant"]
                else points_defenseur * -3
            )
            players_data[player]["score"] += player_score[
                player
            ]  # we add score of this game to the global score
            if player_score[player] > 0:
                winners.append(player)
            else:
                loosers.append(player)

        scores_str = _(
            u"The attacker (%(attaquant)s) makes %(points)i and needs to make %(point_limit)i (%(nb_bouts)s oulder%(plural)s%(separator)s%(bouts)s): (s)he %(victory)s"
        ) % {
            "attaquant": game_data["attaquant"],
            "points": score,
            "point_limit": point_limit,
            "nb_bouts": nb_bouts,
            "plural": "s" if nb_bouts > 1 else "",
            "separator": ": " if nb_bouts != 0 else "",
            "bouts": ",".join(map(str, bouts)),
            "victory": "wins" if victory else "looses",
        }
        scores_str += "\n"
        for player in game_data["players"]:
            scores_str += _(
                u"\n--\n%(player)s:\nscore for this game ==> %(score_game)i\ntotal score ==> %(total_score)i"
            ) % {
                "player": player,
                "score_game": player_score[player],
                "total_score": players_data[player]["score"],
            }
        log.debug(scores_str)

        return (scores_str, winners, loosers)

    def __invalid_cards(self, game_data, cards):
        """Checks that the player has the right to play what he wants to
        @param game_data: Game data
        @param cards: cards the player want to play
        @return forbidden_cards cards or empty list if cards are ok"""
        forbidden_cards = []
        if game_data["stage"] == "ecart":
            for card in cards:
                if card.bout or card.value == "roi":
                    forbidden_cards.append(card)
                # TODO: manage case where atouts (trumps) are in the dog
        elif game_data["stage"] == "play":
            biggest_atout = None
            suit_asked = None
            players = game_data["players"]
            players_data = game_data["players_data"]
            idx = players.index(game_data["first_player"])
            current_idx = game_data["current_player"]
            current_player = players[current_idx]
            if idx == current_idx:
                # the player is the first to play, he can play what he wants
                return forbidden_cards
            while idx != current_idx:
                player = players[idx]
                played_card = players_data[player]["played"]
                if not suit_asked and played_card.value != "excuse":
                    suit_asked = played_card.suit
                if played_card.suit == "atout" and played_card > biggest_atout:
                    biggest_atout = played_card
                idx = (idx + 1) % len(players)
            has_suit = (
                False
            )  # True if there is one card of the asked suit in the hand of the player
            has_atout = False
            biggest_hand_atout = None

            for hand_card in game_data["hand"][current_player]:
                if hand_card.suit == suit_asked:
                    has_suit = True
                if hand_card.suit == "atout":
                    has_atout = True
                if hand_card.suit == "atout" and hand_card > biggest_hand_atout:
                    biggest_hand_atout = hand_card

            assert len(cards) == 1
            card = cards[0]
            if card.suit != suit_asked and has_suit and card.value != "excuse":
                forbidden_cards.append(card)
                return forbidden_cards
            if card.suit != suit_asked and card.suit != "atout" and has_atout:
                forbidden_cards.append(card)
                return forbidden_cards
            if (
                card.suit == "atout"
                and card < biggest_atout
                and biggest_hand_atout > biggest_atout
                and card.value != "excuse"
            ):
                forbidden_cards.append(card)
        else:
            log.error(_("Internal error: unmanaged game stage"))
        return forbidden_cards

    def __start_play(self, room_jid, game_data, profile):
        """Start the game (tell to the first player after dealer to play"""
        game_data["stage"] = "play"
        next_player_idx = game_data["current_player"] = (
            game_data["init_player"] + 1
        ) % len(
            game_data["players"]
        )  # the player after the dealer start
        game_data["first_player"] = next_player = game_data["players"][next_player_idx]
        to_jid = jid.JID(room_jid.userhost() + "/" + next_player)  # FIXME: gof:
        self.send(to_jid, "your_turn", profile=profile)

    def _contratChoosed(self, raw_data, profile):
        """Will be called when the contrat is selected
        @param raw_data: contains the choosed session id and the chosen contrat
        @param profile_key: profile
        """
        try:
            session_data = self._sessions.profileGet(raw_data["session_id"], profile)
        except KeyError:
            log.warning(_("session id doesn't exist, session has probably expired"))
            # TODO: send error dialog
            return defer.succeed({})

        room_jid = session_data["room_jid"]
        referee_jid = self.games[room_jid]["referee"]
        player = self.host.plugins["XEP-0045"].getRoomNick(room_jid, profile)
        data = xml_tools.XMLUIResult2DataFormResult(raw_data)
        contrat = data["contrat"]
        log.debug(
            _(u"contrat [%(contrat)s] choosed by %(profile)s")
            % {"contrat": contrat, "profile": profile}
        )
        d = self.send(
            referee_jid,
            ("", "contrat_choosed"),
            {"player": player},
            content=contrat,
            profile=profile,
        )
        d.addCallback(lambda ignore: {})
        del self._sessions[raw_data["session_id"]]
        return d

    def _scoreShowed(self, raw_data, profile):
        """Will be called when the player closes the score dialog
        @param raw_data: nothing to retrieve from here but the session id
        @param profile_key: profile
        """
        try:
            session_data = self._sessions.profileGet(raw_data["session_id"], profile)
        except KeyError:
            log.warning(_("session id doesn't exist, session has probably expired"))
            # TODO: send error dialog
            return defer.succeed({})

        room_jid_s = session_data["room_jid"].userhost()
        # XXX: empty hand means to the frontend "reset the display"...
        self.host.bridge.tarotGameNew(room_jid_s, [], profile)
        del self._sessions[raw_data["session_id"]]
        return defer.succeed({})

    def play_cards(self, player, referee, cards, profile_key=C.PROF_KEY_NONE):
        """Must be call by player when the contrat is selected
        @param player: player's name
        @param referee: arbiter jid
        @cards: cards played (list of tuples)
        @profile_key: profile
        """
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            log.error(_(u"profile %s is unknown") % profile_key)
            return
        log.debug(
            _(u"Cards played by %(profile)s: [%(cards)s]")
            % {"profile": profile, "cards": cards}
        )
        elem = self.__card_list_to_xml(TarotCard.from_tuples(cards), "cards_played")
        self.send(jid.JID(referee), elem, {"player": player}, profile=profile)

    def newRound(self, room_jid, profile):
        game_data = self.games[room_jid]
        players = game_data["players"]
        game_data["first_player"] = None  # first player for the current trick
        game_data["contrat"] = None
        common_data = {
            "contrat": None,
            "levees": [],  # cards won
            "played": None,  # card on the table
            "wait_for_low": None,  # Used when a player wait for a low card because of excuse
        }

        hand = game_data["hand"] = {}
        hand_size = game_data["hand_size"]
        chien = game_data["chien"] = []
        deck = self.deck_ordered[:]
        random.shuffle(deck)
        for i in range(4):
            hand[players[i]] = deck[0:hand_size]
            del deck[0:hand_size]
        chien.extend(deck)
        del (deck[:])
        msg_elts = {}
        for player in players:
            msg_elts[player] = self.__card_list_to_xml(hand[player], "hand")

        RoomGame.newRound(self, room_jid, (common_data, msg_elts), profile)

        pl_idx = game_data["current_player"] = (game_data["init_player"] + 1) % len(
            players
        )  # the player after the dealer start
        player = players[pl_idx]
        to_jid = jid.JID(room_jid.userhost() + "/" + player)  # FIXME: gof:
        self.send(to_jid, self.__ask_contrat(), profile=profile)

    def room_game_cmd(self, mess_elt, profile):
        """
        @param mess_elt: instance of twisted.words.xish.domish.Element
        """
        client = self.host.getClient(profile)
        from_jid = jid.JID(mess_elt["from"])
        room_jid = jid.JID(from_jid.userhost())
        nick = self.host.plugins["XEP-0045"].getRoomNick(client, room_jid)

        game_elt = mess_elt.firstChildElement()
        game_data = self.games[room_jid]
        is_player = self.isPlayer(room_jid, nick)
        if "players_data" in game_data:
            players_data = game_data["players_data"]

        for elt in game_elt.elements():
            if not is_player and (elt.name not in ("started", "players")):
                continue  # user is in the room but not playing

            if elt.name in (
                "started",
                "players",
            ):  # new game created and/or players list updated
                players = []
                for player in elt.elements():
                    players.append(unicode(player))
                signal = (
                    self.host.bridge.tarotGameStarted
                    if elt.name == "started"
                    else self.host.bridge.tarotGamePlayers
                )
                signal(room_jid.userhost(), from_jid.full(), players, profile)

            elif elt.name == "player_ready":  # ready to play
                player = elt["player"]
                status = self.games[room_jid]["status"]
                nb_players = len(self.games[room_jid]["players"])
                status[player] = "ready"
                log.debug(
                    _(u"Player %(player)s is ready to start [status: %(status)s]")
                    % {"player": player, "status": status}
                )
                if (
                    status.values().count("ready") == nb_players
                ):  # everybody is ready, we can start the game
                    self.newRound(room_jid, profile)

            elif elt.name == "hand":  # a new hand has been received
                self.host.bridge.tarotGameNew(
                    room_jid.userhost(), self.__xml_to_list(elt), profile
                )

            elif elt.name == "contrat":  # it's time to choose contrat
                form = data_form.Form.fromElement(elt.firstChildElement())
                session_id, session_data = self._sessions.newSession(profile=profile)
                session_data["room_jid"] = room_jid
                xml_data = xml_tools.dataForm2XMLUI(
                    form, self.__choose_contrat_id, session_id
                ).toXml()
                self.host.bridge.tarotGameChooseContrat(
                    room_jid.userhost(), xml_data, profile
                )

            elif elt.name == "contrat_choosed":
                # TODO: check we receive the contrat from the right person
                # TODO: use proper XEP-0004 way for answering form
                player = elt["player"]
                players_data[player]["contrat"] = unicode(elt)
                contrats = [players_data[p]["contrat"] for p in game_data["players"]]
                if contrats.count(None):
                    # not everybody has choosed his contrat, it's next one turn
                    player = self.__next_player(game_data)
                    to_jid = jid.JID(room_jid.userhost() + "/" + player)  # FIXME: gof:
                    self.send(to_jid, self.__ask_contrat(), profile=profile)
                else:
                    best_contrat = [None, "Passe"]
                    for player in game_data["players"]:
                        contrat = players_data[player]["contrat"]
                        idx_best = self.contrats.index(best_contrat[1])
                        idx_pl = self.contrats.index(contrat)
                        if idx_pl > idx_best:
                            best_contrat[0] = player
                            best_contrat[1] = contrat
                    if best_contrat[1] == "Passe":
                        log.debug(_("Everybody is passing, round ended"))
                        to_jid = jid.JID(room_jid.userhost())
                        self.send(
                            to_jid,
                            self.__give_scores(*self.__draw_game(game_data)),
                            profile=profile,
                        )
                        game_data["init_player"] = (game_data["init_player"] + 1) % len(
                            game_data["players"]
                        )  # we change the dealer
                        for player in game_data["players"]:
                            game_data["status"][player] = "init"
                        return
                    log.debug(
                        _(u"%(player)s win the bid with %(contrat)s")
                        % {"player": best_contrat[0], "contrat": best_contrat[1]}
                    )
                    game_data["contrat"] = best_contrat[1]

                    if (
                        game_data["contrat"] == "Garde Sans"
                        or game_data["contrat"] == "Garde Contre"
                    ):
                        self.__start_play(room_jid, game_data, profile)
                        game_data["attaquant"] = best_contrat[0]
                    else:
                        # Time to show the chien to everybody
                        to_jid = jid.JID(room_jid.userhost())  # FIXME: gof:
                        elem = self.__card_list_to_xml(game_data["chien"], "chien")
                        self.send(
                            to_jid, elem, {"attaquant": best_contrat[0]}, profile=profile
                        )
                        # the attacker (attaquant) get the chien
                        game_data["hand"][best_contrat[0]].extend(game_data["chien"])
                        del game_data["chien"][:]

                    if game_data["contrat"] == "Garde Sans":
                        # The chien go into attaquant's (attacker) levees
                        players_data[best_contrat[0]]["levees"].extend(game_data["chien"])
                        del game_data["chien"][:]

            elif elt.name == "chien":  # we have received the chien
                log.debug(_("tarot: chien received"))
                data = {"attaquant": elt["attaquant"]}
                game_data["stage"] = "ecart"
                game_data["attaquant"] = elt["attaquant"]
                self.host.bridge.tarotGameShowCards(
                    room_jid.userhost(), "chien", self.__xml_to_list(elt), data, profile
                )

            elif elt.name == "cards_played":
                if game_data["stage"] == "ecart":
                    # TODO: show atouts (trumps) if player put some in écart
                    assert (
                        game_data["attaquant"] == elt["player"]
                    )  # TODO: throw an xml error here
                    list_cards = TarotCard.from_tuples(self.__xml_to_list(elt))
                    # we now check validity of card
                    invalid_cards = self.__invalid_cards(game_data, list_cards)
                    if invalid_cards:
                        elem = self.__invalid_cards_elt(
                            list_cards, invalid_cards, game_data["stage"]
                        )
                        self.send(
                            jid.JID(room_jid.userhost() + "/" + elt["player"]),
                            elem,
                            profile=profile,
                        )
                        return

                    # FIXME: gof: manage Garde Sans & Garde Contre cases
                    players_data[elt["player"]]["levees"].extend(
                        list_cards
                    )  # we add the chien to attaquant's levées
                    for card in list_cards:
                        game_data["hand"][elt["player"]].remove(card)

                    self.__start_play(room_jid, game_data, profile)

                elif game_data["stage"] == "play":
                    current_player = game_data["players"][game_data["current_player"]]
                    cards = TarotCard.from_tuples(self.__xml_to_list(elt))

                    if mess_elt["type"] == "groupchat":
                        self.host.bridge.tarotGameCardsPlayed(
                            room_jid.userhost(),
                            elt["player"],
                            self.__xml_to_list(elt),
                            profile,
                        )
                    else:
                        # we first check validity of card
                        invalid_cards = self.__invalid_cards(game_data, cards)
                        if invalid_cards:
                            elem = self.__invalid_cards_elt(
                                cards, invalid_cards, game_data["stage"]
                            )
                            self.send(
                                jid.JID(room_jid.userhost() + "/" + current_player),
                                elem,
                                profile=profile,
                            )
                            return
                        # the card played is ok, we forward it to everybody
                        # first we remove it from the hand and put in on the table
                        game_data["hand"][current_player].remove(cards[0])
                        players_data[current_player]["played"] = cards[0]

                        # then we forward the message
                        self.send(room_jid, elt, profile=profile)

                        # Did everybody played ?
                        played = [
                            players_data[player]["played"]
                            for player in game_data["players"]
                        ]
                        if all(played):
                            # everybody has played
                            winner = self.__winner(game_data)
                            log.debug(_(u"The winner of this trick is %s") % winner)
                            # the winner win the trick
                            self.__excuse_hack(game_data, played, winner)
                            players_data[elt["player"]]["levees"].extend(played)
                            # nothing left on the table
                            for player in game_data["players"]:
                                players_data[player]["played"] = None
                            if len(game_data["hand"][current_player]) == 0:
                                # no card left: the game is finished
                                elem = self.__give_scores(
                                    *self.__calculate_scores(game_data)
                                )
                                self.send(room_jid, elem, profile=profile)
                                game_data["init_player"] = (
                                    game_data["init_player"] + 1
                                ) % len(
                                    game_data["players"]
                                )  # we change the dealer
                                for player in game_data["players"]:
                                    game_data["status"][player] = "init"
                                return
                            # next player is the winner
                            next_player = game_data["first_player"] = self.__next_player(
                                game_data, winner
                            )
                        else:
                            next_player = self.__next_player(game_data)

                        # finally, we tell to the next player to play
                        to_jid = jid.JID(room_jid.userhost() + "/" + next_player)
                        self.send(to_jid, "your_turn", profile=profile)

            elif elt.name == "your_turn":
                self.host.bridge.tarotGameYourTurn(room_jid.userhost(), profile)

            elif elt.name == "score":
                form_elt = elt.elements(name="x", uri="jabber:x:data").next()
                winners = []
                loosers = []
                for winner in elt.elements(name="winner", uri=NS_CG):
                    winners.append(unicode(winner))
                for looser in elt.elements(name="looser", uri=NS_CG):
                    loosers.append(unicode(looser))
                form = data_form.Form.fromElement(form_elt)
                session_id, session_data = self._sessions.newSession(profile=profile)
                session_data["room_jid"] = room_jid
                xml_data = xml_tools.dataForm2XMLUI(
                    form, self.__score_id, session_id
                ).toXml()
                self.host.bridge.tarotGameScore(
                    room_jid.userhost(), xml_data, winners, loosers, profile
                )
            elif elt.name == "error":
                if elt["type"] == "invalid_cards":
                    played_cards = self.__xml_to_list(
                        elt.elements(name="played", uri=NS_CG).next()
                    )
                    invalid_cards = self.__xml_to_list(
                        elt.elements(name="invalid", uri=NS_CG).next()
                    )
                    self.host.bridge.tarotGameInvalidCards(
                        room_jid.userhost(),
                        elt["phase"],
                        played_cards,
                        invalid_cards,
                        profile,
                    )
                else:
                    log.error(_(u"Unmanaged error type: %s") % elt["type"])
            else:
                log.error(_(u"Unmanaged card game element: %s") % elt.name)

    def getSyncDataForPlayer(self, room_jid, nick):
        return []
