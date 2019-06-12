

import functools

from trosnoth.const import (
    COINS_PER_ENEMY_CAP, COINS_PER_NEUTRAL_CAP,
    COINS_PER_ZONE_NEUTRALISED, COIN_FACTOR_FOR_ASSIST,
)
from trosnoth.messages import (
    TaggingZoneMsg, AwardPlayerCoinMsg,
)
from trosnoth.model.universe_base import NEUTRAL_TEAM_ID, NO_PLAYER


class ZoneCaptureCalculator(object):
    def __init__(self, world):
        self.finalised = False
        self.world = world

        self.capturedZones = {}     # zone -> captureInfo
        self.coinsForZone = {}      # zone -> coins
        self.pointsForZone = {}     # zone -> points
        self.neutralisedZones = set()

    @classmethod
    def applyToWorld(cls, world):
        if world.trosballManager.enabled:
            return
        if not world.abilities.zoneCaps:
            return

        capInfo = cls(world)
        tagger = None
        for zone in world.zones:
            info = zone.getCurrentCaptureInfo()
            if not info:
                continue

            capInfo.markZoneCaptured(zone, info)

        capInfo.finalise(sendNeutraliseEvent=True)

        capInfo.triggerServerEvents()
        for msg in capInfo.buildMessages():
            world.sendServerCommand(msg)

    def markZoneCaptured(self, zone, captureInfo):
        if self.finalised:
            raise RuntimeError('already finalised')
        if zone in self.capturedZones:
            raise ValueError('zone cannot be captured twice in one tick')
        team = captureInfo['team']
        if team == zone.owner:
            raise ValueError('zone is already owned by that team')

        if team is None:
            coins = COINS_PER_ZONE_NEUTRALISED
            points = 1
        elif zone.owner:
            coins = COINS_PER_ENEMY_CAP
            points = 2
        else:
            coins = COINS_PER_NEUTRAL_CAP
            points = 1

        self.capturedZones[zone] = captureInfo
        self.coinsForZone[zone] = coins
        self.pointsForZone[zone] = points

    def getOwner(self, zone):
        if zone in self.capturedZones:
            return self.capturedZones[zone]['team']
        return zone.owner

    def finalise(self, sendNeutraliseEvent=False):
        if self.finalised:
            return
        self.finalised = True
        if not self.capturedZones:
            return

        teamSectors = self.getTeamSectors()

        for team, sectors in list(teamSectors.items()):
            if len(sectors) <= 1:
                continue

            self.removeBestSectorFromList(team, sectors)
            for sector in sectors:
                self.neutralisedZones.update(sector)
                coinsToAward = len(sector) * COINS_PER_ZONE_NEUTRALISED
                cappedZones = self.getCapsRelatedToNeutralisedSector(
                    team, sector)
                coinsPerZone = int(coinsToAward / len(cappedZones) + 0.5)
                pointsPerZone = len(sector) / len(cappedZones)
                for zone in cappedZones:
                    self.coinsForZone[zone] += coinsPerZone
                    self.pointsForZone[zone] += pointsPerZone
                    if sendNeutraliseEvent:
                        tagger = self.capturedZones[zone]['player']
                        if tagger:
                            tagger.onNeutralisedSector(len(sector))

    def getTeamSectors(self):
        seenZones = set()
        teamSectors = dict((team, []) for team in self.world.teams)
        for zone in self.world.zones:
            if zone in seenZones:
                continue
            if self.getOwner(zone) is None:
                continue
            sector = zone.getContiguousZones(ownerGetter=self.getOwner)
            teamSectors[self.getOwner(zone)].append(sector)
            seenZones.update(sector)
        return teamSectors

    def removeBestSectorFromList(self, team, sectors):
        '''
        Accepts team and list of sectors, selects which one that team should
        keep, returns the rest.
        '''
        key = functools.partial(self.getSectorGoodnessKey, team)
        goodSector = max(sectors, key=key)
        sectors.remove(goodSector)

    def getSectorGoodnessKey(self, team, sector):
        '''
        Returns a key by which sectors can be sorted with sectors which should
        be kept sorted as maximum.
        '''
        livePlayerCount = 0
        deadPlayerCount = 0
        darkZoneCount = 0
        for zone in sector:
            for player in zone.players:
                if player.team == team:
                    if player.dead:
                        deadPlayerCount += 1
                    else:
                        livePlayerCount += 1
            if zone.isDark():
                darkZoneCount += 1

        return (len(sector), livePlayerCount, darkZoneCount, deadPlayerCount)

    def getCapsRelatedToNeutralisedSector(self, oldOwner, sector):
        '''
        Goes through the registered zone captures and finds which ones
        contributed to the neutralisation of this sector. Usually this will
        just be a single zone, but in some rare cases multiple captures
        during the some tick will have together caused the neutralisation.
        '''
        result = set()
        for zone, captureInfo in list(self.capturedZones.items()):
            if captureInfo['team'] == oldOwner:
                # A capture for a given team cannot count towards
                # neutralising the same team's zones.
                continue
            if any(z in sector for z in zone.getAdjacentZones()):
                result.add(zone)
        return result

    def triggerServerEvents(self):
        if not self.finalised:
            self.finalise()

        for zone, captureInfo in list(self.capturedZones.items()):
            points = self.pointsForZone[zone]
            self.world.onZoneCaptureFinalised(
                dict(captureInfo, zone=zone, points=points))

    def buildMessages(self):
        if not self.finalised:
            self.finalise()

        for zone, captureInfo in list(self.capturedZones.items()):
            tagger = captureInfo['player']
            playerId = tagger.id if tagger else NO_PLAYER
            team = captureInfo['team']
            teamId = team.id if team else NEUTRAL_TEAM_ID
            yield TaggingZoneMsg(zone.id, playerId, teamId)
            if tagger:
                coins = self.coinsForZone[zone]
                yield AwardPlayerCoinMsg(tagger.id, count=coins)

            helpers = captureInfo['attackers'] - {tagger}
            if helpers:
                coins = int(
                    self.coinsForZone[zone] * COIN_FACTOR_FOR_ASSIST
                    / len(helpers) + 0.5)
                for helper in helpers:
                    yield AwardPlayerCoinMsg(helper.id, count=coins)

        for zone in self.neutralisedZones:
            yield TaggingZoneMsg(zone.id, NO_PLAYER, NEUTRAL_TEAM_ID)
