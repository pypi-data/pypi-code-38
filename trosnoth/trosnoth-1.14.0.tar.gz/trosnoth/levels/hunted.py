#!/usr/bin/env python3
if __name__ == '__main__':
    import os, sys
    sys.path.insert(0, os.path.join(
        os.path.abspath(os.path.dirname(__file__)), '..', '..'))

    # Install the asyncio reactor as early as possible
    import asyncio
    from twisted.internet import asyncioreactor
    asyncioreactor.install(asyncio.get_event_loop())

from trosnoth.const import ACHIEVEMENT_TACTICAL, BOT_GOAL_KILL_THINGS
from trosnoth.levels.base import Level, playLevel
from trosnoth.messages import AwardPlayerCoinMsg, SetPlayerTeamMsg
from trosnoth.triggers.coins import SlowlyIncrementLivePlayerCoinsTrigger
from trosnoth.triggers.deathmatch import (
    makeCirclesLayout, AddLimitedBotsTrigger, PlayerLifeScoreTrigger,
    PlayerKillScoreTrigger,
)


MIN_HUNTERS = 4
MAX_HUNTERS = 12
BONUS_COINS_FOR_WINNER = 500


class HuntedLevel(Level):
    allowAutoTeams = False
    levelName = 'Hunted'

    def __init__(self, duration=None):
        super(HuntedLevel, self).__init__()
        if duration is None:
            duration = 6 * 60
        self.duration = duration
        self.blueTeam = self.redTeam = None

    def getTeamToJoin(self, preferredTeam, user, bot):
        return self.redTeam

    def setupMap(self):
        self.blueTeam = self.world.teams[0]
        self.redTeam = self.world.teams[1]
        self.world.setLayout(makeCirclesLayout(self.world.layoutDatabase))

    async def run(self):
        try:
            self.setTeamName(self.blueTeam, 'Hunters')
            self.setTeamName(self.redTeam, 'Hunted')
            self.redTeam.abilities.set(aggression=False)

            for player in self.world.players:
                if not player.bot:
                    self.world.sendServerCommand(
                        SetPlayerTeamMsg(player.id, self.redTeam.id))
                    zone = self.world.selectZoneForTeam(self.redTeam.id)
                    self.world.magicallyMovePlayer(
                        player, zone.defn.pos, alive=True)


            SlowlyIncrementLivePlayerCoinsTrigger(self).activate()
            scoreTrigger = PlayerLifeScoreTrigger(
                self, teams={self.redTeam}).activate()
            PlayerKillScoreTrigger(self, dieScore=0).activate()
            botTrigger = AddLimitedBotsTrigger(
                self, MIN_HUNTERS, MAX_HUNTERS,
                'terminator', 'Terminator', self.blueTeam).activate()
            self.world.setActiveAchievementCategories({ACHIEVEMENT_TACTICAL})
            self.setUserInfo('Hunted', (
                '* Die as few times as possible',
                '* Players score points for every second they are alive',
            ), BOT_GOAL_KILL_THINGS)
            self.world.abilities.set(zoneCaps=False, balanceTeams=False)
            self.world.uiOptions.set(teamIdsHumansCanJoin=[b'B'])
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
                if score == maxScore and p.team == self.redTeam]

            self.playSound('game-over-whistle.ogg')
            for winner in winners:
                self.notifyAll('{} wins'.format(winner.nick))
                self.world.sendServerCommand(
                    AwardPlayerCoinMsg(winner.id, BONUS_COINS_FOR_WINNER))

            await self.world.sleep_future(3)
        finally:
            self.redTeam.abilities.set(aggression=True)


if __name__ == '__main__':
    playLevel(HuntedLevel(duration=180), aiCount=1)
