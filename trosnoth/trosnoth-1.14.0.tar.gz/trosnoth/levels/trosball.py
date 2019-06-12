#!/usr/bin/env python3
if __name__ == '__main__':
    import os, sys
    sys.path.insert(0, os.path.join(
        os.path.abspath(os.path.dirname(__file__)), '..', '..'))

    # Install the asyncio reactor as early as possible
    import asyncio
    from twisted.internet import asyncioreactor
    asyncioreactor.install(asyncio.get_event_loop())

import logging

from trosnoth.const import (
    FRONT_LINE_TROSBALL, BOT_GOAL_SCORE_TROSBALL_POINT,
    ACHIEVEMENT_AFTER_GAME, ACHIEVEMENT_TACTICAL,
    BONUS_COINS_FOR_TROSBALL_SCORE,
)
from trosnoth.levels.base import Level, RandomLayoutHelper, playLevel
from trosnoth.messages import AwardPlayerCoinMsg
from trosnoth.triggers.coins import (
    SlowlyIncrementLivePlayerCoinsTrigger, AwardStartingCoinsTrigger,
)
from trosnoth.triggers.rabbits import RabbitHuntTrigger
from trosnoth.triggers.trosball import StandardTrosballScoreTrigger
from trosnoth.utils.event import waitForEvents

log = logging.getLogger(__name__)


class TrosballMatchBase(Level):
    levelName = 'Trosball'

    def __init__(self, duration=None, *args, **kwargs):
        super(TrosballMatchBase, self).__init__(*args, **kwargs)

        if duration is None:
            duration = 300
        self.totalDuration = duration
        self.roundDuration = duration
        self.scoreTrigger = None

    def setupMap(self):
        self.makeNewMap(first=True)

    async def run(self):
        assert self.world
        SlowlyIncrementLivePlayerCoinsTrigger(self).activate()
        startingCoinsTrigger = AwardStartingCoinsTrigger(self).activate()
        scoreTrigger = StandardTrosballScoreTrigger(self).activate()
        self.world.scoreboard.setMode(teams=True)

        self.setGameOptions()

        onBuzzer = self.world.clock.onZero
        onScore = scoreTrigger.onTrosballScore
        while True:
            self.initCountdown()
            await onBuzzer.wait_future()
            if startingCoinsTrigger:
                startingCoinsTrigger.deactivate()
                startingCoinsTrigger = None

            self.initRound()
            event, args = await waitForEvents([onBuzzer, onScore])
            if event == onBuzzer:
                break
            self.handleScore(**args)

            await self.world.sleep_future(3)
            self.resetMap()

        self.doGameOver()

        scoreTrigger.deactivate()

        rabbitHuntTrigger = RabbitHuntTrigger(self).activate()
        await rabbitHuntTrigger.onComplete.wait_future()

    def setGameOptions(self):
        self.world.setActiveAchievementCategories({ACHIEVEMENT_TACTICAL})
        self.world.uiOptions.set(
            showNets=True,
            frontLine=FRONT_LINE_TROSBALL,
        )
        self.world.abilities.set(zoneCaps=False)

        self.world.trosballManager.enable()

        self.setUserInfo('Trosball', (
            '* Score points by getting the trosball through the net',
            '* To throw the trosball, press the "use upgrade" key',
            '* The trosball explodes if held for too long',
        ), BOT_GOAL_SCORE_TROSBALL_POINT)

    def handleScore(self, team, player):
        self.playSound('short-whistle.ogg')
        self.world.trosballManager.placeInNet(team)
        self.world.scoreboard.teamScored(team)

        self.world.clock.pause()
        self.world.clock.propagateToClients()
        self.roundDuration = self.world.clock.value

        if player is not None:
            if player.team == team:
                message = '%s scored for %s!' % (player.nick, team.teamName)
            else:
                message = '%s scores an own goal!' % (player.nick,)
            self.world.sendServerCommand(AwardPlayerCoinMsg(
                player.id, count=BONUS_COINS_FOR_TROSBALL_SCORE))
        else:
            message = 'Score for %s!' % (team.teamName,)
        self.notifyAll(message)

    def resetMap(self):
        self.makeNewMap(first=False)
        for player in self.world.players:
            zone = self.world.selectZoneForTeam(player.teamId)
            player.makeAllDead(respawnTime=0.0)
            player.teleportToZoneCentre(zone)
            player.resyncBegun()

        self.world.trosballManager.resetToStartLocation()
        self.world.syncEverything()

    def initCountdown(self, delay=6):
        self.world.pauseStats()
        self.world.clock.startCountDown(delay, flashBelow=0)
        self.world.clock.propagateToClients()

        self.world.abilities.set(
            upgrades=False, respawn=False, leaveFriendlyZones=False)

    def initRound(self):
        self.playSound('startGame.ogg')
        self.world.resumeStats()
        self.world.abilities.set(
            upgrades=True, respawn=True, leaveFriendlyZones=True)

        self.world.clock.startCountDown(self.roundDuration)
        self.world.clock.propagateToClients()

    def doGameOver(self):
        self.world.setActiveAchievementCategories({ACHIEVEMENT_AFTER_GAME})

        maxScore = max(self.world.scoreboard.teamScores.values())
        winningTeams = [
            t for t, score in list(self.world.scoreboard.teamScores.items())
            if score == maxScore
        ]
        winner = winningTeams[0] if len(winningTeams) == 1 else None

        self.setWinner(winner)

    def makeNewMap(self, first):
        raise NotImplementedError('{}.makeNewMap'.format(
            self.__class__.__name__))


class RandomTrosballLevel(TrosballMatchBase):
    '''
    A standard Trosnoth level with no special events or triggers, played on
    a randomised map.
    '''

    def __init__(
            self, halfMapWidth=None, mapHeight=None, blockRatio=None,
            duration=None):
        super(RandomTrosballLevel, self).__init__(duration)

        self.halfMapWidth = halfMapWidth
        self.mapHeight = mapHeight
        self.blockRatio = blockRatio

    def makeNewMap(self, first):
        RandomLayoutHelper(
            self.world, self.halfMapWidth, self.mapHeight,
            self.blockRatio).apply()


class LoadedTrosballLevel(TrosballMatchBase):
    def __init__(self, mapLayout, duration=None):
        super(LoadedTrosballLevel, self).__init__(duration)

        self.mapLayout = mapLayout

    def makeNewMap(self, first):
        if first:
            self.world.setLayout(self.mapLayout)


if __name__ == '__main__':
    playLevel(RandomTrosballLevel(duration=150), aiCount=7)
