#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009, 2010, 2011, 2012, 2013  Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2013  Adrien Cossa (souliane@mailoo.org)

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

""" Tests for the plugin radiocol """

from sat.core import exceptions
from sat.test import helpers, helpers_plugins
from sat.plugins import plugin_misc_radiocol as plugin
from sat.plugins import plugin_misc_room_game as plugin_room_game
from constants import Const

from twisted.words.protocols.jabber.jid import JID
from twisted.words.xish import domish
from twisted.internet import reactor
from twisted.internet import defer
from twisted.python.failure import Failure
from twisted.trial.unittest import SkipTest

try:
    from mutagen.oggvorbis import OggVorbis
    from mutagen.mp3 import MP3
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3NoHeaderError
except ImportError:
    raise exceptions.MissingModule(
        u"Missing module Mutagen, please download/install from https://bitbucket.org/lazka/mutagen"
    )

import uuid
import os
import copy
import shutil


ROOM_JID = JID(Const.MUC_STR[0])
PROFILE = Const.PROFILE[0]
REFEREE_FULL = JID(ROOM_JID.userhost() + "/" + Const.JID[0].user)
PLAYERS_INDICES = [0, 1, 3]  # referee included
OTHER_PROFILES = [Const.PROFILE[1], Const.PROFILE[3]]
OTHER_PLAYERS = [Const.JID[1], Const.JID[3]]


class RadiocolTest(helpers.SatTestCase):
    def setUp(self):
        self.host = helpers.FakeSAT()

    def reinit(self):
        self.host.reinit()
        self.host.plugins["ROOM-GAME"] = plugin_room_game.RoomGame(self.host)
        self.plugin = plugin.Radiocol(self.host)  # must be init after ROOM-GAME
        self.plugin.testing = True
        self.plugin_0045 = self.host.plugins["XEP-0045"] = helpers_plugins.FakeXEP_0045(
            self.host
        )
        self.plugin_0249 = self.host.plugins["XEP-0249"] = helpers_plugins.FakeXEP_0249(
            self.host
        )
        for profile in Const.PROFILE:
            self.host.getClient(profile)  # init self.host.profiles[profile]
        self.songs = []
        self.playlist = []
        self.sound_dir = self.host.memory.getConfig("", "media_dir") + "/test/sound/"
        try:
            for filename in os.listdir(self.sound_dir):
                if filename.endswith(".ogg") or filename.endswith(".mp3"):
                    self.songs.append(filename)
        except OSError:
            raise SkipTest("The sound samples in sat_media/test/sound were not found")

    def _buildPlayers(self, players=[]):
        """@return: the "started" content built with the given players"""
        content = "<started"
        if not players:
            content += "/>"
        else:
            content += ">"
            for i in xrange(0, len(players)):
                content += "<player index='%s'>%s</player>" % (i, players[i])
            content += "</started>"
        return content

    def _expectedMessage(self, to_jid, type_, content):
        """
        @param to_jid: recipient full jid
        @param type_: message type ('normal' or 'groupchat')
        @param content: content as unicode or list of domish elements
        @return: the message XML built from the given recipient, message type and content
        """
        if isinstance(content, list):
            new_content = copy.deepcopy(content)
            for element in new_content:
                if not element.hasAttribute("xmlns"):
                    element["xmlns"] = ""
            content = "".join([element.toXml() for element in new_content])
        return "<message to='%s' type='%s'><%s xmlns='%s'>%s</%s></message>" % (
            to_jid.full(),
            type_,
            plugin.RADIOC_TAG,
            plugin.NC_RADIOCOL,
            content,
            plugin.RADIOC_TAG,
        )

    def _rejectSongCb(self, profile_index):
        """Check if the message "song_rejected" has been sent by the referee
        and process the command with the profile of the uploader
        @param profile_index: uploader's profile"""
        sent = self.host.getSentMessage(0)
        content = "<song_rejected xmlns='' reason='Too many songs in queue'/>"
        self.assertEqualXML(
            sent.toXml(),
            self._expectedMessage(
                JID(
                    ROOM_JID.userhost()
                    + "/"
                    + self.plugin_0045.getNick(0, profile_index),
                    "normal",
                    content,
                )
            ),
        )
        self._roomGameCmd(
            sent, ["radiocolSongRejected", ROOM_JID.full(), "Too many songs in queue"]
        )

    def _noUploadCb(self):
        """Check if the message "no_upload" has been sent by the referee
        and process the command with the profiles of each room users"""
        sent = self.host.getSentMessage(0)
        content = "<no_upload xmlns=''/>"
        self.assertEqualXML(
            sent.toXml(), self._expectedMessage(ROOM_JID, "groupchat", content)
        )
        self._roomGameCmd(sent, ["radiocolNoUpload", ROOM_JID.full()])

    def _uploadOkCb(self):
        """Check if the message "upload_ok" has been sent by the referee
        and process the command with the profiles of each room users"""
        sent = self.host.getSentMessage(0)
        content = "<upload_ok xmlns=''/>"
        self.assertEqualXML(
            sent.toXml(), self._expectedMessage(ROOM_JID, "groupchat", content)
        )
        self._roomGameCmd(sent, ["radiocolUploadOk", ROOM_JID.full()])

    def _preloadCb(self, attrs, profile_index):
        """Check if the message "preload" has been sent by the referee
        and process the command with the profiles of each room users
        @param attrs: information dict about the song
        @param profile_index: profile index of the uploader
        """
        sent = self.host.getSentMessage(0)
        attrs["sender"] = self.plugin_0045.getNick(0, profile_index)
        radiocol_elt = domish.generateElementsNamed(sent.elements(), "radiocol").next()
        preload_elt = domish.generateElementsNamed(
            radiocol_elt.elements(), "preload"
        ).next()
        attrs["timestamp"] = preload_elt["timestamp"]  # we could not guess it...
        content = "<preload xmlns='' %s/>" % " ".join(
            ["%s='%s'" % (attr, attrs[attr]) for attr in attrs]
        )
        if sent.hasAttribute("from"):
            del sent["from"]
        self.assertEqualXML(
            sent.toXml(), self._expectedMessage(ROOM_JID, "groupchat", content)
        )
        self._roomGameCmd(
            sent,
            [
                "radiocolPreload",
                ROOM_JID.full(),
                attrs["timestamp"],
                attrs["filename"],
                attrs["title"],
                attrs["artist"],
                attrs["album"],
                attrs["sender"],
            ],
        )

    def _playNextSongCb(self):
        """Check if the message "play" has been sent by the referee
        and process the command with the profiles of each room users"""
        sent = self.host.getSentMessage(0)
        filename = self.playlist.pop(0)
        content = "<play xmlns='' filename='%s' />" % filename
        self.assertEqualXML(
            sent.toXml(), self._expectedMessage(ROOM_JID, "groupchat", content)
        )
        self._roomGameCmd(sent, ["radiocolPlay", ROOM_JID.full(), filename])

        game_data = self.plugin.games[ROOM_JID]
        if len(game_data["queue"]) == plugin.QUEUE_LIMIT - 1:
            self._uploadOkCb()

    def _addSongCb(self, d, filepath, profile_index):
        """Check if the message "song_added" has been sent by the uploader
        and process the command with the profile of the referee
        @param d: deferred value or failure got from self.plugin.radiocolSongAdded
        @param filepath: full path to the sound file
        @param profile_index: the profile index of the uploader
        """
        if isinstance(d, Failure):
            self.fail("OGG or MP3 song could not be added!")

        game_data = self.plugin.games[ROOM_JID]

        # this is copied from the plugin
        if filepath.lower().endswith(".mp3"):
            actual_song = MP3(filepath)
            try:
                song = EasyID3(filepath)

                class Info(object):
                    def __init__(self, length):
                        self.length = length

                song.info = Info(actual_song.info.length)
            except ID3NoHeaderError:
                song = actual_song
        else:
            song = OggVorbis(filepath)

        attrs = {
            "filename": os.path.basename(filepath),
            "title": song.get("title", ["Unknown"])[0],
            "artist": song.get("artist", ["Unknown"])[0],
            "album": song.get("album", ["Unknown"])[0],
            "length": str(song.info.length),
        }
        self.assertEqual(game_data["to_delete"][attrs["filename"]], filepath)

        content = "<song_added xmlns='' %s/>" % " ".join(
            ["%s='%s'" % (attr, attrs[attr]) for attr in attrs]
        )
        sent = self.host.getSentMessage(profile_index)
        self.assertEqualXML(
            sent.toXml(), self._expectedMessage(REFEREE_FULL, "normal", content)
        )

        reject_song = len(game_data["queue"]) >= plugin.QUEUE_LIMIT
        no_upload = len(game_data["queue"]) + 1 >= plugin.QUEUE_LIMIT
        play_next = (
            not game_data["playing"]
            and len(game_data["queue"]) + 1 == plugin.QUEUE_TO_START
        )

        self._roomGameCmd(sent, profile_index)  # queue unchanged or +1
        if reject_song:
            self._rejectSongCb(profile_index)
            return
        if no_upload:
            self._noUploadCb()
        self._preloadCb(attrs, profile_index)
        self.playlist.append(attrs["filename"])
        if play_next:
            self._playNextSongCb()  # queue -1

    def _roomGameCmd(self, sent, from_index=0, call=[]):
        """Process a command. It is also possible to call this method as
        _roomGameCmd(sent, call) instead of _roomGameCmd(sent, from_index, call).
        If from index is a list, it is assumed that it is containing the value
        for call and from_index will take its default value.
        @param sent: the sent message that we need to process
        @param from_index: index of the message sender
        @param call: list containing the name of the expected bridge call
        followed by its arguments, or empty list if no call is expected
        """
        if isinstance(from_index, list):
            call = from_index
            from_index = 0

        sent["from"] = ROOM_JID.full() + "/" + self.plugin_0045.getNick(0, from_index)
        recipient = JID(sent["to"]).resource

        # The message could have been sent to a room user (room_jid + '/' + nick),
        # but when it is received, the 'to' attribute of the message has been
        # changed to the recipient own JID. We need to simulate that here.
        if recipient:
            room = self.plugin_0045.getRoom(0, 0)
            sent["to"] = (
                Const.JID_STR[0]
                if recipient == room.nick
                else room.roster[recipient].entity.full()
            )

        for index in xrange(0, len(Const.PROFILE)):
            nick = self.plugin_0045.getNick(0, index)
            if nick:
                if not recipient or nick == recipient:
                    if call and (
                        self.plugin.isPlayer(ROOM_JID, nick)
                        or call[0] == "radiocolStarted"
                    ):
                        args = copy.deepcopy(call)
                        args.append(Const.PROFILE[index])
                        self.host.bridge.expectCall(*args)
                    self.plugin.room_game_cmd(sent, Const.PROFILE[index])

    def _syncCb(self, sync_data, profile_index):
        """Synchronize one player when he joins a running game.
        @param sync_data: result from self.plugin.getSyncData
        @param profile_index: index of the profile to be synchronized
        """
        for nick in sync_data:
            expected = self._expectedMessage(
                JID(ROOM_JID.userhost() + "/" + nick), "normal", sync_data[nick]
            )
            sent = self.host.getSentMessage(0)
            self.assertEqualXML(sent.toXml(), expected)
            for elt in sync_data[nick]:
                if elt.name == "preload":
                    self.host.bridge.expectCall(
                        "radiocolPreload",
                        ROOM_JID.full(),
                        elt["timestamp"],
                        elt["filename"],
                        elt["title"],
                        elt["artist"],
                        elt["album"],
                        elt["sender"],
                        Const.PROFILE[profile_index],
                    )
                elif elt.name == "play":
                    self.host.bridge.expectCall(
                        "radiocolPlay",
                        ROOM_JID.full(),
                        elt["filename"],
                        Const.PROFILE[profile_index],
                    )
                elif elt.name == "no_upload":
                    self.host.bridge.expectCall(
                        "radiocolNoUpload", ROOM_JID.full(), Const.PROFILE[profile_index]
                    )
            sync_data[nick]
            self._roomGameCmd(sent, [])

    def _joinRoom(self, room, nicks, player_index, sync=True):
        """Make a player join a room and update the list of nicks
        @param room: wokkel.muc.Room instance from the referee perspective
        @param nicks: list of the players which will be updated
        @param player_index: profile index of the new player
        @param sync: set to True to synchronize data
        """
        user_nick = self.plugin_0045.joinRoom(0, player_index)
        self.plugin.userJoinedTrigger(room, room.roster[user_nick], PROFILE)
        if player_index not in PLAYERS_INDICES:
            # this user is actually not a player
            self.assertFalse(self.plugin.isPlayer(ROOM_JID, user_nick))
            to_jid, type_ = (JID(ROOM_JID.userhost() + "/" + user_nick), "normal")
        else:
            # this user is a player
            self.assertTrue(self.plugin.isPlayer(ROOM_JID, user_nick))
            nicks.append(user_nick)
            to_jid, type_ = (ROOM_JID, "groupchat")

        # Check that the message "players" has been sent by the referee
        expected = self._expectedMessage(to_jid, type_, self._buildPlayers(nicks))
        sent = self.host.getSentMessage(0)
        self.assertEqualXML(sent.toXml(), expected)

        # Process the command with the profiles of each room users
        self._roomGameCmd(
            sent,
            [
                "radiocolStarted",
                ROOM_JID.full(),
                REFEREE_FULL.full(),
                nicks,
                [plugin.QUEUE_TO_START, plugin.QUEUE_LIMIT],
            ],
        )

        if sync:
            self._syncCb(self.plugin._getSyncData(ROOM_JID, [user_nick]), player_index)

    def _leaveRoom(self, room, nicks, player_index):
        """Make a player leave a room and update the list of nicks
        @param room: wokkel.muc.Room instance from the referee perspective
        @param nicks: list of the players which will be updated
        @param player_index: profile index of the new player
        """
        user_nick = self.plugin_0045.getNick(0, player_index)
        user = room.roster[user_nick]
        self.plugin_0045.leaveRoom(0, player_index)
        self.plugin.userLeftTrigger(room, user, PROFILE)
        nicks.remove(user_nick)

    def _uploadSong(self, song_index, profile_index):
        """Upload the song of index song_index (modulo self.songs size) from the profile of index profile_index.

        @param song_index: index of the song or None to test with non existing file
        @param profile_index: index of the uploader's profile
        """
        if song_index is None:
            dst_filepath = unicode(uuid.uuid1())
            expect_io_error = True
        else:
            song_index = song_index % len(self.songs)
            src_filename = self.songs[song_index]
            dst_filepath = "/tmp/%s%s" % (uuid.uuid1(), os.path.splitext(src_filename)[1])
            shutil.copy(self.sound_dir + src_filename, dst_filepath)
            expect_io_error = False

        try:
            d = self.plugin.radiocolSongAdded(
                REFEREE_FULL, dst_filepath, Const.PROFILE[profile_index]
            )
        except IOError:
            self.assertTrue(expect_io_error)
            return

        self.assertFalse(expect_io_error)
        cb = lambda defer: self._addSongCb(defer, dst_filepath, profile_index)

        def eb(failure):
            if not isinstance(failure, Failure):
                self.fail("Adding a song which is not OGG nor MP3 should fail!")
            self.assertEqual(failure.value.__class__, exceptions.DataError)

        if src_filename.endswith(".ogg") or src_filename.endswith(".mp3"):
            d.addCallbacks(cb, cb)
        else:
            d.addCallbacks(eb, eb)

    def test_init(self):
        self.reinit()
        self.assertEqual(self.plugin.invite_mode, self.plugin.FROM_PLAYERS)
        self.assertEqual(self.plugin.wait_mode, self.plugin.FOR_NONE)
        self.assertEqual(self.plugin.join_mode, self.plugin.INVITED)
        self.assertEqual(self.plugin.ready_mode, self.plugin.FORCE)

    def test_game(self):
        self.reinit()

        # create game
        self.plugin.prepareRoom(OTHER_PLAYERS, ROOM_JID, PROFILE)
        self.assertTrue(self.plugin._gameExists(ROOM_JID, True))
        room = self.plugin_0045.getRoom(0, 0)
        nicks = [self.plugin_0045.getNick(0, 0)]

        sent = self.host.getSentMessage(0)
        self.assertEqualXML(
            sent.toXml(),
            self._expectedMessage(ROOM_JID, "groupchat", self._buildPlayers(nicks)),
        )
        self._roomGameCmd(
            sent,
            [
                "radiocolStarted",
                ROOM_JID.full(),
                REFEREE_FULL.full(),
                nicks,
                [plugin.QUEUE_TO_START, plugin.QUEUE_LIMIT],
            ],
        )

        self._joinRoom(room, nicks, 1)  # player joins
        self._joinRoom(room, nicks, 4)  # user not playing joins

        song_index = 0
        self._uploadSong(
            song_index, 0
        )  # ogg or mp3 file should exist in sat_media/test/song
        self._uploadSong(None, 0)  # non existing file

        # another songs are added by Const.JID[1] until the radio starts + 1 to fill the queue
        # when the first song starts + 1 to be rejected because the queue is full
        for song_index in xrange(1, plugin.QUEUE_TO_START + 1):
            self._uploadSong(song_index, 1)

        self.plugin.playNext(Const.MUC[0], PROFILE)  # simulate the end of the first song
        self._playNextSongCb()
        self._uploadSong(
            song_index, 1
        )  # now the song is accepted and the queue is full again

        self._joinRoom(room, nicks, 3)  # new player joins

        self.plugin.playNext(Const.MUC[0], PROFILE)  # the second song finishes
        self._playNextSongCb()
        self._uploadSong(0, 3)  # the player who recently joined re-upload the first file

        self._leaveRoom(room, nicks, 1)  # one player leaves
        self._joinRoom(room, nicks, 1)  # and join again

        self.plugin.playNext(Const.MUC[0], PROFILE)  # empty the queue
        self._playNextSongCb()
        self.plugin.playNext(Const.MUC[0], PROFILE)
        self._playNextSongCb()

        for filename in self.playlist:
            self.plugin.deleteFile("/tmp/" + filename)

        return defer.succeed(None)

    def tearDown(self, *args, **kwargs):
        """Clean the reactor"""
        helpers.SatTestCase.tearDown(self, *args, **kwargs)
        for delayed_call in reactor.getDelayedCalls():
            delayed_call.cancel()
