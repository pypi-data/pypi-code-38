from trosnoth.const import TICK_PERIOD
from twisted.internet import defer

from trosnoth.model.map import ZoneLayout, ZoneStep
from trosnoth.triggers.base import Trigger, DurationScoreTrigger


class PlayerKillScoreTrigger(Trigger):
    '''
    When a player is killed, award leaderboard points to the killer.
    '''

    def __init__(self, level, killScore=1, dieScore=-1):
        super(PlayerKillScoreTrigger, self).__init__(level)
        self.killScore = killScore
        self.dieScore = dieScore

    def doActivate(self):
        self.world.onPlayerKill.addListener(self.gotPlayerKill)
        self.world.scoreboard.setMode(players=True)

    def doDeactivate(self):
        self.world.onPlayerKill.removeListener(self.gotPlayerKill)
        if self.world.scoreboard:
            self.world.scoreboard.setMode(players=False)

    def gotPlayerKill(self, killer, target, hitKind):
        if killer:
            self.world.scoreboard.playerScored(killer, self.killScore)
        self.world.scoreboard.playerScored(target, self.dieScore)


class PlayerLifeScoreTrigger(DurationScoreTrigger):
    '''
    Players get points based on how long they have been alive.
    '''

    def __init__(self, level, interval=1, teams=None):
        super(PlayerLifeScoreTrigger, self).__init__(level, interval)
        self.teams = teams

    def doActivate(self):
        super(PlayerLifeScoreTrigger, self).doActivate()
        self.world.scoreboard.setMode(players=True)
        self.world.onPlayerKill.addListener(self.gotPlayerKill)

    def doDeactivate(self):
        self.world.onPlayerKill.removeListener(self.gotPlayerKill)
        if self.world.scoreboard:
            self.world.scoreboard.setMode(players=False)
        super(PlayerLifeScoreTrigger, self).doDeactivate()

    def gotInterval(self):
        self.callback = self.world.callLater(self.interval, self.gotInterval)
        for p in self.world.players:
            if p in self.playerPortions:
                self.world.scoreboard.playerScored(p, self.playerPortions[p])
            elif not p.dead:
                if self.teams is None or p.team in self.teams:
                    self.world.scoreboard.playerScored(p, 1)
        self.extraTicks = 0
        self.playerPortions = {}

    def checkCondition(self, player):
        if player.dead:
            return False
        return self.isPlayerInSelectedTeams(player)

    def isPlayerInSelectedTeams(self, player):
        return self.teams is None or player.team in self.teams

    def gotPlayerKill(self, killer, target, hitKind):
        if self.isPlayerInSelectedTeams(target):
            self.conditionLost(target)


def makeCirclesLayout(layoutDatabase):
    zones = ZoneLayout()

    # Centre
    zone = zones.firstLocation
    zones.setZoneOwner(zone, 0, dark=True)

    # Inner ring
    zone = zones.firstLocation
    zones.addZoneAt(zone + ZoneStep.SOUTH, ownerIndex=1, dark=False)
    zones.addZoneAt(zone + ZoneStep.NORTHEAST, ownerIndex=1, dark=False)
    zones.addZoneAt(zone + ZoneStep.NORTHWEST, ownerIndex=1, dark=False)
    se = zones.connectZone(
        zone, ZoneStep.SOUTHEAST, ownerIndex=1, dark=False)
    zones.connectZone(se, ZoneStep.SOUTHWEST)
    zones.connectZone(se, ZoneStep.NORTH)
    sw = zones.connectZone(
        zone, ZoneStep.SOUTHWEST, ownerIndex=1, dark=False)
    zones.connectZone(sw, ZoneStep.SOUTHEAST)
    zones.connectZone(sw, ZoneStep.NORTH)
    n = zones.connectZone(zone, ZoneStep.NORTH, ownerIndex=1, dark=False)
    zones.connectZone(n, ZoneStep.SOUTHEAST)
    zones.connectZone(n, ZoneStep.SOUTHWEST)

    # Outer ring
    zone = zones.connectZone(n, ZoneStep.NORTHEAST)
    zone = zones.connectZone(zone, ZoneStep.SOUTHEAST)
    zone = zones.connectZone(zone, ZoneStep.SOUTH)
    zones.connectZone(zone, ZoneStep.NORTHWEST)
    zone = zones.connectZone(zone, ZoneStep.SOUTH)
    zone = zones.connectZone(zone, ZoneStep.SOUTHWEST)
    zones.connectZone(zone, ZoneStep.NORTH)
    zone = zones.connectZone(zone, ZoneStep.SOUTHWEST)
    zone = zones.connectZone(zone, ZoneStep.NORTHWEST)
    zones.connectZone(zone, ZoneStep.NORTHEAST)
    zone = zones.connectZone(zone, ZoneStep.NORTHWEST)
    zone = zones.connectZone(zone, ZoneStep.NORTH)
    zones.connectZone(zone, ZoneStep.SOUTHEAST)
    zone = zones.connectZone(zone, ZoneStep.NORTH)
    zone = zones.connectZone(zone, ZoneStep.NORTHEAST)
    zones.connectZone(zone, ZoneStep.SOUTH)
    zone = zones.connectZone(zone, ZoneStep.NORTHEAST)
    zone = zones.connectZone(zone, ZoneStep.SOUTHEAST)

    return zones.createMapLayout(layoutDatabase, autoOwner=False)


class AddOneBotTrigger(Trigger):
    '''
    Adds one bot to the game unless the total player count is equal to or
    greater than playerLimit.
    '''

    def __init__(self, level, playerLimit=4, *args, **kwargs):
        super(AddOneBotTrigger, self).__init__(level, *args, **kwargs)
        self.playerLimit = playerLimit
        self.bot = None
        self._checking = False

    def doActivate(self):
        self.world.onPlayerAdded.addListener(self.gotPlayerAdded)
        self.world.onPlayerRemoved.addListener(self.gotPlayerRemoved)

        self._check()

    def doDeactivate(self):
        self._stopBot()

    def gotPlayerAdded(self, player, *args, **kwargs):
        self._check()

    def gotPlayerRemoved(self, player, *args, **kwargs):
        self._check()

    def _stopBot(self):
        agent, self.bot = self.bot, None
        if agent:
            agent.stop()
            self.world.game.detachAgent(agent)

    @defer.inlineCallbacks
    def _check(self):
        if self._checking:
            return
        self._checking = True
        try:
            while True:
                humans = sum(not p.bot for p in self.world.players)
                shouldHaveBot = humans < self.playerLimit
                if self.bot and not shouldHaveBot:
                    self._stopBot()
                    break
                elif shouldHaveBot and not self.bot:

                    nick = 'RangerBot'
                    # Pretect against tricksy humans editing their nicks
                    while any(p.nick == nick for p in self.world.players):
                        nick += "'"
                    self.bot = yield self.level.addBot(None, nick, 'ranger')
                else:
                    break

        finally:
            self._checking = False


class AddLimitedBotsTrigger(Trigger):
    def __init__(self,  level, minBots, maxBots, botClass, botNick, botTeam):
        super(AddLimitedBotsTrigger, self).__init__(level)
        self.minBots = minBots
        self.maxBots = maxBots
        self.botClass = botClass
        self.botNick = botNick
        self.botTeam = botTeam
        self.bots = []
        self._checking = False

    def doActivate(self):
        self.world.onPlayerAdded.addListener(self.gotPlayerAdded)
        self.world.onPlayerRemoved.addListener(self.gotPlayerRemoved)

        self._check()

    def doDeactivate(self):
        self.world.onPlayerAdded.removeListener(self.gotPlayerAdded)
        self.world.onPlayerRemoved.removeListener(self.gotPlayerRemoved)
        bots = self.bots
        self.bots = []

        for agent in bots:
            self._stopBot(agent)

    def gotPlayerAdded(self, player, *args, **kwargs):
        self._check()

    def gotPlayerRemoved(self, player, *args, **kwargs):
        self._check()

    def _stopBot(self, agent=None):
        if not agent:
            agent = self.bots.pop(-1)
        agent.stop()
        self.world.game.detachAgent(agent)

    @defer.inlineCallbacks
    def _check(self):
        if self._checking:
            return
        self._checking = True
        try:
            while True:
                humans = sum(
                    p.team not in (None, self.botTeam)
                    for p in self.world.players)
                botCount = len(self.bots)
                target = min(self.maxBots, max(self.minBots, humans))
                if botCount == target:
                    break
                elif botCount > target:
                    for i in range(botCount - target):
                        self._stopBot()
                else:
                    nick = '{} #{}'.format(self.botNick, botCount + 1)
                    # Pretect against tricksy humans editing their nicks
                    while any(p.nick == nick for p in self.world.players):
                        nick += "'"
                    agent = yield self.level.addBot(
                        self.botTeam, nick, self.botClass)
                    self.bots.append(agent)

        finally:
            self._checking = False
