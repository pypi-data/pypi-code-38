#!/usr/bin/env python3
if __name__ == '__main__':
    import os, sys
    sys.path.insert(0, os.path.join(
        os.path.abspath(os.path.dirname(__file__)), '..', '..'))

    # Install the asyncio reactor as early as possible
    import asyncio
    from twisted.internet import asyncioreactor
    asyncioreactor.install(asyncio.get_event_loop())

import random

from trosnoth.const import BOT_GOAL_CAPTURE_MAP, ACHIEVEMENT_TACTICAL
from trosnoth.levels.base import playLevel, Level, SetPlayerTeamMsg
from trosnoth.messages import AwardPlayerCoinMsg, ZoneStateMsg
from trosnoth.model.map import ZoneStep, ZoneLayout
from trosnoth.model.universe import OrbRegion
from trosnoth.model.universe_base import NEUTRAL_TEAM_ID
from trosnoth.triggers.coins import SlowlyIncrementLivePlayerCoinsTrigger
from trosnoth.utils.event import waitForEvents
from trosnoth.utils.math import distance

BONUS_COINS_FOR_WINNER = 500


class OrbChaseLevel(Level):
    allowAutoTeams = False
    levelName = 'Orb Chase'

    def __init__(self, duration=None):
        super(OrbChaseLevel, self).__init__()
        if duration is None:
            duration = 6 * 60
        self.duration = duration
        self.team = None
        self.targetZone = None
        self.targetTeamId = None

    def getTeamToJoin(self, preferredTeam, user, bot):
        return self.team

    def setupMap(self):
        self.team = self.world.teams[0]
        self.targetTeamId = self.world.teams[1].id
        self.world.setLayout(self.makeRingLayout())

    def makeRingLayout(self):
        zones = ZoneLayout()

        # Outer ring
        northSpawnZone = zone = zones.firstLocation
        zone = zones.connectZone(zone, ZoneStep.SOUTHEAST)
        zone = zones.connectZone(zone, ZoneStep.SOUTHEAST)
        eastZone = zone = zones.connectZone(zone, ZoneStep.SOUTH)
        eastSpawnZone = zone = zones.connectZone(zone, ZoneStep.SOUTH)
        zone = zones.connectZone(zone, ZoneStep.SOUTHWEST)
        zone = zones.connectZone(zone, ZoneStep.SOUTHWEST)
        southWestZone = zone = zones.connectZone(zone, ZoneStep.NORTHWEST)
        westSpawnZone = zone = zones.connectZone(zone, ZoneStep.NORTHWEST)
        zone = zones.connectZone(zone, ZoneStep.NORTH)
        zone = zones.connectZone(zone, ZoneStep.NORTH)
        northWestZone = zone = zones.connectZone(zone, ZoneStep.NORTHEAST)
        zone = zones.connectZone(zone, ZoneStep.NORTHEAST)

        # Inner swirl
        zone = zones.connectZone(eastZone, ZoneStep.NORTHWEST)
        zone = zones.connectZone(zone, ZoneStep.NORTHWEST)
        zones.connectZone(zone, ZoneStep.SOUTH, ownerIndex=0, dark=True)
        zone = zones.connectZone(southWestZone, ZoneStep.NORTHEAST)
        zone = zones.connectZone(zone, ZoneStep.NORTHEAST)
        zones.connectZone(zone, ZoneStep.NORTHWEST)
        zone = zones.connectZone(northWestZone, ZoneStep.SOUTH)
        zone = zones.connectZone(zone, ZoneStep.SOUTH)
        zones.connectZone(zone, ZoneStep.NORTHEAST)

        # Outer spawn zones
        zones.connectZone(
            northSpawnZone, ZoneStep.NORTH, ownerIndex=0, dark=True)
        zones.connectZone(
            eastSpawnZone, ZoneStep.SOUTHEAST, ownerIndex=0, dark=True)
        zones.connectZone(
            westSpawnZone, ZoneStep.SOUTHWEST, ownerIndex=0, dark=True)

        return zones.createMapLayout(
            self.world.layoutDatabase, autoOwner=False)

    async def run(self):
        self.setTeamName(self.team, 'Racers')
        for player in self.world.players:
            self.world.sendServerCommand(
                SetPlayerTeamMsg(player.id, self.team.id))

        SlowlyIncrementLivePlayerCoinsTrigger(self).activate()
        self.world.setActiveAchievementCategories({ACHIEVEMENT_TACTICAL})
        self.world.scoreboard.setMode(players=True)
        self.world.abilities.set(zoneCaps=False, balanceTeams=False)
        self.world.uiOptions.set(teamIdsHumansCanJoin=[b'A'])

        await self.pregameCountdownPhase()
        await self.mainPhase()

        # Game over!
        playerScores = self.world.scoreboard.playerScores
        maxScore = max(playerScores.values())
        winners = [
            p for p, score in list(playerScores.items())
            if score == maxScore
        ]

        self.playSound('game-over-whistle.ogg')
        for winner in winners:
            self.notifyAll('{} wins'.format(winner.nick))
            self.world.sendServerCommand(
                AwardPlayerCoinMsg(winner.id, BONUS_COINS_FOR_WINNER))

    async def pregameCountdownPhase(self, delay=10):
        self.setUserInfo('Get Ready...', (
            '* Game will begin soon',
            '* Score points by touching the red orb',
        ), BOT_GOAL_CAPTURE_MAP)
        self.world.clock.startCountDown(delay, flashBelow=0)
        self.world.clock.propagateToClients()

        self.world.pauseStats()
        self.world.abilities.set(respawn=False)
        await self.world.clock.onZero.wait_future()

    async def mainPhase(self):
        self.setUserInfo('Orb Chase', (
            '* Score points by touching the red orb',
        ), BOT_GOAL_CAPTURE_MAP)
        self.notifyAll('The game is now on!!')
        self.playSound('startGame.ogg')
        self.world.resumeStats()
        self.world.abilities.set(respawn=True)

        if self.duration:
            self.world.clock.startCountDown(self.duration)
        else:
            self.world.clock.stop()
        self.world.clock.propagateToClients()

        onClockZero = self.world.clock.onZero

        while True:
            zone = self.selectZone()
            region = OrbRegion(self.world, zone.defn)
            self.world.addRegion(region)
            try:
                event, args = await waitForEvents(
                    [onClockZero, region.onEnter])

                if event == onClockZero:
                    break

                self.playSound('short-whistle.ogg')
                self.world.scoreboard.playerScored(args['player'], 1)
            finally:
                self.world.removeRegion(region)

    def selectZone(self):
        if self.targetZone:
            self.world.sendServerCommand(
                ZoneStateMsg(self.targetZone.id, NEUTRAL_TEAM_ID, True))

        allZones = [z for z in self.world.zones if z.owner is None]
        options = [z for z in allZones if not z.players]
        if options:
            zone = random.choice(options)
        else:
            zone = min(
                allZones,
                key=lambda z: min(
                    distance(z.defn.pos, p.pos) for p in z.players))

        self.world.sendServerCommand(
            ZoneStateMsg(zone.id, self.targetTeamId, True))
        self.targetZone = zone
        return zone


if __name__ == '__main__':
    playLevel(OrbChaseLevel(duration=180))
