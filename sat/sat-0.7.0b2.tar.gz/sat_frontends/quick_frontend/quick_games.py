#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# helper class for making a SAT frontend
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

from sat.core.log import getLogger

log = getLogger(__name__)

from sat.core.i18n import _

from sat_frontends.tools import jid
from sat_frontends.tools import games
from sat_frontends.quick_frontend.constants import Const as C

import quick_chat


class RoomGame(object):
    _game_name = None
    _signal_prefix = None
    _signal_suffixes = None

    @classmethod
    def registerSignals(cls, host):
        def make_handler(suffix, signal):
            def handler(*args):
                if suffix in ("Started", "Players"):
                    return cls.startedHandler(host, suffix, *args)
                return cls.genericHandler(host, signal, *args)

            return handler

        for suffix in cls._signal_suffixes:
            signal = cls._signal_prefix + suffix
            host.registerSignal(
                signal, handler=make_handler(suffix, signal), iface="plugin"
            )

    @classmethod
    def startedHandler(cls, host, suffix, *args):
        room_jid, args, profile = jid.JID(args[0]), args[1:-1], args[-1]
        referee, players, args = args[0], args[1], args[2:]
        chat_widget = host.widgets.getOrCreateWidget(
            quick_chat.QuickChat, room_jid, type_=C.CHAT_GROUP, profile=profile
        )

        # update symbols
        if cls._game_name not in chat_widget.visible_states:
            chat_widget.visible_states.append(cls._game_name)
        symbols = games.SYMBOLS[cls._game_name]
        index = 0
        contact_list = host.contact_lists[profile]
        for occupant in chat_widget.occupants:
            occupant_jid = jid.newResource(room_jid, occupant)
            contact_list.setCache(
                occupant_jid,
                cls._game_name,
                symbols[index % len(symbols)] if occupant in players else None,
            )
            chat_widget.update(occupant_jid)

        if suffix == "Players" or chat_widget.nick not in players:
            return  # waiting for other players to join, or not playing
        if cls._game_name in chat_widget.games:
            return  # game panel is already there
        real_class = host.widgets.getRealClass(cls)
        if real_class == cls:
            host.showDialog(
                _(
                    u"A {game} activity between {players} has been started, but you couldn't take part because your client doesn't support it."
                ).format(game=cls._game_name, players=", ".join(players)),
                _(u"{game} Game").format(game=cls._game_name),
            )
            return
        panel = real_class(chat_widget, referee, players, *args)
        chat_widget.games[cls._game_name] = panel
        chat_widget.addGamePanel(panel)

    @classmethod
    def genericHandler(cls, host, signal, *args):
        room_jid, args, profile = jid.JID(args[0]), args[1:-1], args[-1]
        chat_widget = host.widgets.getWidget(quick_chat.QuickChat, room_jid, profile)
        if chat_widget:
            try:
                game_panel = chat_widget.games[cls._game_name]
            except KeyError:
                log.error(
                    "TODO: better game synchronisation - received signal %s but no panel is found"
                    % signal
                )
                return
            else:
                getattr(game_panel, "%sHandler" % signal)(*args)


class Tarot(RoomGame):
    _game_name = "Tarot"
    _signal_prefix = "tarotGame"
    _signal_suffixes = (
        "Started",
        "Players",
        "New",
        "ChooseContrat",
        "ShowCards",
        "YourTurn",
        "Score",
        "CardsPlayed",
        "InvalidCards",
    )


class Quiz(RoomGame):
    _game_name = "Quiz"
    _signal_prefix = "quizGame"
    _signal_suffixes = (
        "Started",
        "New",
        "Question",
        "PlayerBuzzed",
        "PlayerSays",
        "AnswerResult",
        "TimerExpired",
        "TimerRestarted",
    )


class Radiocol(RoomGame):
    _game_name = "Radiocol"
    _signal_prefix = "radiocol"
    _signal_suffixes = (
        "Started",
        "Players",
        "SongRejected",
        "Preload",
        "Play",
        "NoUpload",
        "UploadOk",
    )
