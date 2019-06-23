#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)
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

""" Tests for the plugin room game (base class for MUC games) """

from sat.core.i18n import _
from constants import Const
from sat.test import helpers, helpers_plugins
from sat.plugins import plugin_misc_room_game as plugin
from twisted.words.protocols.jabber.jid import JID
from wokkel.muc import User

from logging import WARNING

# Data used for test initialization
NAMESERVICE = "http://www.goffi.org/protocol/dummy"
TAG = "dummy"
PLUGIN_INFO = {
    "name": "Dummy plugin",
    "import_name": "DUMMY",
    "type": "MISC",
    "protocols": [],
    "dependencies": [],
    "main": "Dummy",
    "handler": "no",  # handler MUST be "no" (dynamic inheritance)
    "description": _("""Dummy plugin to test room game"""),
}

ROOM_JID = JID(Const.MUC_STR[0])
PROFILE = Const.PROFILE[0]
OTHER_PROFILE = Const.PROFILE[1]


class RoomGameTest(helpers.SatTestCase):
    def setUp(self):
        self.host = helpers.FakeSAT()

    def reinit(self, game_init={}, player_init={}):
        self.host.reinit()
        self.plugin = plugin.RoomGame(self.host)
        self.plugin._init_(
            self.host, PLUGIN_INFO, (NAMESERVICE, TAG), game_init, player_init
        )
        self.plugin_0045 = self.host.plugins["XEP-0045"] = helpers_plugins.FakeXEP_0045(
            self.host
        )
        self.plugin_0249 = self.host.plugins["XEP-0249"] = helpers_plugins.FakeXEP_0249(
            self.host
        )
        for profile in Const.PROFILE:
            self.host.getClient(profile)  # init self.host.profiles[profile]

    def initGame(self, muc_index, user_index):
        self.plugin_0045.joinRoom(user_index, muc_index)
        self.plugin._initGame(JID(Const.MUC_STR[muc_index]), Const.JID[user_index].user)

    def _expectedMessage(self, to, type_, tag, players=[]):
        content = "<%s" % tag
        if not players:
            content += "/>"
        else:
            content += ">"
            for i in xrange(0, len(players)):
                content += "<player index='%s'>%s</player>" % (i, players[i])
            content += "</%s>" % tag
        return "<message to='%s' type='%s'><%s xmlns='%s'>%s</dummy></message>" % (
            to.full(),
            type_,
            TAG,
            NAMESERVICE,
            content,
        )

    def test_createOrInvite_solo(self):
        self.reinit()
        self.plugin_0045.joinRoom(0, 0)
        self.plugin._createOrInvite(self.plugin_0045.getRoom(0, 0), [], Const.PROFILE[0])
        self.assertTrue(self.plugin._gameExists(ROOM_JID, True))

    def test_createOrInvite_multi_not_waiting(self):
        self.reinit()
        self.plugin_0045.joinRoom(0, 0)
        other_players = [Const.JID[1], Const.JID[2]]
        self.plugin._createOrInvite(
            self.plugin_0045.getRoom(0, 0), other_players, Const.PROFILE[0]
        )
        self.assertTrue(self.plugin._gameExists(ROOM_JID, True))

    def test_createOrInvite_multi_waiting(self):
        self.reinit(player_init={"score": 0})
        self.plugin_0045.joinRoom(0, 0)
        other_players = [Const.JID[1], Const.JID[2]]
        self.plugin._createOrInvite(
            self.plugin_0045.getRoom(0, 0), other_players, Const.PROFILE[0]
        )
        self.assertTrue(self.plugin._gameExists(ROOM_JID, False))
        self.assertFalse(self.plugin._gameExists(ROOM_JID, True))

    def test_initGame(self):
        self.reinit()
        self.initGame(0, 0)
        self.assertTrue(self.plugin.isReferee(ROOM_JID, Const.JID[0].user))
        self.assertEqual([], self.plugin.games[ROOM_JID]["players"])

    def test_checkJoinAuth(self):
        self.reinit()
        check = lambda value: getattr(self, "assert%s" % value)(
            self.plugin._checkJoinAuth(ROOM_JID, Const.JID[0], Const.JID[0].user)
        )
        check(False)
        # to test the "invited" mode, the referee must be different than the user to test
        self.initGame(0, 1)
        self.plugin.join_mode = self.plugin.ALL
        check(True)
        self.plugin.join_mode = self.plugin.INVITED
        check(False)
        self.plugin.invitations[ROOM_JID] = [(None, [Const.JID[0].userhostJID()])]
        check(True)
        self.plugin.join_mode = self.plugin.NONE
        check(False)
        self.plugin.games[ROOM_JID]["players"].append(Const.JID[0].user)
        check(True)

    def test_updatePlayers(self):
        self.reinit()
        self.initGame(0, 0)
        self.assertEqual(self.plugin.games[ROOM_JID]["players"], [])
        self.plugin._updatePlayers(ROOM_JID, [], True, Const.PROFILE[0])
        self.assertEqual(self.plugin.games[ROOM_JID]["players"], [])
        self.plugin._updatePlayers(ROOM_JID, ["user1"], True, Const.PROFILE[0])
        self.assertEqual(self.plugin.games[ROOM_JID]["players"], ["user1"])
        self.plugin._updatePlayers(ROOM_JID, ["user2", "user3"], True, Const.PROFILE[0])
        self.assertEqual(
            self.plugin.games[ROOM_JID]["players"], ["user1", "user2", "user3"]
        )
        self.plugin._updatePlayers(
            ROOM_JID, ["user2", "user3"], True, Const.PROFILE[0]
        )  # should not be stored twice
        self.assertEqual(
            self.plugin.games[ROOM_JID]["players"], ["user1", "user2", "user3"]
        )

    def test_synchronizeRoom(self):
        self.reinit()
        self.initGame(0, 0)
        self.plugin._synchronizeRoom(ROOM_JID, [Const.MUC[0]], Const.PROFILE[0])
        self.assertEqual(
            self.host.getSentMessageXml(0),
            self._expectedMessage(ROOM_JID, "groupchat", "players", []),
        )
        self.plugin.games[ROOM_JID]["players"].append("test1")
        self.plugin._synchronizeRoom(ROOM_JID, [Const.MUC[0]], Const.PROFILE[0])
        self.assertEqual(
            self.host.getSentMessageXml(0),
            self._expectedMessage(ROOM_JID, "groupchat", "players", ["test1"]),
        )
        self.plugin.games[ROOM_JID]["started"] = True
        self.plugin.games[ROOM_JID]["players"].append("test2")
        self.plugin._synchronizeRoom(ROOM_JID, [Const.MUC[0]], Const.PROFILE[0])
        self.assertEqual(
            self.host.getSentMessageXml(0),
            self._expectedMessage(ROOM_JID, "groupchat", "started", ["test1", "test2"]),
        )
        self.plugin.games[ROOM_JID]["players"].append("test3")
        self.plugin.games[ROOM_JID]["players"].append("test4")
        user1 = JID(ROOM_JID.userhost() + "/" + Const.JID[0].user)
        user2 = JID(ROOM_JID.userhost() + "/" + Const.JID[1].user)
        self.plugin._synchronizeRoom(ROOM_JID, [user1, user2], Const.PROFILE[0])
        self.assertEqualXML(
            self.host.getSentMessageXml(0),
            self._expectedMessage(
                user1, "normal", "started", ["test1", "test2", "test3", "test4"]
            ),
        )
        self.assertEqualXML(
            self.host.getSentMessageXml(0),
            self._expectedMessage(
                user2, "normal", "started", ["test1", "test2", "test3", "test4"]
            ),
        )

    def test_invitePlayers(self):
        self.reinit()
        self.initGame(0, 0)
        self.plugin_0045.joinRoom(0, 1)
        self.assertEqual(self.plugin.invitations[ROOM_JID], [])
        room = self.plugin_0045.getRoom(0, 0)
        nicks = self.plugin._invitePlayers(
            room, [Const.JID[1], Const.JID[2]], Const.JID[0].user, Const.PROFILE[0]
        )
        self.assertEqual(
            self.plugin.invitations[ROOM_JID][0][1],
            [Const.JID[1].userhostJID(), Const.JID[2].userhostJID()],
        )
        # the following assertion is True because Const.JID[1] and Const.JID[2] have the same userhost
        self.assertEqual(nicks, [Const.JID[1].user, Const.JID[2].user])

        nicks = self.plugin._invitePlayers(
            room, [Const.JID[1], Const.JID[3]], Const.JID[0].user, Const.PROFILE[0]
        )
        self.assertEqual(
            self.plugin.invitations[ROOM_JID][1][1],
            [Const.JID[1].userhostJID(), Const.JID[3].userhostJID()],
        )
        # this time Const.JID[1] and Const.JID[3] have the same user but the host differs
        self.assertEqual(nicks, [Const.JID[1].user])

    def test_checkInviteAuth(self):
        def check(value, index):
            nick = self.plugin_0045.getNick(0, index)
            getattr(self, "assert%s" % value)(
                self.plugin._checkInviteAuth(ROOM_JID, nick)
            )

        self.reinit()

        for mode in [
            self.plugin.FROM_ALL,
            self.plugin.FROM_NONE,
            self.plugin.FROM_REFEREE,
            self.plugin.FROM_PLAYERS,
        ]:
            self.plugin.invite_mode = mode
            check(True, 0)

        self.initGame(0, 0)
        self.plugin.invite_mode = self.plugin.FROM_ALL
        check(True, 0)
        check(True, 1)
        self.plugin.invite_mode = self.plugin.FROM_NONE
        check(True, 0)  # game initialized but not started yet, referee can invite
        check(False, 1)
        self.plugin.invite_mode = self.plugin.FROM_REFEREE
        check(True, 0)
        check(False, 1)
        user_nick = self.plugin_0045.joinRoom(0, 1)
        self.plugin.games[ROOM_JID]["players"].append(user_nick)
        self.plugin.invite_mode = self.plugin.FROM_PLAYERS
        check(True, 0)
        check(True, 1)
        check(False, 2)

    def test_isReferee(self):
        self.reinit()
        self.initGame(0, 0)
        self.assertTrue(self.plugin.isReferee(ROOM_JID, self.plugin_0045.getNick(0, 0)))
        self.assertFalse(self.plugin.isReferee(ROOM_JID, self.plugin_0045.getNick(0, 1)))

    def test_isPlayer(self):
        self.reinit()
        self.initGame(0, 0)
        self.assertTrue(self.plugin.isPlayer(ROOM_JID, self.plugin_0045.getNick(0, 0)))
        user_nick = self.plugin_0045.joinRoom(0, 1)
        self.plugin.games[ROOM_JID]["players"].append(user_nick)
        self.assertTrue(self.plugin.isPlayer(ROOM_JID, user_nick))
        self.assertFalse(self.plugin.isPlayer(ROOM_JID, self.plugin_0045.getNick(0, 2)))

    def test_checkWaitAuth(self):
        def check(value, other_players, confirmed, rest):
            room = self.plugin_0045.getRoom(0, 0)
            self.assertEqual(
                (value, confirmed, rest), self.plugin._checkWaitAuth(room, other_players)
            )

        self.reinit()
        self.initGame(0, 0)
        other_players = [Const.JID[1], Const.JID[3]]
        self.plugin.wait_mode = self.plugin.FOR_NONE
        check(True, [], [], [])
        check(
            True, [Const.JID[0]], [], [Const.JID[0]]
        )  # getRoomNickOfUser checks for the other users only
        check(True, other_players, [], other_players)
        self.plugin.wait_mode = self.plugin.FOR_ALL
        check(True, [], [], [])
        check(False, [Const.JID[0]], [], [Const.JID[0]])
        check(False, other_players, [], other_players)
        self.plugin_0045.joinRoom(0, 1)
        check(False, other_players, [], other_players)
        self.plugin_0045.joinRoom(0, 4)
        check(
            False,
            other_players,
            [self.plugin_0045.getNickOfUser(0, 1, 0)],
            [Const.JID[3]],
        )
        self.plugin_0045.joinRoom(0, 3)
        check(
            True,
            other_players,
            [
                self.plugin_0045.getNickOfUser(0, 1, 0),
                self.plugin_0045.getNickOfUser(0, 3, 0),
            ],
            [],
        )

        other_players = [Const.JID[1], Const.JID[3], Const.JID[2]]
        # the following assertion is True because Const.JID[1] and Const.JID[2] have the same userhost
        check(
            True,
            other_players,
            [
                self.plugin_0045.getNickOfUser(0, 1, 0),
                self.plugin_0045.getNickOfUser(0, 3, 0),
                self.plugin_0045.getNickOfUser(0, 2, 0),
            ],
            [],
        )

    def test_prepareRoom_trivial(self):
        self.reinit()
        other_players = []
        self.plugin.prepareRoom(other_players, ROOM_JID, PROFILE)
        self.assertTrue(self.plugin._gameExists(ROOM_JID, True))
        self.assertTrue(
            self.plugin._checkJoinAuth(ROOM_JID, Const.JID[0], Const.JID[0].user)
        )
        self.assertTrue(self.plugin._checkInviteAuth(ROOM_JID, Const.JID[0].user))
        self.assertEqual((True, [], []), self.plugin._checkWaitAuth(ROOM_JID, []))
        self.assertTrue(self.plugin.isReferee(ROOM_JID, Const.JID[0].user))
        self.assertTrue(self.plugin.isPlayer(ROOM_JID, Const.JID[0].user))
        self.assertEqual(
            (False, True), self.plugin._checkCreateGameAndInit(ROOM_JID, PROFILE)
        )

    def test_prepareRoom_invite(self):
        self.reinit()
        other_players = [Const.JID[1], Const.JID[2]]
        self.plugin.prepareRoom(other_players, ROOM_JID, PROFILE)
        room = self.plugin_0045.getRoom(0, 0)

        self.assertTrue(self.plugin._gameExists(ROOM_JID, True))
        self.assertTrue(
            self.plugin._checkJoinAuth(ROOM_JID, Const.JID[1], Const.JID[1].user)
        )
        self.assertFalse(
            self.plugin._checkJoinAuth(ROOM_JID, Const.JID[3], Const.JID[3].user)
        )
        self.assertFalse(self.plugin._checkInviteAuth(ROOM_JID, Const.JID[1].user))
        self.assertEqual(
            (True, [], other_players), self.plugin._checkWaitAuth(room, other_players)
        )

        player2_nick = self.plugin_0045.joinRoom(0, 1)
        self.plugin.userJoinedTrigger(room, room.roster[player2_nick], PROFILE)
        self.assertTrue(self.plugin.isPlayer(ROOM_JID, player2_nick))
        self.assertTrue(self.plugin._checkInviteAuth(ROOM_JID, player2_nick))
        self.assertFalse(self.plugin.isReferee(ROOM_JID, player2_nick))
        self.assertTrue(self.plugin.isPlayer(ROOM_JID, player2_nick))
        self.assertTrue(
            self.plugin.isPlayer(ROOM_JID, self.plugin_0045.getNickOfUser(0, 2, 0))
        )
        self.assertFalse(self.plugin.isPlayer(ROOM_JID, "xxx"))
        self.assertEqual(
            (False, False),
            self.plugin._checkCreateGameAndInit(ROOM_JID, Const.PROFILE[1]),
        )

    def test_prepareRoom_score1(self):
        self.reinit(player_init={"score": 0})
        other_players = [Const.JID[1], Const.JID[2]]
        self.plugin.prepareRoom(other_players, ROOM_JID, PROFILE)
        room = self.plugin_0045.getRoom(0, 0)

        self.assertFalse(self.plugin._gameExists(ROOM_JID, True))
        self.assertTrue(
            self.plugin._checkJoinAuth(ROOM_JID, Const.JID[1], Const.JID[1].user)
        )
        self.assertFalse(
            self.plugin._checkJoinAuth(ROOM_JID, Const.JID[3], Const.JID[3].user)
        )
        self.assertFalse(self.plugin._checkInviteAuth(ROOM_JID, Const.JID[1].user))
        self.assertEqual(
            (False, [], other_players), self.plugin._checkWaitAuth(room, other_players)
        )

        user_nick = self.plugin_0045.joinRoom(0, 1)
        self.plugin.userJoinedTrigger(room, room.roster[user_nick], PROFILE)
        self.assertTrue(self.plugin.isPlayer(ROOM_JID, user_nick))
        self.assertFalse(self.plugin._checkInviteAuth(ROOM_JID, user_nick))
        self.assertFalse(self.plugin.isReferee(ROOM_JID, user_nick))
        self.assertTrue(self.plugin.isPlayer(ROOM_JID, user_nick))
        # the following assertion is True because Const.JID[1] and Const.JID[2] have the same userhost
        self.assertTrue(
            self.plugin.isPlayer(ROOM_JID, self.plugin_0045.getNickOfUser(0, 2, 0))
        )
        # the following assertion is True because Const.JID[1] nick in the room is equal to Const.JID[3].user
        self.assertTrue(self.plugin.isPlayer(ROOM_JID, Const.JID[3].user))
        # but Const.JID[3] is actually not in the room
        self.assertEqual(self.plugin_0045.getNickOfUser(0, 3, 0), None)
        self.assertEqual(
            (True, False), self.plugin._checkCreateGameAndInit(ROOM_JID, Const.PROFILE[0])
        )

    def test_prepareRoom_score2(self):
        self.reinit(player_init={"score": 0})
        other_players = [Const.JID[1], Const.JID[4]]
        self.plugin.prepareRoom(other_players, ROOM_JID, PROFILE)
        room = self.plugin_0045.getRoom(0, 0)

        user_nick = self.plugin_0045.joinRoom(0, 1)
        self.plugin.userJoinedTrigger(room, room.roster[user_nick], PROFILE)
        self.assertEqual(
            (True, False), self.plugin._checkCreateGameAndInit(ROOM_JID, PROFILE)
        )
        user_nick = self.plugin_0045.joinRoom(0, 4)
        self.plugin.userJoinedTrigger(room, room.roster[user_nick], PROFILE)
        self.assertEqual(
            (False, True), self.plugin._checkCreateGameAndInit(ROOM_JID, PROFILE)
        )

    def test_userJoinedTrigger(self):
        self.reinit(player_init={"xxx": "xyz"})
        other_players = [Const.JID[1], Const.JID[3]]
        self.plugin.prepareRoom(other_players, ROOM_JID, PROFILE)
        nicks = [self.plugin_0045.getNick(0, 0)]

        self.assertEqual(
            self.host.getSentMessageXml(0),
            self._expectedMessage(ROOM_JID, "groupchat", "players", nicks),
        )
        self.assertTrue(len(self.plugin.invitations[ROOM_JID]) == 1)

        # wrong profile
        user_nick = self.plugin_0045.joinRoom(0, 1)
        room = self.plugin_0045.getRoom(0, 1)
        self.plugin.userJoinedTrigger(room, User(user_nick, Const.JID[1]), OTHER_PROFILE)
        self.assertEqual(
            self.host.getSentMessage(0), None
        )  # no new message has been sent
        self.assertFalse(self.plugin._gameExists(ROOM_JID, True))  # game not started

        # referee profile, user is allowed, wait for one more
        room = self.plugin_0045.getRoom(0, 0)
        self.plugin.userJoinedTrigger(room, User(user_nick, Const.JID[1]), PROFILE)
        nicks.append(user_nick)
        self.assertEqual(
            self.host.getSentMessageXml(0),
            self._expectedMessage(ROOM_JID, "groupchat", "players", nicks),
        )
        self.assertFalse(self.plugin._gameExists(ROOM_JID, True))  # game not started

        # referee profile, user is not allowed
        user_nick = self.plugin_0045.joinRoom(0, 4)
        self.plugin.userJoinedTrigger(room, User(user_nick, Const.JID[4]), PROFILE)
        self.assertEqual(
            self.host.getSentMessageXml(0),
            self._expectedMessage(
                JID(ROOM_JID.userhost() + "/" + user_nick), "normal", "players", nicks
            ),
        )
        self.assertFalse(self.plugin._gameExists(ROOM_JID, True))  # game not started

        # referee profile, user is allowed, everybody here
        user_nick = self.plugin_0045.joinRoom(0, 3)
        self.plugin.userJoinedTrigger(room, User(user_nick, Const.JID[3]), PROFILE)
        nicks.append(user_nick)
        self.assertEqual(
            self.host.getSentMessageXml(0),
            self._expectedMessage(ROOM_JID, "groupchat", "started", nicks),
        )
        self.assertTrue(self.plugin._gameExists(ROOM_JID, True))  # game started
        self.assertTrue(len(self.plugin.invitations[ROOM_JID]) == 0)

        # wait for none
        self.reinit()
        self.plugin.prepareRoom(other_players, ROOM_JID, PROFILE)
        self.assertNotEqual(self.host.getSentMessage(0), None)  # init messages
        room = self.plugin_0045.getRoom(0, 0)
        nicks = [self.plugin_0045.getNick(0, 0)]
        user_nick = self.plugin_0045.joinRoom(0, 3)
        self.plugin.userJoinedTrigger(room, User(user_nick, Const.JID[3]), PROFILE)
        nicks.append(user_nick)
        self.assertEqual(
            self.host.getSentMessageXml(0),
            self._expectedMessage(ROOM_JID, "groupchat", "started", nicks),
        )
        self.assertTrue(self.plugin._gameExists(ROOM_JID, True))

    def test_userLeftTrigger(self):
        self.reinit(player_init={"xxx": "xyz"})
        other_players = [Const.JID[1], Const.JID[3], Const.JID[4]]
        self.plugin.prepareRoom(other_players, ROOM_JID, PROFILE)
        room = self.plugin_0045.getRoom(0, 0)
        nicks = [self.plugin_0045.getNick(0, 0)]
        self.assertEqual(
            self.plugin.invitations[ROOM_JID][0][1],
            [
                Const.JID[1].userhostJID(),
                Const.JID[3].userhostJID(),
                Const.JID[4].userhostJID(),
            ],
        )

        # one user joins
        user_nick = self.plugin_0045.joinRoom(0, 1)
        self.plugin.userJoinedTrigger(room, User(user_nick, Const.JID[1]), PROFILE)
        nicks.append(user_nick)

        # the user leaves
        self.assertEqual(self.plugin.games[ROOM_JID]["players"], nicks)
        room = self.plugin_0045.getRoom(0, 1)
        # to not call self.plugin_0045.leaveRoom(0, 1) here, we are testing the trigger with a wrong profile
        self.plugin.userLeftTrigger(
            room, User(user_nick, Const.JID[1]), Const.PROFILE[1]
        )  # not the referee
        self.assertEqual(self.plugin.games[ROOM_JID]["players"], nicks)
        room = self.plugin_0045.getRoom(0, 0)
        user_nick = self.plugin_0045.leaveRoom(0, 1)
        self.plugin.userLeftTrigger(
            room, User(user_nick, Const.JID[1]), PROFILE
        )  # referee
        nicks.pop()
        self.assertEqual(self.plugin.games[ROOM_JID]["players"], nicks)

        # all the users join
        user_nick = self.plugin_0045.joinRoom(0, 1)
        self.plugin.userJoinedTrigger(room, User(user_nick, Const.JID[1]), PROFILE)
        nicks.append(user_nick)
        user_nick = self.plugin_0045.joinRoom(0, 3)
        self.plugin.userJoinedTrigger(room, User(user_nick, Const.JID[3]), PROFILE)
        nicks.append(user_nick)
        user_nick = self.plugin_0045.joinRoom(0, 4)
        self.plugin.userJoinedTrigger(room, User(user_nick, Const.JID[4]), PROFILE)
        nicks.append(user_nick)
        self.assertEqual(self.plugin.games[ROOM_JID]["players"], nicks)
        self.assertTrue(len(self.plugin.invitations[ROOM_JID]) == 0)

        # one user leaves
        user_nick = self.plugin_0045.leaveRoom(0, 4)
        self.plugin.userLeftTrigger(room, User(user_nick, Const.JID[4]), PROFILE)
        nicks.pop()
        self.assertEqual(
            self.plugin.invitations[ROOM_JID][0][1], [Const.JID[4].userhostJID()]
        )

        # another leaves
        user_nick = self.plugin_0045.leaveRoom(0, 3)
        self.plugin.userLeftTrigger(room, User(user_nick, Const.JID[3]), PROFILE)
        nicks.pop()
        self.assertEqual(
            self.plugin.invitations[ROOM_JID][0][1],
            [Const.JID[4].userhostJID(), Const.JID[3].userhostJID()],
        )

        # they can join again
        user_nick = self.plugin_0045.joinRoom(0, 3)
        self.plugin.userJoinedTrigger(room, User(user_nick, Const.JID[3]), PROFILE)
        nicks.append(user_nick)
        user_nick = self.plugin_0045.joinRoom(0, 4)
        self.plugin.userJoinedTrigger(room, User(user_nick, Const.JID[4]), PROFILE)
        nicks.append(user_nick)
        self.assertEqual(self.plugin.games[ROOM_JID]["players"], nicks)
        self.assertTrue(len(self.plugin.invitations[ROOM_JID]) == 0)

    def test__checkCreateGameAndInit(self):
        self.reinit()
        helpers.muteLogging()
        self.assertEqual(
            (False, False), self.plugin._checkCreateGameAndInit(ROOM_JID, PROFILE)
        )
        helpers.unmuteLogging()

        nick = self.plugin_0045.joinRoom(0, 0)
        self.assertEqual(
            (True, False), self.plugin._checkCreateGameAndInit(ROOM_JID, PROFILE)
        )
        self.assertTrue(self.plugin._gameExists(ROOM_JID, False))
        self.assertFalse(self.plugin._gameExists(ROOM_JID, True))
        self.assertTrue(self.plugin.isReferee(ROOM_JID, nick))

        helpers.muteLogging()
        self.assertEqual(
            (False, False), self.plugin._checkCreateGameAndInit(ROOM_JID, OTHER_PROFILE)
        )
        helpers.unmuteLogging()

        self.plugin_0045.joinRoom(0, 1)
        self.assertEqual(
            (False, False), self.plugin._checkCreateGameAndInit(ROOM_JID, OTHER_PROFILE)
        )

        self.plugin.createGame(ROOM_JID, [Const.JID[1]], PROFILE)
        self.assertEqual(
            (False, True), self.plugin._checkCreateGameAndInit(ROOM_JID, PROFILE)
        )
        self.assertEqual(
            (False, False), self.plugin._checkCreateGameAndInit(ROOM_JID, OTHER_PROFILE)
        )

    def test_createGame(self):

        self.reinit(player_init={"xxx": "xyz"})
        nicks = []
        for i in [0, 1, 3, 4]:
            nicks.append(self.plugin_0045.joinRoom(0, i))

        # game not exists
        self.plugin.createGame(ROOM_JID, nicks, PROFILE)
        self.assertTrue(self.plugin._gameExists(ROOM_JID, True))
        self.assertEqual(self.plugin.games[ROOM_JID]["players"], nicks)
        self.assertEqual(
            self.host.getSentMessageXml(0),
            self._expectedMessage(ROOM_JID, "groupchat", "started", nicks),
        )
        for nick in nicks:
            self.assertEqual("init", self.plugin.games[ROOM_JID]["status"][nick])
            self.assertEqual(
                self.plugin.player_init, self.plugin.games[ROOM_JID]["players_data"][nick]
            )
            self.plugin.games[ROOM_JID]["players_data"][nick]["xxx"] = nick
        for nick in nicks:
            # checks that a copy of self.player_init has been done and not a reference
            self.assertEqual(
                nick, self.plugin.games[ROOM_JID]["players_data"][nick]["xxx"]
            )

        # game exists, current profile is referee
        self.reinit(player_init={"xxx": "xyz"})
        self.initGame(0, 0)
        self.plugin.games[ROOM_JID]["started"] = True
        self.plugin.createGame(ROOM_JID, nicks, PROFILE)
        self.assertEqual(
            self.host.getSentMessageXml(0),
            self._expectedMessage(ROOM_JID, "groupchat", "started", nicks),
        )

        # game exists, current profile is not referee
        self.reinit(player_init={"xxx": "xyz"})
        self.initGame(0, 0)
        self.plugin.games[ROOM_JID]["started"] = True
        self.plugin_0045.joinRoom(0, 1)
        self.plugin.createGame(ROOM_JID, nicks, OTHER_PROFILE)
        self.assertEqual(
            self.host.getSentMessage(0), None
        )  # no sync message has been sent by other_profile
