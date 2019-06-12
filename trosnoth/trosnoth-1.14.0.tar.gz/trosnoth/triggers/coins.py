from trosnoth.const import BONUS_COINS_PER_5_SECONDS
from trosnoth.messages import AwardPlayerCoinMsg
from trosnoth.triggers.base import Trigger


class SlowlyIncrementLivePlayerCoinsTrigger(Trigger):
    '''
    Gives coins to living players at a constant slow rate.
    '''

    def __init__(self, level, factor=1, *args, **kwargs):
        super(SlowlyIncrementLivePlayerCoinsTrigger, self).__init__(
            level, *args, **kwargs)
        self.factor = factor
        self.nextCall = None

    def doActivate(self):
        self.nextCall = self.world.callLater(5, self.everyFiveSeconds)

    def doDeactivate(self):
        if self.nextCall:
            self.nextCall.cancel()
            self.nextCall = None

    def everyFiveSeconds(self):
        self.nextCall = self.world.callLater(5, self.everyFiveSeconds)

        for player in self.world.players:
            if not player.dead:
                self.world.sendServerCommand(AwardPlayerCoinMsg(
                    player.id, count=self.factor * BONUS_COINS_PER_5_SECONDS))


class AwardStartingCoinsTrigger(Trigger):
    '''
    During the time that this trigger is active, all new players to the game
    will be awarded a fixed number of starting coins. Players who are
    already in the game when the trigger is activated will also be awarded
    coins.
    '''

    def __init__(self, level, coins=200, *args, **kwargs):
        super(AwardStartingCoinsTrigger, self).__init__(level, *args, **kwargs)
        self.coins = coins

    def doActivate(self):
        for player in self.world.players:
            self.world.sendServerCommand(
                AwardPlayerCoinMsg(player.id, self.coins))

        self.world.onPlayerAdded.addListener(self.newPlayerAdded)

    def doDeactivate(self):
        self.world.onPlayerAdded.removeListener(self.newPlayerAdded)

    def newPlayerAdded(self, player):
        self.world.sendServerCommand(AwardPlayerCoinMsg(player.id, self.coins))
