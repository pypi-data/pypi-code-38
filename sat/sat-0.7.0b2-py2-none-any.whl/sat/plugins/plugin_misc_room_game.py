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

from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.words.protocols.jabber import jid
from twisted.words.xish import domish
from twisted.internet import defer
from time import time
from wokkel import disco, iwokkel
from zope.interface import implements
import copy

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

# Don't forget to set it to False before you commit
_DEBUG = False

PLUGIN_INFO = {
    C.PI_NAME: "Room game",
    C.PI_IMPORT_NAME: "ROOM-GAME",
    C.PI_TYPE: "MISC",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0045", "XEP-0249"],
    C.PI_MAIN: "RoomGame",
    C.PI_HANDLER: "no",  # handler MUST be "no" (dynamic inheritance)
    C.PI_DESCRIPTION: _("""Base class for MUC games"""),
}


# FIXME: this plugin is broken, need to be fixed


class RoomGame(object):
    """This class is used to help launching a MUC game.

    Bridge methods callbacks: _prepareRoom, _playerReady, _createGame
    Triggered methods: userJoinedTrigger, userLeftTrigger
    Also called from subclasses: newRound

    For examples of messages sequences, please look in sub-classes.
    """

    # Values for self.invite_mode (who can invite after the game creation)
    FROM_ALL, FROM_NONE, FROM_REFEREE, FROM_PLAYERS = xrange(0, 4)
    # Values for self.wait_mode (for who we should wait before creating the game)
    FOR_ALL, FOR_NONE = xrange(0, 2)
    # Values for self.join_mode (who can join the game - NONE means solo game)
    ALL, INVITED, NONE = xrange(0, 3)
    # Values for ready_mode (how to turn a MUC user into a player)
    ASK, FORCE = xrange(0, 2)

    MESSAGE = "/message"
    REQUEST = '%s/%s[@xmlns="%s"]'

    def __init__(self, host):
        """For other plugin to dynamically inherit this class, it is necessary to not use __init__ but _init_.
        The subclass itself must be initialized this way:

        class MyGame(object):

            def inheritFromRoomGame(self, host):
                global RoomGame
                RoomGame = host.plugins["ROOM-GAME"].__class__
                self.__class__ = type(self.__class__.__name__, (self.__class__, RoomGame, object), {})

            def __init__(self, host):
                self.inheritFromRoomGame(host)
                RoomGame._init_(self, host, ...)

        """
        self.host = host

    def _init_(self, host, plugin_info, ns_tag, game_init=None, player_init=None):
        """
        @param host
        @param plugin_info: PLUGIN_INFO map of the game plugin
        @param ns_tag: couple (nameservice, tag) to construct the messages
        @param game_init: dictionary for general game initialization
        @param player_init: dictionary for player initialization, applicable to each player
        """
        self.host = host
        self.name = plugin_info["import_name"]
        self.ns_tag = ns_tag
        self.request = self.REQUEST % (self.MESSAGE, ns_tag[1], ns_tag[0])
        if game_init is None:
            game_init = {}
        if player_init is None:
            player_init = {}
        self.game_init = game_init
        self.player_init = player_init
        self.games = {}
        self.invitations = {}  # values are a couple (x, y) with x the time and y a list of users

        # These are the default settings, which can be overwritten by child class after initialization
        self.invite_mode = self.FROM_PLAYERS if self.player_init == {} else self.FROM_NONE
        self.wait_mode = self.FOR_NONE if self.player_init == {} else self.FOR_ALL
        self.join_mode = self.INVITED
        self.ready_mode = self.FORCE  # TODO: asking for confirmation is not implemented

        # this has been added for testing purpose. It is sometimes needed to remove a dependence
        # while building the synchronization data, for example to replace a call to time.time()
        # by an arbitrary value. If needed, this attribute would be set to True from the testcase.
        self.testing = False

        host.trigger.add("MUC user joined", self.userJoinedTrigger)
        host.trigger.add("MUC user left", self.userLeftTrigger)

    def _createOrInvite(self, room_jid, other_players, profile):
        """
        This is called only when someone explicitly wants to play.

        The game will not be created if one already exists in the room,
        also its creation could be postponed until all the expected players
        join the room (in that case it will be created from userJoinedTrigger).
        @param room (wokkel.muc.Room): the room
        @param other_players (list[jid.JID]): list of the other players JID (bare)
        """
        # FIXME: broken !
        raise NotImplementedError("To be fixed")
        client = self.host.getClient(profile)
        user_jid = self.host.getJidNStream(profile)[0]
        nick = self.host.plugins["XEP-0045"].getRoomNick(client, room_jid)
        nicks = [nick]
        if self._gameExists(room_jid):
            if not self._checkJoinAuth(room_jid, user_jid, nick):
                return
            nicks.extend(self._invitePlayers(room_jid, other_players, nick, profile))
            self._updatePlayers(room_jid, nicks, True, profile)
        else:
            self._initGame(room_jid, nick)
            (auth, waiting, missing) = self._checkWaitAuth(room_jid, other_players)
            nicks.extend(waiting)
            nicks.extend(self._invitePlayers(room_jid, missing, nick, profile))
            if auth:
                self.createGame(room_jid, nicks, profile)
            else:
                self._updatePlayers(room_jid, nicks, False, profile)

    def _initGame(self, room_jid, referee_nick):
        """

        @param room_jid (jid.JID): JID of the room
        @param referee_nick (unicode): nickname of the referee
        """
        # Important: do not add the referee to 'players' yet. For a
        # <players /> message to be emitted whenever a new player is joining,
        # it is necessary to not modify 'players' outside of _updatePlayers.
        referee_jid = jid.JID(room_jid.userhost() + "/" + referee_nick)
        self.games[room_jid] = {
            "referee": referee_jid,
            "players": [],
            "started": False,
            "status": {},
        }
        self.games[room_jid].update(copy.deepcopy(self.game_init))
        self.invitations.setdefault(room_jid, [])

    def _gameExists(self, room_jid, started=False):
        """Return True if a game has been initialized/started.
        @param started: if False, the game must be initialized to return True,
        otherwise it must be initialized and started with createGame.
        @return: True if a game is initialized/started in that room"""
        return room_jid in self.games and (not started or self.games[room_jid]["started"])

    def _checkJoinAuth(self, room_jid, user_jid=None, nick="", verbose=False):
        """Checks if this profile is allowed to join the game.

        The parameter nick is used to check if the user is already
        a player in that game. When this method is called from
        userJoinedTrigger, nick is also used to check the user
        identity instead of user_jid_s (see TODO comment below).
        @param room_jid (jid.JID): the JID of the room hosting the game
        @param user_jid (jid.JID): JID of the user
        @param nick (unicode): nick of the user
        @return: True if this profile can join the game
        """
        auth = False
        if not self._gameExists(room_jid):
            auth = False
        elif self.join_mode == self.ALL or self.isPlayer(room_jid, nick):
            auth = True
        elif self.join_mode == self.INVITED:
            # considering all the batches of invitations
            for invitations in self.invitations[room_jid]:
                if user_jid is not None:
                    if user_jid.userhostJID() in invitations[1]:
                        auth = True
                        break
                else:
                    # TODO: that's not secure enough but what to do if
                    # wokkel.muc.User's 'entity' attribute is not set?!
                    if nick in [invited.user for invited in invitations[1]]:
                        auth = True
                        break

        if not auth and (verbose or _DEBUG):
            log.debug(
                _(u"%(user)s not allowed to join the game %(game)s in %(room)s")
                % {
                    "user": user_jid.userhost() or nick,
                    "game": self.name,
                    "room": room_jid.userhost(),
                }
            )
        return auth

    def _updatePlayers(self, room_jid, nicks, sync, profile):
        """Update the list of players and signal to the room that some players joined the game.
        If sync is True, the news players are synchronized with the game data they have missed.
        Remark: self.games[room_jid]['players'] should not be modified outside this method.
        @param room_jid (jid.JID): JID of the room
        @param nicks (list[unicode]): list of players nicks in the room (referee included, in first position)
        @param sync (bool): set to True to send synchronization data to the new players
        @param profile (unicode): %(doc_profile)s
        """
        if nicks == []:
            return
        # this is better than set(nicks).difference(...) as it keeps the order
        new_nicks = [
            nick for nick in nicks if nick not in self.games[room_jid]["players"]
        ]
        if len(new_nicks) == 0:
            return

        def setStatus(status):
            for nick in new_nicks:
                self.games[room_jid]["status"][nick] = status

        sync = (
            sync
            and self._gameExists(room_jid, True)
            and len(self.games[room_jid]["players"]) > 0
        )
        setStatus("desync" if sync else "init")
        self.games[room_jid]["players"].extend(new_nicks)
        self._synchronizeRoom(room_jid, [room_jid], profile)
        if sync:
            setStatus("init")

    def _synchronizeRoom(self, room_jid, recipients, profile):
        """Communicate the list of players to the whole room or only to some users,
        also send the synchronization data to the players who recently joined the game.
        @param room_jid (jid.JID): JID of the room
        @recipients (list[jid.JID]): list of JIDs, the recipients of the message could be:
            - room JID
            - room JID + "/" + user nick
        @param profile (unicode): %(doc_profile)s
        """
        if self._gameExists(room_jid, started=True):
            element = self._createStartElement(self.games[room_jid]["players"])
        else:
            element = self._createStartElement(
                self.games[room_jid]["players"], name="players"
            )
        elements = [(element, None, None)]

        sync_args = []
        sync_data = self._getSyncData(room_jid)
        for nick in sync_data:
            user_jid = jid.JID(room_jid.userhost() + "/" + nick)
            if user_jid in recipients:
                user_elements = copy.deepcopy(elements)
                for child in sync_data[nick]:
                    user_elements.append((child, None, None))
                recipients.remove(user_jid)
            else:
                user_elements = [(child, None, None) for child in sync_data[nick]]
            sync_args.append(([user_jid, user_elements], {"profile": profile}))

        for recipient in recipients:
            self._sendElements(recipient, elements, profile=profile)
        for args, kwargs in sync_args:
            self._sendElements(*args, **kwargs)

    def _getSyncData(self, room_jid, force_nicks=None):
        """The synchronization data are returned for each player who
        has the state 'desync' or if he's been contained by force_nicks.
        @param room_jid (jid.JID): JID of the room
        @param force_nicks: force the synchronization for this list of the nicks
        @return: a mapping between player nicks and a list of elements to
        be sent by self._synchronizeRoom for the game to be synchronized.
        """
        if not self._gameExists(room_jid):
            return {}
        data = {}
        status = self.games[room_jid]["status"]
        nicks = [nick for nick in status if status[nick] == "desync"]
        if force_nicks is None:
            force_nicks = []
        for nick in force_nicks:
            if nick not in nicks:
                nicks.append(nick)
        for nick in nicks:
            elements = self.getSyncDataForPlayer(room_jid, nick)
            if elements:
                data[nick] = elements
        return data

    def getSyncDataForPlayer(self, room_jid, nick):
        """This method may (and should probably) be overwritten by a child class.
        @param room_jid (jid.JID): JID of the room
        @param nick: the nick of the player to be synchronized
        @return: a list of elements to synchronize this player with the game.
        """
        return []

    def _invitePlayers(self, room_jid, other_players, nick, profile):
        """Invite players to a room, associated game may exist or not.

        @param other_players (list[jid.JID]): list of the players to invite
        @param nick (unicode): nick of the user who send the invitation
        @return: list[unicode] of room nicks for invited players who are already in the room
        """
        raise NotImplementedError("Need to be fixed !")
        # FIXME: this is broken and unsecure !
        if not self._checkInviteAuth(room_jid, nick):
            return []
        # TODO: remove invitation waiting for too long, using the time data
        self.invitations[room_jid].append(
            (time(), [player.userhostJID() for player in other_players])
        )
        nicks = []
        for player_jid in [player.userhostJID() for player in other_players]:
            # TODO: find a way to make it secure
            other_nick = self.host.plugins["XEP-0045"].getRoomEntityNick(
                room_jid, player_jid, secure=self.testing
            )
            if other_nick is None:
                self.host.plugins["XEP-0249"].invite(
                    player_jid, room_jid, {"game": self.name}, profile
                )
            else:
                nicks.append(other_nick)
        return nicks

    def _checkInviteAuth(self, room_jid, nick, verbose=False):
        """Checks if this user is allowed to invite players

        @param room_jid (jid.JID): JID of the room
        @param nick: user nick in the room
        @param verbose: display debug message
        @return: True if the user is allowed to invite other players
        """
        auth = False
        if self.invite_mode == self.FROM_ALL or not self._gameExists(room_jid):
            auth = True
        elif self.invite_mode == self.FROM_NONE:
            auth = not self._gameExists(room_jid, started=True) and self.isReferee(
                room_jid, nick
            )
        elif self.invite_mode == self.FROM_REFEREE:
            auth = self.isReferee(room_jid, nick)
        elif self.invite_mode == self.FROM_PLAYERS:
            auth = self.isPlayer(room_jid, nick)
        if not auth and (verbose or _DEBUG):
            log.debug(
                _(u"%(user)s not allowed to invite for the game %(game)s in %(room)s")
                % {"user": nick, "game": self.name, "room": room_jid.userhost()}
            )
        return auth

    def isReferee(self, room_jid, nick):
        """Checks if the player with this nick is the referee for the game in this room"
        @param room_jid (jid.JID): room JID
        @param nick: user nick in the room
        @return: True if the user is the referee of the game in this room
        """
        if not self._gameExists(room_jid):
            return False
        return (
            jid.JID(room_jid.userhost() + "/" + nick) == self.games[room_jid]["referee"]
        )

    def isPlayer(self, room_jid, nick):
        """Checks if the user with this nick is a player for the game in this room.
        @param room_jid (jid.JID): JID of the room
        @param nick: user nick in the room
        @return: True if the user is a player of the game in this room
        """
        if not self._gameExists(room_jid):
            return False
        # Important: the referee is not in the 'players' list right after
        # the game initialization, that's why we do also check with isReferee
        return nick in self.games[room_jid]["players"] or self.isReferee(room_jid, nick)

    def _checkWaitAuth(self, room, other_players, verbose=False):
        """Check if we must wait for other players before starting the game.

        @param room (wokkel.muc.Room): the room
        @param other_players (list[jid.JID]): list of the players without the referee
        @param verbose (bool): display debug message
        @return: (x, y, z) with:
            x: False if we must wait, True otherwise
            y: the nicks of the players that have been checked and confirmed
            z: the JID of the players that have not been checked or that are missing
        """
        if self.wait_mode == self.FOR_NONE or other_players == []:
            result = (True, [], other_players)
        elif len(room.roster) < len(other_players):
            # do not check the players until we may actually have them all
            result = (False, [], other_players)
        else:
            # TODO: find a way to make it secure
            (nicks, missing) = self.host.plugins["XEP-0045"].getRoomNicksOfUsers(
                room, other_players, secure=False
            )
            result = (len(nicks) == len(other_players), nicks, missing)
        if not result[0] and (verbose or _DEBUG):
            log.debug(
                _(
                    u"Still waiting for %(users)s before starting the game %(game)s in %(room)s"
                )
                % {
                    "users": result[2],
                    "game": self.name,
                    "room": room.occupantJID.userhost(),
                }
            )
        return result

    def getUniqueName(self, muc_service=None, profile_key=C.PROF_KEY_NONE):
        """Generate unique room name

        @param muc_service (jid.JID): you can leave empty to autofind the muc service
        @param profile_key (unicode): %(doc_profile_key)s
        @return: jid.JID (unique name for a new room to be created)
        """
        client = self.host.getClient(profile_key)
        # FIXME: jid.JID must be used instead of strings
        room = self.host.plugins["XEP-0045"].getUniqueName(client, muc_service)
        return jid.JID("sat_%s_%s" % (self.name.lower(), room.userhost()))

    def _prepareRoom(
        self, other_players=None, room_jid_s="", profile_key=C.PROF_KEY_NONE
    ):
        room_jid = jid.JID(room_jid_s) if room_jid_s else None
        other_players = [jid.JID(player).userhostJID() for player in other_players]
        return self.prepareRoom(other_players, room_jid, profile_key)

    def prepareRoom(self, other_players=None, room_jid=None, profile_key=C.PROF_KEY_NONE):
        """Prepare the room for a game: create it if it doesn't exist and invite players.

        @param other_players (list[JID]): list of other players JID (bare)
        @param room_jid (jid.JID): JID of the room, or None to generate a unique name
        @param profile_key (unicode): %(doc_profile_key)s
        """
        # FIXME: need to be refactored
        client = self.host.getClient(profile_key)
        log.debug(_(u"Preparing room for %s game") % self.name)
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            log.error(_("Unknown profile"))
            return defer.succeed(None)
        if other_players is None:
            other_players = []

        # Create/join the given room, or a unique generated one if no room is specified.
        if room_jid is None:
            room_jid = self.getUniqueName(profile_key=profile_key)
        else:
            self.host.plugins["XEP-0045"].checkRoomJoined(client, room_jid)
            self._createOrInvite(client, room_jid, other_players)
            return defer.succeed(None)

        user_jid = self.host.getJidNStream(profile)[0]
        d = self.host.plugins["XEP-0045"].join(room_jid, user_jid.user, {}, profile)
        return d.addCallback(
            lambda __: self._createOrInvite(client, room_jid, other_players)
        )

    def userJoinedTrigger(self, room, user, profile):
        """This trigger is used to check if the new user can take part of a game, create the game if we were waiting for him or just update the players list.

        @room: wokkel.muc.Room object. room.roster is a dict{wokkel.muc.User.nick: wokkel.muc.User}
        @user: wokkel.muc.User object. user.nick is a unicode and user.entity a JID
        @return: True to not interrupt the main process.
        """
        room_jid = room.occupantJID.userhostJID()
        profile_nick = room.occupantJID.resource
        if not self.isReferee(room_jid, profile_nick):
            return True  # profile is not the referee
        if not self._checkJoinAuth(
            room_jid, user.entity if user.entity else None, user.nick
        ):
            # user not allowed but let him know that we are playing :p
            self._synchronizeRoom(
                room_jid, [jid.JID(room_jid.userhost() + "/" + user.nick)], profile
            )
            return True
        if self.wait_mode == self.FOR_ALL:
            # considering the last batch of invitations
            batch = len(self.invitations[room_jid]) - 1
            if batch < 0:
                log.error(
                    u"Invitations from %s to play %s in %s have been lost!"
                    % (profile_nick, self.name, room_jid.userhost())
                )
                return True
            other_players = self.invitations[room_jid][batch][1]
            (auth, nicks, __) = self._checkWaitAuth(room, other_players)
            if auth:
                del self.invitations[room_jid][batch]
                nicks.insert(0, profile_nick)  # add the referee
                self.createGame(room_jid, nicks, profile_key=profile)
                return True
        # let the room know that a new player joined
        self._updatePlayers(room_jid, [user.nick], True, profile)
        return True

    def userLeftTrigger(self, room, user, profile):
        """This trigger is used to update or stop the game when a user leaves.

        @room: wokkel.muc.Room object. room.roster is a dict{wokkel.muc.User.nick: wokkel.muc.User}
        @user: wokkel.muc.User object. user.nick is a unicode and user.entity a JID
        @return: True to not interrupt the main process.
        """
        room_jid = room.occupantJID.userhostJID()
        profile_nick = room.occupantJID.resource
        if not self.isReferee(room_jid, profile_nick):
            return True  # profile is not the referee
        if self.isPlayer(room_jid, user.nick):
            try:
                self.games[room_jid]["players"].remove(user.nick)
            except ValueError:
                pass
            if len(self.games[room_jid]["players"]) == 0:
                return True
            if self.wait_mode == self.FOR_ALL:
                # allow this user to join the game again
                user_jid = user.entity.userhostJID()
                if len(self.invitations[room_jid]) == 0:
                    self.invitations[room_jid].append((time(), [user_jid]))
                else:
                    batch = 0  # add to the first batch of invitations
                    if user_jid not in self.invitations[room_jid][batch][1]:
                        self.invitations[room_jid][batch][1].append(user_jid)
        return True

    def _checkCreateGameAndInit(self, room_jid, profile):
        """Check if that profile can create the game. If the game can be created
        but is not initialized yet, this method will also do the initialization.

        @param room_jid (jid.JID): JID of the room
        @param profile
        @return: a couple (create, sync) with:
                - create: set to True to allow the game creation
                - sync: set to True to advice a game synchronization
        """
        user_nick = self.host.plugins["XEP-0045"].getRoomNick(room_jid, profile)
        if not user_nick:
            log.error(
                u"Internal error: profile %s has not joined the room %s"
                % (profile, room_jid.userhost())
            )
            return False, False
        if self._gameExists(room_jid):
            is_referee = self.isReferee(room_jid, user_nick)
            if self._gameExists(room_jid, started=True):
                log.info(
                    _(u"%(game)s game already created in room %(room)s")
                    % {"game": self.name, "room": room_jid.userhost()}
                )
                return False, is_referee
            elif not is_referee:
                log.info(
                    _(u"%(game)s game in room %(room)s can only be created by %(user)s")
                    % {"game": self.name, "room": room_jid.userhost(), "user": user_nick}
                )
                return False, False
        else:
            self._initGame(room_jid, user_nick)
        return True, False

    def _createGame(self, room_jid_s, nicks=None, profile_key=C.PROF_KEY_NONE):
        self.createGame(jid.JID(room_jid_s), nicks, profile_key)

    def createGame(self, room_jid, nicks=None, profile_key=C.PROF_KEY_NONE):
        """Create a new game.

        This can be called directly from a frontend and skips all the checks and invitation system,
        but the game must not exist and all the players must be in the room already.
        @param room_jid (jid.JID): JID of the room
        @param nicks (list[unicode]): list of players nicks in the room (referee included, in first position)
        @param profile_key (unicode): %(doc_profile_key)s
        """
        log.debug(
            _(u"Creating %(game)s game in room %(room)s")
            % {"game": self.name, "room": room_jid}
        )
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            log.error(_(u"profile %s is unknown") % profile_key)
            return
        (create, sync) = self._checkCreateGameAndInit(room_jid, profile)
        if nicks is None:
            nicks = []
        if not create:
            if sync:
                self._updatePlayers(room_jid, nicks, True, profile)
            return
        self.games[room_jid]["started"] = True
        self._updatePlayers(room_jid, nicks, False, profile)
        if self.player_init:
            # specific data to each player (score, private data)
            self.games[room_jid].setdefault("players_data", {})
            for nick in nicks:
                # The dict must be COPIED otherwise it is shared between all users
                self.games[room_jid]["players_data"][nick] = copy.deepcopy(
                    self.player_init
                )

    def _playerReady(self, player_nick, referee_jid_s, profile_key=C.PROF_KEY_NONE):
        self.playerReady(player_nick, jid.JID(referee_jid_s), profile_key)

    def playerReady(self, player_nick, referee_jid, profile_key=C.PROF_KEY_NONE):
        """Must be called when player is ready to start a new game

        @param player: the player nick in the room
        @param referee_jid (jid.JID): JID of the referee
        """
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            log.error(_(u"profile %s is unknown") % profile_key)
            return
        log.debug(u"new player ready: %s" % profile)
        # TODO: we probably need to add the game and room names in the sent message
        self.send(referee_jid, "player_ready", {"player": player_nick}, profile=profile)

    def newRound(self, room_jid, data, profile):
        """Launch a new round (reinit the user data)

        @param room_jid: room userhost
        @param data: a couple (common_data, msg_elts) with:
                    - common_data: backend initialization data for the new round
                    - msg_elts: dict to map each user to his specific initialization message
        @param profile
        """
        log.debug(_(u"new round for %s game") % self.name)
        game_data = self.games[room_jid]
        players = game_data["players"]
        players_data = game_data["players_data"]
        game_data["stage"] = "init"

        common_data, msg_elts = copy.deepcopy(data) if data is not None else (None, None)

        if isinstance(msg_elts, dict):
            for player in players:
                to_jid = jid.JID(room_jid.userhost() + "/" + player)  # FIXME: gof:
                elem = (
                    msg_elts[player]
                    if isinstance(msg_elts[player], domish.Element)
                    else None
                )
                self.send(to_jid, elem, profile=profile)
        elif isinstance(msg_elts, domish.Element):
            self.send(room_jid, msg_elts, profile=profile)
        if common_data is not None:
            for player in players:
                players_data[player].update(copy.deepcopy(common_data))

    def _createGameElt(self, to_jid):
        """Create a generic domish Element for the game messages

        @param to_jid: JID of the recipient
        @return: the created element
        """
        type_ = "normal" if to_jid.resource else "groupchat"
        elt = domish.Element((None, "message"))
        elt["to"] = to_jid.full()
        elt["type"] = type_
        elt.addElement(self.ns_tag)
        return elt

    def _createStartElement(self, players=None, name="started"):
        """Create a domish Element listing the game users

        @param players: list of the players
        @param name: element name:
                    - "started" to signal the players that the game has been started
                    - "players" to signal the list of players when the game is not started yet
        @return the create element
        """
        started_elt = domish.Element((None, name))
        if players is None:
            return started_elt
        idx = 0
        for player in players:
            player_elt = domish.Element((None, "player"))
            player_elt.addContent(player)
            player_elt["index"] = str(idx)
            idx += 1
            started_elt.addChild(player_elt)
        return started_elt

    def _sendElements(self, to_jid, data, profile=None):
        """ TODO

        @param to_jid: recipient JID
        @param data: list of (elem, attr, content) with:
                    - elem: domish.Element, unicode or a couple:
                            - domish.Element to be directly added as a child to the message
                            - unicode name or couple (uri, name) to create a new domish.Element
                              and add it as a child to the message (see domish.Element.addElement)
                    - attrs: dictionary of attributes for the new child
                    - content: unicode that is appended to the child content
        @param profile: the profile from which the message is sent
        @return: a Deferred instance
        """
        client = self.host.getClient(profile)
        msg = self._createGameElt(to_jid)
        for elem, attrs, content in data:
            if elem is not None:
                if isinstance(elem, domish.Element):
                    msg.firstChildElement().addChild(elem)
                else:
                    elem = msg.firstChildElement().addElement(elem)
                if attrs is not None:
                    elem.attributes.update(attrs)
                if content is not None:
                    elem.addContent(content)
        client.send(msg)
        return defer.succeed(None)

    def send(self, to_jid, elem=None, attrs=None, content=None, profile=None):
        """ TODO

        @param to_jid: recipient JID
        @param elem: domish.Element, unicode or a couple:
                    - domish.Element to be directly added as a child to the message
                    - unicode name or couple (uri, name) to create a new domish.Element
                      and add it as a child to the message (see domish.Element.addElement)
        @param attrs: dictionary of attributes for the new child
        @param content: unicode that is appended to the child content
        @param profile: the profile from which the message is sent
        @return: a Deferred instance
        """
        return self._sendElements(to_jid, [(elem, attrs, content)], profile)

    def getHandler(self, client):
        return RoomGameHandler(self)


class RoomGameHandler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        self.xmlstream.addObserver(
            self.plugin_parent.request,
            self.plugin_parent.room_game_cmd,
            profile=self.parent.profile,
        )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(self.plugin_parent.ns_tag[0])]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
