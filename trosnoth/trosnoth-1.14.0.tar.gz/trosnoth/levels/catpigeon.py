#!/usr/bin/env python3
if __name__ == '__main__':
    import os, sys
    sys.path.insert(0, os.path.join(
        os.path.abspath(os.path.dirname(__file__)), '..', '..'))

    # Install the asyncio reactor as early as possible
    import asyncio
    from twisted.internet import asyncioreactor
    asyncioreactor.install(asyncio.get_event_loop())

from twisted.internet import defer

from trosnoth.const import ACHIEVEMENT_TACTICAL, BOT_GOAL_HUNT_RABBITS
from trosnoth.levels.base import Level, playLevel
from trosnoth.messages import AwardPlayerCoinMsg, SetPlayerTeamMsg
from trosnoth.triggers.base import Trigger
from trosnoth.triggers.coins import SlowlyIncrementLivePlayerCoinsTrigger
from trosnoth.triggers.deathmatch import (
    PlayerKillScoreTrigger, makeCirclesLayout, AddLimitedBotsTrigger,
)


MIN_PIGEONS = 4
MAX_PIGEONS = 12
BONUS_COINS_FOR_WINNER = 500


class CatPigeonLevel(Level):
    allowAutoTeams = False
    levelName = 'Cat Among Pigeons'

    def __init__(self, duration=None):
        super(CatPigeonLevel, self).__init__()
        if duration is None:
            duration = 6 * 60
        self.duration = duration
        self.blueTeam = self.redTeam = None

    def getTeamToJoin(self, preferredTeam, user, bot):
        return self.blueTeam

    def setupMap(self):
        self.blueTeam = self.world.teams[0]
        self.redTeam = self.world.teams[1]
        self.world.setLayout(makeCirclesLayout(self.world.layoutDatabase))

    async def run(self):
        self.setTeamName(self.blueTeam, 'Cats')
        self.setTeamName(self.redTeam, 'Pigeons')

        for player in self.world.players:
            if not player.bot:
                self.world.sendServerCommand(
                    SetPlayerTeamMsg(player.id, self.blueTeam.id))

        SlowlyIncrementLivePlayerCoinsTrigger(self).activate()
        scoreTrigger = PlayerKillScoreTrigger(self).activate()
        RespawnOnJoinTrigger(self).activate()
        botTrigger = AddLimitedBotsTrigger(
            self, MIN_PIGEONS, MAX_PIGEONS,
            'sirrobin', 'Pigeon', self.redTeam).activate()
        self.world.setActiveAchievementCategories({ACHIEVEMENT_TACTICAL})
        self.setUserInfo('Cat Among Pigeons', (
            '* Kill as many enemy players as you can',
        ), BOT_GOAL_HUNT_RABBITS)
        self.world.abilities.set(zoneCaps=False, balanceTeams=False)
        self.world.uiOptions.set(teamIdsHumansCanJoin=[b'A'])
        if self.duration:
            self.world.clock.startCountDown(self.duration)
        else:
            self.world.clock.stop()
        self.world.clock.propagateToClients()

        await self.world.clock.onZero.wait_future()

        # Game over!
        self.world.finaliseStats()
        scoreTrigger.deactivate()
        botTrigger.deactivate()
        playerScores = self.world.scoreboard.playerScores
        maxScore = max(playerScores.values())
        winners = [
            p for p, score in list(playerScores.items())
            if score == maxScore and p.team == self.blueTeam]

        self.playSound('game-over-whistle.ogg')
        for winner in winners:
            self.notifyAll('{} wins'.format(winner.nick))
            self.world.sendServerCommand(
                AwardPlayerCoinMsg(winner.id, BONUS_COINS_FOR_WINNER))

        await self.world.sleep_future(3)


class RespawnOnJoinTrigger(Trigger):
    def doActivate(self):
        self.world.onPlayerAdded.addListener(self.gotPlayerAdded)
        for player in self.world.players:
            self.gotPlayerAdded(player)

    def doDeactivate(self):
        self.world.onPlayerAdded.removeListener(self.gotPlayerAdded)

    def gotPlayerAdded(self, player, *args, **kwargs):
        if player.team == self.level.blueTeam:
            mapLayout = self.world.map.layout
            self.world.magicallyMovePlayer(
                player, (mapLayout.centreX, mapLayout.centreY), alive=True)


if __name__ == '__main__':
    playLevel(CatPigeonLevel(duration=180), aiCount=1)
