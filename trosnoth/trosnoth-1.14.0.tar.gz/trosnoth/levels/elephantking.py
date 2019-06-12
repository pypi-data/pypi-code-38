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
from trosnoth.messages import AwardPlayerCoinMsg
from trosnoth.messages import SetPlayerTeamMsg
from trosnoth.model.universe_base import NEUTRAL_TEAM_ID
from trosnoth.triggers.coins import SlowlyIncrementLivePlayerCoinsTrigger
from trosnoth.triggers.deathmatch import AddOneBotTrigger
from trosnoth.triggers.elephant import (
    ElephantDurationScoreTrigger, EnsureElephantIsInGameTrigger,
)

from trosnoth.levels.base import Level, playLevel, RandomLayoutHelper

BONUS_COINS_FOR_WINNER = 500


class ElephantKingLevel(Level):
    allowAutoTeams = False
    levelName = 'Elephant King'

    halfMapWidth = 1
    mapHeight = 2
    blockRatio = 0.35
    defaultDuration = 360

    def __init__(self, duration=None):
        super(ElephantKingLevel, self).__init__()
        if duration is None:
            duration = self.defaultDuration
        self.duration = duration

    def getTeamToJoin(self, preferredTeam, user, bot):
        return None

    def setupMap(self):
        layoutHelper = RandomLayoutHelper(
            self.world, self.halfMapWidth, self.mapHeight,
            self.blockRatio, self.duration)
        layoutHelper.apply()

    async def run(self):
        for player in self.world.players:
            self.world.sendServerCommand(
                SetPlayerTeamMsg(player.id, NEUTRAL_TEAM_ID))

        SlowlyIncrementLivePlayerCoinsTrigger(self).activate()
        ElephantDurationScoreTrigger(self).activate()
        EnsureElephantIsInGameTrigger(self).activate()
        AddOneBotTrigger(self).activate()
        self.world.setActiveAchievementCategories({ACHIEVEMENT_TACTICAL})
        self.setUserInfo('Elephant King', (
            '* To get the elephant, kill the player who has it',
            '* The player who holds the elephant for the longest wins',
        ), BOT_GOAL_KILL_THINGS)
        self.world.abilities.set(zoneCaps=False, balanceTeams=False)
        self.world.uiOptions.set(
            teamIdsHumansCanJoin=[NEUTRAL_TEAM_ID],
            highlightElephant=True,
        )
        if self.duration:
            self.world.clock.startCountDown(self.duration)
        else:
            self.world.clock.stop()
        self.world.clock.propagateToClients()

        await self.world.clock.onZero.wait_future()

        # Game over!
        playerScores = self.world.scoreboard.playerScores
        maxScore = max(playerScores.values())
        winners = [
            p for p, score in playerScores.items()
            if score == maxScore]

        self.playSound('game-over-whistle.ogg')
        for winner in winners:
            self.notifyAll('{} wins'.format(winner.nick))
            self.world.sendServerCommand(
                AwardPlayerCoinMsg(winner.id, BONUS_COINS_FOR_WINNER))


if __name__ == '__main__':
    playLevel(ElephantKingLevel(duration=120), aiCount=1)
