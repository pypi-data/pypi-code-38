#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing Radiocol
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

from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.words.xish import domish
from twisted.internet import reactor
from twisted.words.protocols.jabber import jid
from twisted.internet import defer
from sat.core import exceptions
import os.path
import copy
import time
from os import unlink

try:
    from mutagen.oggvorbis import OggVorbis, OggVorbisHeaderError
    from mutagen.mp3 import MP3, HeaderNotFoundError
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3NoHeaderError
except ImportError:
    raise exceptions.MissingModule(
        u"Missing module Mutagen, please download/install from https://bitbucket.org/lazka/mutagen"
    )


NC_RADIOCOL = "http://www.goffi.org/protocol/radiocol"
RADIOC_TAG = "radiocol"

PLUGIN_INFO = {
    C.PI_NAME: "Radio collective plugin",
    C.PI_IMPORT_NAME: "Radiocol",
    C.PI_TYPE: "Exp",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0045", "XEP-0249", "ROOM-GAME"],
    C.PI_MAIN: "Radiocol",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of radio collective"""),
}


# Number of songs needed in the queue before we start playing
QUEUE_TO_START = 2
# Maximum number of songs in the queue (the song being currently played doesn't count)
QUEUE_LIMIT = 2


class Radiocol(object):
    def inheritFromRoomGame(self, host):
        global RoomGame
        RoomGame = host.plugins["ROOM-GAME"].__class__
        self.__class__ = type(
            self.__class__.__name__, (self.__class__, RoomGame, object), {}
        )

    def __init__(self, host):
        log.info(_("Radio collective initialization"))
        self.inheritFromRoomGame(host)
        RoomGame._init_(
            self,
            host,
            PLUGIN_INFO,
            (NC_RADIOCOL, RADIOC_TAG),
            game_init={
                "queue": [],
                "upload": True,
                "playing": None,
                "playing_time": 0,
                "to_delete": {},
            },
        )
        self.host = host
        host.bridge.addMethod(
            "radiocolLaunch",
            ".plugin",
            in_sign="asss",
            out_sign="",
            method=self._prepareRoom,
            async=True,
        )
        host.bridge.addMethod(
            "radiocolCreate",
            ".plugin",
            in_sign="sass",
            out_sign="",
            method=self._createGame,
        )
        host.bridge.addMethod(
            "radiocolSongAdded",
            ".plugin",
            in_sign="sss",
            out_sign="",
            method=self._radiocolSongAdded,
            async=True,
        )
        host.bridge.addSignal(
            "radiocolPlayers", ".plugin", signature="ssass"
        )  # room_jid, referee, players, profile
        host.bridge.addSignal(
            "radiocolStarted", ".plugin", signature="ssasais"
        )  # room_jid, referee, players, [QUEUE_TO_START, QUEUE_LIMIT], profile
        host.bridge.addSignal(
            "radiocolSongRejected", ".plugin", signature="sss"
        )  # room_jid, reason, profile
        host.bridge.addSignal(
            "radiocolPreload", ".plugin", signature="ssssssss"
        )  # room_jid, timestamp, filename, title, artist, album, profile
        host.bridge.addSignal(
            "radiocolPlay", ".plugin", signature="sss"
        )  # room_jid, filename, profile
        host.bridge.addSignal(
            "radiocolNoUpload", ".plugin", signature="ss"
        )  # room_jid, profile
        host.bridge.addSignal(
            "radiocolUploadOk", ".plugin", signature="ss"
        )  # room_jid, profile

    def __create_preload_elt(self, sender, song_added_elt):
        preload_elt = copy.deepcopy(song_added_elt)
        preload_elt.name = "preload"
        preload_elt["sender"] = sender
        preload_elt["timestamp"] = str(time.time())
        # attributes filename, title, artist, album, length have been copied
        # XXX: the frontend should know the temporary directory where file is put
        return preload_elt

    def _radiocolSongAdded(self, referee_s, song_path, profile):
        return self.radiocolSongAdded(jid.JID(referee_s), song_path, profile)

    def radiocolSongAdded(self, referee, song_path, profile):
        """This method is called by libervia when a song has been uploaded
        @param referee (jid.JID): JID of the referee in the room (room userhost + '/' + nick)
        @param song_path (unicode): absolute path of the song added
        @param profile_key (unicode): %(doc_profile_key)s
        @return: a Deferred instance
        """
        # XXX: this is a Q&D way for the proof of concept. In the future, the song should
        #     be streamed to the backend using XMPP file copy
        #     Here we cheat because we know we are on the same host, and we don't
        #     check data. Referee will have to parse the song himself to check it
        try:
            if song_path.lower().endswith(".mp3"):
                actual_song = MP3(song_path)
                try:
                    song = EasyID3(song_path)

                    class Info(object):
                        def __init__(self, length):
                            self.length = length

                    song.info = Info(actual_song.info.length)
                except ID3NoHeaderError:
                    song = actual_song
            else:
                song = OggVorbis(song_path)
        except (OggVorbisHeaderError, HeaderNotFoundError):
            # this file is not ogg vorbis nor mp3, we reject it
            self.deleteFile(song_path)  # FIXME: same host trick (see note above)
            return defer.fail(
                exceptions.DataError(
                    D_(
                        "The uploaded file has been rejected, only Ogg Vorbis and MP3 songs are accepted."
                    )
                )
            )

        attrs = {
            "filename": os.path.basename(song_path),
            "title": song.get("title", ["Unknown"])[0],
            "artist": song.get("artist", ["Unknown"])[0],
            "album": song.get("album", ["Unknown"])[0],
            "length": str(song.info.length),
        }
        radio_data = self.games[
            referee.userhostJID()
        ]  # FIXME: referee comes from Libervia's client side, it's unsecure
        radio_data["to_delete"][
            attrs["filename"]
        ] = (
            song_path
        )  # FIXME: works only because of the same host trick, see the note under the docstring
        return self.send(referee, ("", "song_added"), attrs, profile=profile)

    def playNext(self, room_jid, profile):
        """"Play next song in queue if exists, and put a timer
        which trigger after the song has been played to play next one"""
        # TODO: songs need to be erased once played or found invalids
        #      ==> unlink done the Q&D way with the same host trick (see above)
        radio_data = self.games[room_jid]
        if len(radio_data["players"]) == 0:
            log.debug(_(u"No more participants in the radiocol: cleaning data"))
            radio_data["queue"] = []
            for filename in radio_data["to_delete"]:
                self.deleteFile(filename, radio_data)
            radio_data["to_delete"] = {}
        queue = radio_data["queue"]
        if not queue:
            # nothing left to play, we need to wait for uploads
            radio_data["playing"] = None
            return
        song = queue.pop(0)
        filename, length = song["filename"], float(song["length"])
        self.send(room_jid, ("", "play"), {"filename": filename}, profile=profile)
        radio_data["playing"] = song
        radio_data["playing_time"] = time.time()

        if not radio_data["upload"] and len(queue) < QUEUE_LIMIT:
            # upload is blocked and we now have resources to get more, we reactivate it
            self.send(room_jid, ("", "upload_ok"), profile=profile)
            radio_data["upload"] = True

        reactor.callLater(length, self.playNext, room_jid, profile)
        # we wait more than the song length to delete the file, to manage poorly reactive networks/clients
        reactor.callLater(
            length + 90, self.deleteFile, filename, radio_data
        )  # FIXME: same host trick (see above)

    def deleteFile(self, filename, radio_data=None):
        """
        Delete a previously uploaded file.
        @param filename: filename to delete, or full filepath if radio_data is None
        @param radio_data: current game data
        @return: True if the file has been deleted
        """
        if radio_data:
            try:
                file_to_delete = radio_data["to_delete"][filename]
            except KeyError:
                log.error(
                    _(u"INTERNAL ERROR: can't find full path of the song to delete")
                )
                return False
        else:
            file_to_delete = filename
        try:
            unlink(file_to_delete)
        except OSError:
            log.error(
                _(u"INTERNAL ERROR: can't find %s on the file system" % file_to_delete)
            )
            return False
        return True

    def room_game_cmd(self, mess_elt, profile):
        from_jid = jid.JID(mess_elt["from"])
        room_jid = from_jid.userhostJID()
        nick = self.host.plugins["XEP-0045"].getRoomNick(room_jid, profile)

        radio_elt = mess_elt.firstChildElement()
        radio_data = self.games[room_jid]
        if "queue" in radio_data:
            queue = radio_data["queue"]

        from_referee = self.isReferee(room_jid, from_jid.resource)
        to_referee = self.isReferee(room_jid, jid.JID(mess_elt["to"]).user)
        is_player = self.isPlayer(room_jid, nick)
        for elt in radio_elt.elements():
            if not from_referee and not (to_referee and elt.name == "song_added"):
                continue  # sender must be referee, expect when a song is submitted
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
                    self.host.bridge.radiocolStarted
                    if elt.name == "started"
                    else self.host.bridge.radiocolPlayers
                )
                signal(
                    room_jid.userhost(),
                    from_jid.full(),
                    players,
                    [QUEUE_TO_START, QUEUE_LIMIT],
                    profile,
                )
            elif elt.name == "preload":  # a song is in queue and must be preloaded
                self.host.bridge.radiocolPreload(
                    room_jid.userhost(),
                    elt["timestamp"],
                    elt["filename"],
                    elt["title"],
                    elt["artist"],
                    elt["album"],
                    elt["sender"],
                    profile,
                )
            elif elt.name == "play":
                self.host.bridge.radiocolPlay(
                    room_jid.userhost(), elt["filename"], profile
                )
            elif elt.name == "song_rejected":  # a song has been refused
                self.host.bridge.radiocolSongRejected(
                    room_jid.userhost(), elt["reason"], profile
                )
            elif elt.name == "no_upload":
                self.host.bridge.radiocolNoUpload(room_jid.userhost(), profile)
            elif elt.name == "upload_ok":
                self.host.bridge.radiocolUploadOk(room_jid.userhost(), profile)
            elif elt.name == "song_added":  # a song has been added
                # FIXME: we are KISS for the proof of concept: every song is added, to a limit of 3 in queue.
                #       Need to manage some sort of rules to allow peoples to send songs
                if len(queue) >= QUEUE_LIMIT:
                    # there are already too many songs in queue, we reject this one
                    # FIXME: add an error code
                    self.send(
                        from_jid,
                        ("", "song_rejected"),
                        {"reason": "Too many songs in queue"},
                        profile=profile,
                    )
                    return

                # The song is accepted and added in queue
                preload_elt = self.__create_preload_elt(from_jid.resource, elt)
                queue.append(preload_elt)

                if len(queue) >= QUEUE_LIMIT:
                    # We are at the limit, we refuse new upload until next play
                    self.send(room_jid, ("", "no_upload"), profile=profile)
                    radio_data["upload"] = False

                self.send(room_jid, preload_elt, profile=profile)
                if not radio_data["playing"] and len(queue) == QUEUE_TO_START:
                    # We have not started playing yet, and we have QUEUE_TO_START
                    # songs in queue. We can now start the party :)
                    self.playNext(room_jid, profile)
            else:
                log.error(_(u"Unmanaged game element: %s") % elt.name)

    def getSyncDataForPlayer(self, room_jid, nick):
        game_data = self.games[room_jid]
        elements = []
        if game_data["playing"]:
            preload = copy.deepcopy(game_data["playing"])
            current_time = game_data["playing_time"] + 1 if self.testing else time.time()
            preload["filename"] += "#t=%.2f" % (current_time - game_data["playing_time"])
            elements.append(preload)
            play = domish.Element(("", "play"))
            play["filename"] = preload["filename"]
            elements.append(play)
        if len(game_data["queue"]) > 0:
            elements.extend(copy.deepcopy(game_data["queue"]))
            if len(game_data["queue"]) == QUEUE_LIMIT:
                elements.append(domish.Element(("", "no_upload")))
        return elements
