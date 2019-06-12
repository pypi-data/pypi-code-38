import logging

from twisted.internet import defer
from twisted.python.failure import Failure

from trosnoth.utils import netmsg
from trosnoth.network.networkDefines import validServerVersions
from trosnoth.messages import (
    ChatMsg, TaggingZoneMsg, PlayerCoinsSpentMsg, PlayerHasUpgradeMsg,
    CannotBuyUpgradeMsg,
    SetTeamNameMsg, SetGameModeMsg, ShotFiredMsg, RespawnMsg, PingMsg,
    PlayerUpdateMsg, AwardPlayerCoinMsg, ChatFromServerMsg, AddPlayerMsg,
    SetAgentPlayerMsg, UpdatePlayerStateMsg, AimPlayerAtMsg, RemovePlayerMsg,
    CannotJoinMsg, InitClientMsg, DelayUpdatedMsg, PlayerHitMsg,
    ZoneStateMsg, TickMsg, AchievementUnlockedMsg, WorldResetMsg,
    PlayerIsReadyMsg, PreferredTeamSelectedMsg, SetPreferredDurationMsg,
    SetPreferredSizeMsg, SetPlayerTeamMsg, CreateCollectableCoinMsg,
    RemoveCollectableCoinMsg, PlayerHasElephantMsg, ChangeNicknameMsg,
    SetGameSpeedMsg, FireShoxwaveMsg, GrapplingHookMsg, SetPreferredLevelMsg,
    UpgradeChangedMsg, PlayerHasTrosballMsg, TrosballPositionMsg,
    ResyncPlayerMsg, ResyncAcknowledgedMsg, WorldLoadingMsg, SetUIOptionsMsg,
    UpgradeApprovedMsg, UpdateClockStateMsg, PlayerAllDeadMsg,
    PlaySoundMsg, SetPlayerCoinsMsg, UpdateGameInfoMsg, SetWorldAbilitiesMsg,
    UpdateScoreBoardModeMsg, SetTeamScoreMsg, SetPlayerScoreMsg,
    SetTeamAbilitiesMsg, EmoteMsg, AgentDetachedMsg, ChangeHeadMsg,
)
from trosnoth.network.base import MsgClientProtocol
from trosnoth.utils.event import Event
from trosnoth.utils.unrepr import unrepr

log = logging.getLogger(__name__)

clientMsgs = netmsg.MessageCollection(
    PlayerHasElephantMsg,
    PlayerHasTrosballMsg,
    InitClientMsg,
    CannotJoinMsg,
    TaggingZoneMsg,
    PlayerCoinsSpentMsg,
    PlayerHasUpgradeMsg,
    ShotFiredMsg,
    AddPlayerMsg,
    SetPlayerTeamMsg,
    RespawnMsg,
    GrapplingHookMsg,
    UpdatePlayerStateMsg,
    AimPlayerAtMsg,
    SetTeamNameMsg,
    SetGameModeMsg,
    SetGameSpeedMsg,
    SetAgentPlayerMsg,
    AgentDetachedMsg,
    RemovePlayerMsg,
    PlayerUpdateMsg,
    ResyncPlayerMsg,
    ResyncAcknowledgedMsg,
    CannotBuyUpgradeMsg,
    UpgradeApprovedMsg,
    ChatMsg,
    ZoneStateMsg,
    AchievementUnlockedMsg,
    WorldResetMsg,
    PlayerIsReadyMsg,
    SetPreferredDurationMsg,
    PreferredTeamSelectedMsg,
    SetPreferredLevelMsg,
    SetPreferredSizeMsg,
    CreateCollectableCoinMsg,
    RemoveCollectableCoinMsg,
    ChangeNicknameMsg,
    ChangeHeadMsg,
    FireShoxwaveMsg,
    UpgradeChangedMsg,
    TrosballPositionMsg,
    AwardPlayerCoinMsg,
    SetPlayerCoinsMsg,
    ChatFromServerMsg,
    DelayUpdatedMsg,
    PlayerHitMsg,
    PlayerAllDeadMsg,
    WorldLoadingMsg,
    UpdateClockStateMsg,
    PlaySoundMsg,
    UpdateGameInfoMsg,
    UpdateScoreBoardModeMsg,
    SetTeamScoreMsg,
    SetPlayerScoreMsg,
    SetUIOptionsMsg,
    SetWorldAbilitiesMsg,
    SetTeamAbilitiesMsg,
    EmoteMsg,
    PingMsg,
    TickMsg,
)


class ConnectionFailed(Exception):
    def __init__(self, reason):
        self.reason = reason


class TrosnothClientProtocol(MsgClientProtocol):
    # In Trosnoth 1.8, the network protocol changed completely in order to
    # allow the server to send messages to specific agents and not just
    # generally broadcast everything. As a result, the greeting had to change.
    greeting = b'Trosnoth18'
    messages = clientMsgs

    def connectionMade(self):
        self.onConnectionLost = Event()

        super(TrosnothClientProtocol, self).connectionMade()
        self.validated = False
        self.settings_deferred = defer.Deferred()
        self.getSettingsCalled = False

    def getSettings(self):
        assert not self.getSettingsCalled, 'getSettings() already called'
        self.getSettingsCalled = True
        return self.settings_deferred

    def disconnect(self):
        self.transport.loseConnection()

    def gotGeneralMsg(self, msg):
        if not self.validated:
            if isinstance(msg, InitClientMsg):
                self.gotInitClientMsg(msg)
        else:
            super(TrosnothClientProtocol, self).gotGeneralMsg(msg)

    def gotInitClientMsg(self, msg):
        # Settings from the server.
        settings = unrepr(msg.settings.decode('utf-8'))

        # Check that we recognise the server version.
        svrVersion = settings.get('serverVersion', 'server.v1.0.0+')
        if svrVersion not in validServerVersions:
            log.info('Client: bad server version %s', svrVersion)
            self.settings_deferred.errback(Failure(
                ConnectionFailed('Incompatible server version.')))
            self.transport.abortConnection()
            return

        # Tell the client that the connection has been made.
        self.validated = True
        self.settings_deferred.callback(settings)

    def receiveBadString(self, string):
        if not self.validated:
            self.settings_deferred.errback(Failure(ConnectionFailed(
                'Remote host sent unexpected message: %r' % (string,))))
            self.transport.abortConnection()
            return

        log.warning('Client: Unknown message: %r', string,)
        log.warning('      : Did you invent a new network message and forget')
        log.warning('      : to add it to trosnoth.network.client.clientMsgs?')

    def connectionLost(self, reason=None):
        if not self.settings_deferred.called:
            self.settings_deferred.errback(Failure(
                ConnectionFailed('Remote server dropped connection.')))
            return
        super(TrosnothClientProtocol, self).connectionLost(reason)
        self.onConnectionLost()
