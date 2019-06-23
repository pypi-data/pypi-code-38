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

""" Helpers class for plugin dependencies """

from twisted.internet import defer

from wokkel.muc import Room, User
from wokkel.generic import parseXml
from wokkel.disco import DiscoItem, DiscoItems

# temporary until the changes are integrated to Wokkel
from sat_tmp.wokkel.rsm import RSMResponse

from constants import Const as C
from sat.plugins import plugin_xep_0045
from collections import OrderedDict


class FakeMUCClient(object):
    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host
        self.joined_rooms = {}

    def join(self, room_jid, nick, options=None, profile_key=C.PROF_KEY_NONE):
        """
        @param room_jid: the room JID
        @param nick: nick to be used in the room
        @param options: joining options
        @param profile_key: the profile key of the user joining the room
        @return: the deferred joined wokkel.muc.Room instance
        """
        profile = self.host.memory.getProfileName(profile_key)
        roster = {}

        # ask the other profiles to fill our roster
        for i in xrange(0, len(C.PROFILE)):
            other_profile = C.PROFILE[i]
            if other_profile == profile:
                continue
            try:
                other_room = self.plugin_parent.clients[other_profile].joined_rooms[
                    room_jid
                ]
                roster.setdefault(
                    other_room.nick, User(other_room.nick, C.PROFILE_DICT[other_profile])
                )
                for other_nick in other_room.roster:
                    roster.setdefault(other_nick, other_room.roster[other_nick])
            except (AttributeError, KeyError):
                pass

        # rename our nick if it already exists
        while nick in roster.keys():
            if C.PROFILE_DICT[profile].userhost() == roster[nick].entity.userhost():
                break  # same user with different resource --> same nickname
            nick = nick + "_"

        room = Room(room_jid, nick)
        room.roster = roster
        self.joined_rooms[room_jid] = room

        # fill the other rosters with the new entry
        for i in xrange(0, len(C.PROFILE)):
            other_profile = C.PROFILE[i]
            if other_profile == profile:
                continue
            try:
                other_room = self.plugin_parent.clients[other_profile].joined_rooms[
                    room_jid
                ]
                other_room.roster.setdefault(
                    room.nick, User(room.nick, C.PROFILE_DICT[profile])
                )
            except (AttributeError, KeyError):
                pass

        return defer.succeed(room)

    def leave(self, roomJID, profile_key=C.PROF_KEY_NONE):
        """
        @param roomJID: the room JID
        @param profile_key: the profile key of the user joining the room
        @return: a dummy deferred
        """
        profile = self.host.memory.getProfileName(profile_key)
        room = self.joined_rooms[roomJID]
        # remove ourself from the other rosters
        for i in xrange(0, len(C.PROFILE)):
            other_profile = C.PROFILE[i]
            if other_profile == profile:
                continue
            try:
                other_room = self.plugin_parent.clients[other_profile].joined_rooms[
                    roomJID
                ]
                del other_room.roster[room.nick]
            except (AttributeError, KeyError):
                pass
        del self.joined_rooms[roomJID]
        return defer.Deferred()


class FakeXEP_0045(plugin_xep_0045.XEP_0045):
    def __init__(self, host):
        self.host = host
        self.clients = {}
        for profile in C.PROFILE:
            self.clients[profile] = FakeMUCClient(self)

    def join(self, room_jid, nick, options={}, profile_key="@DEFAULT@"):
        """
        @param roomJID: the room JID
        @param nick: nick to be used in the room
        @param options: ignore
        @param profile_key: the profile of the user joining the room
        @return: the deferred joined wokkel.muc.Room instance or None
        """
        profile = self.host.memory.getProfileName(profile_key)
        if room_jid in self.clients[profile].joined_rooms:
            return defer.succeed(None)
        room = self.clients[profile].join(room_jid, nick, profile_key=profile)
        return room

    def joinRoom(self, muc_index, user_index):
        """Called by tests
        @return: the nickname of the user who joined room"""
        muc_jid = C.MUC[muc_index]
        nick = C.JID[user_index].user
        profile = C.PROFILE[user_index]
        self.join(muc_jid, nick, profile_key=profile)
        return self.getNick(muc_index, user_index)

    def leave(self, room_jid, profile_key="@DEFAULT@"):
        """
        @param roomJID: the room JID
        @param profile_key: the profile of the user leaving the room
        @return: a dummy deferred
        """
        profile = self.host.memory.getProfileName(profile_key)
        if room_jid not in self.clients[profile].joined_rooms:
            raise plugin_xep_0045.UnknownRoom("This room has not been joined")
        return self.clients[profile].leave(room_jid, profile)

    def leaveRoom(self, muc_index, user_index):
        """Called by tests
        @return: the nickname of the user who left the room"""
        muc_jid = C.MUC[muc_index]
        nick = self.getNick(muc_index, user_index)
        profile = C.PROFILE[user_index]
        self.leave(muc_jid, profile_key=profile)
        return nick

    def getRoom(self, muc_index, user_index):
        """Called by tests
        @return: a wokkel.muc.Room instance"""
        profile = C.PROFILE[user_index]
        muc_jid = C.MUC[muc_index]
        try:
            return self.clients[profile].joined_rooms[muc_jid]
        except (AttributeError, KeyError):
            return None

    def getNick(self, muc_index, user_index):
        try:
            return self.getRoomNick(C.MUC[muc_index], C.PROFILE[user_index])
        except (KeyError, AttributeError):
            return ""

    def getNickOfUser(self, muc_index, user_index, profile_index, secure=True):
        try:
            room = self.clients[C.PROFILE[profile_index]].joined_rooms[C.MUC[muc_index]]
            return self.getRoomNickOfUser(room, C.JID[user_index])
        except (KeyError, AttributeError):
            return None


class FakeXEP_0249(object):
    def __init__(self, host):
        self.host = host

    def invite(self, target, room, options={}, profile_key="@DEFAULT@"):
        """
        Invite a user to a room. To accept the invitation from a test,
        just call FakeXEP_0045.joinRoom (no need to have a dedicated method).
        @param target: jid of the user to invite
        @param room: jid of the room where the user is invited
        @options: attribute with extra info (reason, password) as in #XEP-0249
        @profile_key: %(doc_profile_key)s
        """
        pass


class FakeSatPubSubClient(object):
    def __init__(self, host, parent_plugin):
        self.host = host
        self.parent_plugin = parent_plugin
        self.__items = OrderedDict()
        self.__rsm_responses = {}

    def createNode(self, service, nodeIdentifier=None, options=None, sender=None):
        return defer.succeed(None)

    def deleteNode(self, service, nodeIdentifier, sender=None):
        try:
            del self.__items[nodeIdentifier]
        except KeyError:
            pass
        return defer.succeed(None)

    def subscribe(self, service, nodeIdentifier, subscriber, options=None, sender=None):
        return defer.succeed(None)

    def unsubscribe(
        self,
        service,
        nodeIdentifier,
        subscriber,
        subscriptionIdentifier=None,
        sender=None,
    ):
        return defer.succeed(None)

    def publish(self, service, nodeIdentifier, items=None, sender=None):
        node = self.__items.setdefault(nodeIdentifier, [])

        def replace(item_obj):
            index = 0
            for current in node:
                if current["id"] == item_obj["id"]:
                    node[index] = item_obj
                    return True
                index += 1
            return False

        for item in items:
            item_obj = parseXml(item) if isinstance(item, unicode) else item
            if not replace(item_obj):
                node.append(item_obj)
        return defer.succeed(None)

    def items(
        self,
        service,
        nodeIdentifier,
        maxItems=None,
        itemIdentifiers=None,
        subscriptionIdentifier=None,
        sender=None,
        ext_data=None,
    ):
        try:
            items = self.__items[nodeIdentifier]
        except KeyError:
            items = []
        if ext_data:
            assert "id" in ext_data
            if "rsm" in ext_data:
                args = (0, items[0]["id"], items[-1]["id"]) if items else ()
                self.__rsm_responses[ext_data["id"]] = RSMResponse(len(items), *args)
        return defer.succeed(items)

    def retractItems(self, service, nodeIdentifier, itemIdentifiers, sender=None):
        node = self.__items[nodeIdentifier]
        for item in [item for item in node if item["id"] in itemIdentifiers]:
            node.remove(item)
        return defer.succeed(None)

    def getRSMResponse(self, id):
        if id not in self.__rsm_responses:
            return {}
        result = self.__rsm_responses[id].toDict()
        del self.__rsm_responses[id]
        return result

    def subscriptions(self, service, nodeIdentifier, sender=None):
        return defer.succeed([])

    def service_getDiscoItems(self, service, nodeIdentifier, profile_key=C.PROF_KEY_NONE):
        items = DiscoItems()
        for item in self.__items.keys():
            items.append(DiscoItem(service, item))
        return defer.succeed(items)
