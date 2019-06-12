import logging

from trosnoth.messages import PlayerHasElephantMsg
from trosnoth.triggers.base import DurationScoreTrigger, Trigger
from twisted.internet import defer

log = logging.getLogger(__name__)


class ElephantDurationScoreTrigger(DurationScoreTrigger):
    '''
    Players get points based on how long they hold the elephant for.
    '''
    def __init__(self, *args, **kwargs):
        super(ElephantDurationScoreTrigger, self).__init__(*args, **kwargs)
        self.playerWithElephant = self.world.playerWithElephant

    def doActivate(self):
        super(ElephantDurationScoreTrigger, self).doActivate()
        self.world.scoreboard.setMode(players=True)
        self.world.onPlayerKill.addListener(self.gotPlayerKill)

    def doDeactivate(self):
        self.world.onPlayerKill.removeListener(self.gotPlayerKill)
        if self.world.scoreboard:
            self.world.scoreboard.setMode(players=False)
        super(ElephantDurationScoreTrigger, self).doDeactivate()

    def gotInterval(self):
        self.playerWithElephant = self.world.playerWithElephant
        super(ElephantDurationScoreTrigger, self).gotInterval()

    def checkCondition(self, player):
        return player.hasElephant() and not player.dead

    def gotPlayerKill(self, killer, target, hitKind):
        if self.playerWithElephant == target:
            self.conditionLost(target)
            self.playerWithElephant = None


class EnsureElephantIsInGameTrigger(Trigger):
    '''
    If at any point there is no live elephant in the game, adds a bot to the
    game and gives it the elephant. As soon as the bot loses the elephant,
    it is removed from the game.
    '''
    def __init__(self, level):
        super(EnsureElephantIsInGameTrigger, self).__init__(level)
        self.bot = None
        self.addingBot = False

    def doActivate(self):
        self.world.onElephantTransfer.addListener(self.gotElephantTransfer)
        self.world.callLater(0, self.checkIfBotIsNeeded)

    def doDeactivate(self):
        self.world.onElephantTransfer.removeListener(self.gotElephantTransfer)

    def gotElephantTransfer(self, oldOwner):
        self.checkIfBotIsNeeded()

    def checkIfBotIsNeeded(self):
        if self.bot and self.bot.player.hasElephant():
            return

        if self.world.playerWithElephant is None or \
                self.world.playerWithElephant.dead:
            self.addBotWithElephant()
        else:
            self.removeBot()

    @defer.inlineCallbacks
    def addBotWithElephant(self):
        if self.addingBot:
            return
        if self.bot and self.bot.player.dead:
            self.removeBot()

        # Add a bot
        if not self.bot:
            self.addingBot = True
            try:
                nick = 'ElephantBot'
                # Pretect against tricksy humans editing their nicks
                while any(p.nick == nick for p in self.world.players):
                    nick += "'"
                self.bot = yield self.level.addBot(None, nick, 'ranger')
            finally:
                self.addingBot = False

        # Give the bot the elephant, and notice when the bot dies
        self.world.sendServerCommand(PlayerHasElephantMsg(self.bot.player.id))

    def removeBot(self):
        agent, self.bot = self.bot, None
        if agent:
            agent.stop()
            self.world.game.detachAgent(agent)
