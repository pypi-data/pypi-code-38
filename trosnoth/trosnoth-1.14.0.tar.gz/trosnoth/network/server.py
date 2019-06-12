# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2012 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import logging

from twisted.internet import reactor
from twisted.internet.error import CannotListenError

from trosnoth.const import DEFAULT_GAME_PORT
from trosnoth.model.agenthub import LocalHub
from trosnoth.network.base import MsgServer
from trosnoth.network.networkDefines import serverVersion

from trosnoth.messages import (
    ChatMsg, InitClientMsg,
    ResyncAcknowledgedMsg, BuyUpgradeMsg, ShootMsg, GrapplingHookMsg,
    RespawnRequestMsg, JoinRequestMsg, UpdatePlayerStateMsg, AimPlayerAtMsg,
    PlayerIsReadyMsg, SetPreferredDurationMsg, SetPreferredTeamMsg,
    SetPreferredSizeMsg, RemovePlayerMsg, ChangeNicknameMsg, CheckSyncMsg,
    ThrowTrosballMsg, PlayerHasUpgradeMsg, PlayerAllDeadMsg, PingMsg,
    SetPreferredLevelMsg, EmoteRequestMsg, ChangeHeadMsg,
)
from trosnoth.utils import netmsg
from trosnoth.utils.event import Event

log = logging.getLogger(__name__)

# The set of messages that the server expects to receive.
serverMsgs = netmsg.MessageCollection(
    ShootMsg,
    UpdatePlayerStateMsg,
    AimPlayerAtMsg,
    BuyUpgradeMsg,
    GrapplingHookMsg,
    ThrowTrosballMsg,
    RespawnRequestMsg,
    JoinRequestMsg,
    ChatMsg,
    PlayerIsReadyMsg,
    SetPreferredDurationMsg,
    SetPreferredTeamMsg,
    SetPreferredSizeMsg,
    SetPreferredLevelMsg,
    RemovePlayerMsg,
    ChangeNicknameMsg,
    ChangeHeadMsg,
    PlayerHasUpgradeMsg,
    CheckSyncMsg,
    ResyncAcknowledgedMsg,
    PlayerAllDeadMsg,
    EmoteRequestMsg,
    PingMsg,
)


class TrosnothServerFactory(MsgServer):
    messages = serverMsgs

    def __init__(
            self, game, noAuth=False, agentCallback=None, *args, **kwargs):
        self.game = game
        self.noAuth = noAuth
        self.agentCallback = agentCallback

        self.connectedClients = set()

        self.onShutdown = Event()       # ()
        self.onConnectionEstablished = Event(['protocol'])
        self.onConnectionLost = Event(['protocol'])

        self.running = True
        self._alreadyShutdown = False

    def checkGreeting(self, greeting):
        return (greeting == b'Trosnoth18')

    def startListening(self, port=DEFAULT_GAME_PORT, interface=''):
        try:
            self.port = reactor.listenTCP(port, self, interface=interface)
        except CannotListenError:
            log.warning('WARNING: Could not listen on port %s', port)
            self.port = reactor.listenTCP(0, self, interface=interface)

    def getTCPPort(self):
        return self.port.getHost().port

    def stopListening(self):
        self.port.stopListening()

    def gotBadString(self, protocol, data):
        log.warning('Server: Unrecognised network data: %r' % (data,))
        log.warning('      : Did you invent a new network message and forget')
        log.warning('      : to add it to '
                    'trosnoth.network.server.serverMsgs?')

    def connectionEstablished(self, protocol):
        '''
        Called by the network manager when a new incoming connection is
        completed.
        '''
        # Remember that this connection's ready for transmission.
        self.connectedClients.add(protocol)
        hub = LocalHub(
            self.game, noAuth=self.noAuth, agentCallback=self.agentCallback)
        hub.connectNode(protocol)

        # Send the setting information.
        protocol.gotServerCommand(InitClientMsg(self._getClientSettings()))

        self.onConnectionEstablished(protocol)

    def _getClientSettings(self):
        '''Returns a byte string representing the settings which must be
        sent to clients that connect to this server.'''

        result = self.game.world.dumpEverything()
        result['serverVersion'] = serverVersion

        return repr(result).encode('utf-8')

    def connectionLost(self, protocol, reason):
        if protocol in self.connectedClients:
            protocol.hub.disconnectNode()

        self.connectedClients.remove(protocol)
        self.onConnectionLost(protocol)

    def shutdown(self):
        if self._alreadyShutdown:
            return
        self._alreadyShutdown = True

        # Kill server
        self.running = False
        self.game.stop()
        self.onShutdown.execute()
