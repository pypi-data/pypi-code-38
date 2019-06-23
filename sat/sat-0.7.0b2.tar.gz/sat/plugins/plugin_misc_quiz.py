#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing Quiz game
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
from twisted.internet import reactor
from twisted.words.protocols.jabber import client as jabber_client, jid
from time import time


NS_QG = "http://www.goffi.org/protocol/quiz"
QG_TAG = "quiz"

PLUGIN_INFO = {
    C.PI_NAME: "Quiz game plugin",
    C.PI_IMPORT_NAME: "Quiz",
    C.PI_TYPE: "Game",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0045", "XEP-0249", "ROOM-GAME"],
    C.PI_MAIN: "Quiz",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Quiz game"""),
}


class Quiz(object):
    def inheritFromRoomGame(self, host):
        global RoomGame
        RoomGame = host.plugins["ROOM-GAME"].__class__
        self.__class__ = type(
            self.__class__.__name__, (self.__class__, RoomGame, object), {}
        )

    def __init__(self, host):
        log.info(_("Plugin Quiz initialization"))
        self.inheritFromRoomGame(host)
        RoomGame._init_(
            self,
            host,
            PLUGIN_INFO,
            (NS_QG, QG_TAG),
            game_init={"stage": None},
            player_init={"score": 0},
        )
        host.bridge.addMethod(
            "quizGameLaunch",
            ".plugin",
            in_sign="asss",
            out_sign="",
            method=self._prepareRoom,
        )  # args: players, room_jid, profile
        host.bridge.addMethod(
            "quizGameCreate",
            ".plugin",
            in_sign="sass",
            out_sign="",
            method=self._createGame,
        )  # args: room_jid, players, profile
        host.bridge.addMethod(
            "quizGameReady",
            ".plugin",
            in_sign="sss",
            out_sign="",
            method=self._playerReady,
        )  # args: player, referee, profile
        host.bridge.addMethod(
            "quizGameAnswer",
            ".plugin",
            in_sign="ssss",
            out_sign="",
            method=self.playerAnswer,
        )
        host.bridge.addSignal(
            "quizGameStarted", ".plugin", signature="ssass"
        )  # args: room_jid, referee, players, profile
        host.bridge.addSignal(
            "quizGameNew",
            ".plugin",
            signature="sa{ss}s",
            doc={
                "summary": "Start a new game",
                "param_0": "room_jid: jid of game's room",
                "param_1": "game_data: data of the game",
                "param_2": "%(doc_profile)s",
            },
        )
        host.bridge.addSignal(
            "quizGameQuestion",
            ".plugin",
            signature="sssis",
            doc={
                "summary": "Send the current question",
                "param_0": "room_jid: jid of game's room",
                "param_1": "question_id: question id",
                "param_2": "question: question to ask",
                "param_3": "timer: timer",
                "param_4": "%(doc_profile)s",
            },
        )
        host.bridge.addSignal(
            "quizGamePlayerBuzzed",
            ".plugin",
            signature="ssbs",
            doc={
                "summary": "A player just pressed the buzzer",
                "param_0": "room_jid: jid of game's room",
                "param_1": "player: player who pushed the buzzer",
                "param_2": "pause: should the game be paused ?",
                "param_3": "%(doc_profile)s",
            },
        )
        host.bridge.addSignal(
            "quizGamePlayerSays",
            ".plugin",
            signature="sssis",
            doc={
                "summary": "A player just pressed the buzzer",
                "param_0": "room_jid: jid of game's room",
                "param_1": "player: player who pushed the buzzer",
                "param_2": "text: what the player say",
                "param_3": "delay: how long, in seconds, the text must appear",
                "param_4": "%(doc_profile)s",
            },
        )
        host.bridge.addSignal(
            "quizGameAnswerResult",
            ".plugin",
            signature="ssba{si}s",
            doc={
                "summary": "Result of the just given answer",
                "param_0": "room_jid: jid of game's room",
                "param_1": "player: player who gave the answer",
                "param_2": "good_answer: True if the answer is right",
                "param_3": "score: dict of score with player as key",
                "param_4": "%(doc_profile)s",
            },
        )
        host.bridge.addSignal(
            "quizGameTimerExpired",
            ".plugin",
            signature="ss",
            doc={
                "summary": "Nobody answered the question in time",
                "param_0": "room_jid: jid of game's room",
                "param_1": "%(doc_profile)s",
            },
        )
        host.bridge.addSignal(
            "quizGameTimerRestarted",
            ".plugin",
            signature="sis",
            doc={
                "summary": "Nobody answered the question in time",
                "param_0": "room_jid: jid of game's room",
                "param_1": "time_left: time left before timer expiration",
                "param_2": "%(doc_profile)s",
            },
        )

    def __game_data_to_xml(self, game_data):
        """Convert a game data dict to domish element"""
        game_data_elt = domish.Element((None, "game_data"))
        for data in game_data:
            data_elt = domish.Element((None, data))
            data_elt.addContent(game_data[data])
            game_data_elt.addChild(data_elt)
        return game_data_elt

    def __xml_to_game_data(self, game_data_elt):
        """Convert a domish element with game_data to a dict"""
        game_data = {}
        for data_elt in game_data_elt.elements():
            game_data[data_elt.name] = unicode(data_elt)
        return game_data

    def __answer_result_to_signal_args(self, answer_result_elt):
        """Parse answer result element and return a tuple of signal arguments
        @param answer_result_elt: answer result element
        @return: (player, good_answer, score)"""
        score = {}
        for score_elt in answer_result_elt.elements():
            score[score_elt["player"]] = int(score_elt["score"])
        return (
            answer_result_elt["player"],
            answer_result_elt["good_answer"] == str(True),
            score,
        )

    def __answer_result(self, player_answering, good_answer, game_data):
        """Convert a domish an answer_result element
        @param player_answering: player who gave the answer
        @param good_answer: True is the answer is right
        @param game_data: data of the game"""
        players_data = game_data["players_data"]
        score = {}
        for player in game_data["players"]:
            score[player] = players_data[player]["score"]

        answer_result_elt = domish.Element((None, "answer_result"))
        answer_result_elt["player"] = player_answering
        answer_result_elt["good_answer"] = str(good_answer)

        for player in score:
            score_elt = domish.Element((None, "score"))
            score_elt["player"] = player
            score_elt["score"] = str(score[player])
            answer_result_elt.addChild(score_elt)

        return answer_result_elt

    def __ask_question(self, question_id, question, timer):
        """Create a element for asking a question"""
        question_elt = domish.Element((None, "question"))
        question_elt["id"] = question_id
        question_elt["timer"] = str(timer)
        question_elt.addContent(question)
        return question_elt

    def __start_play(self, room_jid, game_data, profile):
        """Start the game (tell to the first player after dealer to play"""
        client = self.host.getClient(profile)
        game_data["stage"] = "play"
        next_player_idx = game_data["current_player"] = (
            game_data["init_player"] + 1
        ) % len(
            game_data["players"]
        )  # the player after the dealer start
        game_data["first_player"] = next_player = game_data["players"][next_player_idx]
        to_jid = jid.JID(room_jid.userhost() + "/" + next_player)
        mess = self.createGameElt(to_jid)
        mess.firstChildElement().addElement("your_turn")
        client.send(mess)

    def playerAnswer(self, player, referee, answer, profile_key=C.PROF_KEY_NONE):
        """Called when a player give an answer"""
        client = self.host.getClient(profile_key)
        log.debug(
            u"new player answer (%(profile)s): %(answer)s"
            % {"profile": client.profile, "answer": answer}
        )
        mess = self.createGameElt(jid.JID(referee))
        answer_elt = mess.firstChildElement().addElement("player_answer")
        answer_elt["player"] = player
        answer_elt.addContent(answer)
        client.send(mess)

    def timerExpired(self, room_jid, profile):
        """Called when nobody answered the question in time"""
        client = self.host.getClient(profile)
        game_data = self.games[room_jid]
        game_data["stage"] = "expired"
        mess = self.createGameElt(room_jid)
        mess.firstChildElement().addElement("timer_expired")
        client.send(mess)
        reactor.callLater(4, self.askQuestion, room_jid, client.profile)

    def pauseTimer(self, room_jid):
        """Stop the timer and save the time left"""
        game_data = self.games[room_jid]
        left = max(0, game_data["timer"].getTime() - time())
        game_data["timer"].cancel()
        game_data["time_left"] = int(left)
        game_data["previous_stage"] = game_data["stage"]
        game_data["stage"] = "paused"

    def restartTimer(self, room_jid, profile):
        """Restart a timer with the saved time"""
        client = self.host.getClient(profile)
        game_data = self.games[room_jid]
        assert game_data["time_left"] is not None
        mess = self.createGameElt(room_jid)
        mess.firstChildElement().addElement("timer_restarted")
        jabber_client.restarted_elt["time_left"] = str(game_data["time_left"])
        client.send(mess)
        game_data["timer"] = reactor.callLater(
            game_data["time_left"], self.timerExpired, room_jid, profile
        )
        game_data["time_left"] = None
        game_data["stage"] = game_data["previous_stage"]
        del game_data["previous_stage"]

    def askQuestion(self, room_jid, profile):
        """Ask a new question"""
        client = self.host.getClient(profile)
        game_data = self.games[room_jid]
        game_data["stage"] = "question"
        game_data["question_id"] = "1"
        timer = 30
        mess = self.createGameElt(room_jid)
        mess.firstChildElement().addChild(
            self.__ask_question(
                game_data["question_id"], u"Quel est l'âge du capitaine ?", timer
            )
        )
        client.send(mess)
        game_data["timer"] = reactor.callLater(
            timer, self.timerExpired, room_jid, profile
        )
        game_data["time_left"] = None

    def checkAnswer(self, room_jid, player, answer, profile):
        """Check if the answer given is right"""
        client = self.host.getClient(profile)
        game_data = self.games[room_jid]
        players_data = game_data["players_data"]
        good_answer = game_data["question_id"] == "1" and answer == "42"
        players_data[player]["score"] += 1 if good_answer else -1
        players_data[player]["score"] = min(9, max(0, players_data[player]["score"]))

        mess = self.createGameElt(room_jid)
        mess.firstChildElement().addChild(
            self.__answer_result(player, good_answer, game_data)
        )
        client.send(mess)

        if good_answer:
            reactor.callLater(4, self.askQuestion, room_jid, profile)
        else:
            reactor.callLater(4, self.restartTimer, room_jid, profile)

    def newGame(self, room_jid, profile):
        """Launch a new round"""
        common_data = {"game_score": 0}
        new_game_data = {
            "instructions": _(
                u"""Bienvenue dans cette partie rapide de quizz, le premier à atteindre le score de 9 remporte le jeu

Attention, tu es prêt ?"""
            )
        }
        msg_elts = self.__game_data_to_xml(new_game_data)
        RoomGame.newRound(self, room_jid, (common_data, msg_elts), profile)
        reactor.callLater(10, self.askQuestion, room_jid, profile)

    def room_game_cmd(self, mess_elt, profile):
        client = self.host.getClient(profile)
        from_jid = jid.JID(mess_elt["from"])
        room_jid = jid.JID(from_jid.userhost())
        game_elt = mess_elt.firstChildElement()
        game_data = self.games[room_jid]
        #  if 'players_data' in game_data:
        #      players_data = game_data['players_data']

        for elt in game_elt.elements():

            if elt.name == "started":  # new game created
                players = []
                for player in elt.elements():
                    players.append(unicode(player))
                self.host.bridge.quizGameStarted(
                    room_jid.userhost(), from_jid.full(), players, profile
                )

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
                    self.newGame(room_jid, profile)

            elif elt.name == "game_data":
                self.host.bridge.quizGameNew(
                    room_jid.userhost(), self.__xml_to_game_data(elt), profile
                )

            elif elt.name == "question":  # A question is asked
                self.host.bridge.quizGameQuestion(
                    room_jid.userhost(),
                    elt["id"],
                    unicode(elt),
                    int(elt["timer"]),
                    profile,
                )

            elif elt.name == "player_answer":
                player = elt["player"]
                pause = (
                    game_data["stage"] == "question"
                )  # we pause the game only if we are have a question at the moment
                # we first send a buzzer message
                mess = self.createGameElt(room_jid)
                buzzer_elt = mess.firstChildElement().addElement("player_buzzed")
                buzzer_elt["player"] = player
                buzzer_elt["pause"] = str(pause)
                client.send(mess)
                if pause:
                    self.pauseTimer(room_jid)
                    # and we send the player answer
                    mess = self.createGameElt(room_jid)
                    _answer = unicode(elt)
                    say_elt = mess.firstChildElement().addElement("player_says")
                    say_elt["player"] = player
                    say_elt.addContent(_answer)
                    say_elt["delay"] = "3"
                    reactor.callLater(2, client.send, mess)
                    reactor.callLater(
                        6, self.checkAnswer, room_jid, player, _answer, profile=profile
                    )

            elif elt.name == "player_buzzed":
                self.host.bridge.quizGamePlayerBuzzed(
                    room_jid.userhost(), elt["player"], elt["pause"] == str(True), profile
                )

            elif elt.name == "player_says":
                self.host.bridge.quizGamePlayerSays(
                    room_jid.userhost(),
                    elt["player"],
                    unicode(elt),
                    int(elt["delay"]),
                    profile,
                )

            elif elt.name == "answer_result":
                player, good_answer, score = self.__answer_result_to_signal_args(elt)
                self.host.bridge.quizGameAnswerResult(
                    room_jid.userhost(), player, good_answer, score, profile
                )

            elif elt.name == "timer_expired":
                self.host.bridge.quizGameTimerExpired(room_jid.userhost(), profile)

            elif elt.name == "timer_restarted":
                self.host.bridge.quizGameTimerRestarted(
                    room_jid.userhost(), int(elt["time_left"]), profile
                )

            else:
                log.error(_(u"Unmanaged game element: %s") % elt.name)
