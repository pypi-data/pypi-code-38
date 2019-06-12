from functools import partial

from trosnoth.const import BOT_GOAL_HUNT_RABBITS
from trosnoth.messages import SetPlayerTeamMsg
from trosnoth.messages import UpdateGameInfoMsg
from trosnoth.model.universe_base import NEUTRAL_TEAM_ID
from trosnoth.triggers.base import Trigger
from trosnoth.utils.event import Event


class GraduallyMakePlayersNeutralTrigger(Trigger):
    '''
    When this trigger is active, any player who is dead, and any new player
    who joins the game, will become neutral. Only players who have not died
    since the trigger was activated will retain their team.
    '''

    def __init__(self, *args, **kwargs):
        super(GraduallyMakePlayersNeutralTrigger, self).__init__(
            *args, **kwargs)
        self.onRabbitKilled = Event(['player'])
        self.onNoMoreRabbits = Event([])
        self.playerDeathListeners = {}

    def doActivate(self):
        for player in self.world.players:
            if player.team is None:
                continue

            if player.dead:
                self.world.sendServerCommand(
                    SetPlayerTeamMsg(player.id, NEUTRAL_TEAM_ID))
            else:
                listener = partial(self.playerDied, player)
                player.onDied.addListener(listener)
                self.playerDeathListeners[player] = listener

        self.world.onPlayerAdded.addListener(self.newPlayerAdded)
        self.world.onPlayerRemoved.addListener(self.playerRemoved)

        if not self.playerDeathListeners:
            self.onNoMoreRabbits()

    def playerDied(self, player, *args, **kwargs):
        self.world.sendServerCommand(
            SetPlayerTeamMsg(player.id, NEUTRAL_TEAM_ID))
        listener = self.playerDeathListeners.pop(player)
        player.onDied.removeListener(listener)
        self.onRabbitKilled(player)

        if not self.playerDeathListeners:
            self.onNoMoreRabbits()

    def newPlayerAdded(self, player):
        if player.team is not None:
            self.world.sendServerCommand(
                SetPlayerTeamMsg(player.id, NEUTRAL_TEAM_ID))

    def playerRemoved(self, player, oldId):
        if player in self.playerDeathListeners:
            listener = self.playerDeathListeners.pop(player)
            player.onDied.removeListener(listener)

    def doDeactivate(self):
        self.world.onPlayerAdded.removeListener(self.newPlayerAdded)
        self.world.onPlayerRemoved.removeListener(self.playerRemoved)
        for player, listener in list(self.playerDeathListeners.items()):
            player.onDied.removeListener(listener)
        self.playerDeathListeners = {}


class RabbitHuntTrigger(Trigger):
    '''
    Complex trigger, which sets all the necessary settings for a rabbit
    hunt. When the rabbit hunt is over, either due to time, or all rabbits
    being dead, this trigger deactivates itself, and fires onComplete.
    '''

    def __init__(self, *args, **kwargs):
        super(RabbitHuntTrigger, self).__init__(*args, **kwargs)
        self.onComplete = Event(['liveRabbits'])
        self.neutraliser = None

    def doActivate(self):
        self.world.finaliseStats()
        self.world.clock.startCountDown(60)
        self.world.clock.propagateToClients()
        self.world.clock.onZero.addListener(self._done)
        self.world.onChangeVoiceChatRooms([], [])
        self.world.uiOptions.set(teamIdsHumansCanJoin=[NEUTRAL_TEAM_ID])

        self.neutraliser = GraduallyMakePlayersNeutralTrigger(self.level)
        self.neutraliser.onNoMoreRabbits.addListener(self._done)
        self.neutraliser.activate()

        self._setUserInfo()
        self.neutraliser.onRabbitKilled.addListener(self._rabbitKilled)

    def _setUserInfo(self):
        title = 'Rabbit Hunt'

        # Defaults for new players and replay viewers
        self.level.setUserInfo(title, (
            '* A game recently finished',
            '* Players who survived are "rabbits"',
            '* Try to shoot all the rabbits before the time runs out',
        ), BOT_GOAL_HUNT_RABBITS)

        for player in self.world.players:
            # Customise each player's objective list
            if player.team is None:
                info = [
                    '* The game is now over',
                    '* Players who survived are "rabbits"',
                    '* Try to shoot all the rabbits before the time runs out',
                ]
            else:
                info = [
                    '* The game is now over',
                    '* Try to survive until the time runs out',
                    '* Try to kill any surviving enemy rabbits',
                    '* If you die, you will respawn as a rogue',
                ]
            player.agent.messageToAgent(
                UpdateGameInfoMsg.build(title, info, BOT_GOAL_HUNT_RABBITS))

    def _rabbitKilled(self, player):
        player.agent.messageToAgent(UpdateGameInfoMsg.build('Rabbit Hunt', [
            '* The game is now over',
            '* Players who survived are "rabbits"',
            '* Try to shoot all the rabbits before the time runs out',
        ], BOT_GOAL_HUNT_RABBITS))

    def _done(self):
        liveRabbits = list(self.neutraliser.playerDeathListeners.keys())
        self.deactivate()
        self.level.playSound('game-over-whistle.ogg')
        self.onComplete(liveRabbits)

    def doDeactivate(self):
        self.world.clock.onZero.removeListener(self._done)
        self.neutraliser.onNoMoreRabbits.removeListener(self._done)
        self.neutraliser.onRabbitKilled.removeListener(self._rabbitKilled)
        self.neutraliser.deactivate()
        self.world.clock.stop()
