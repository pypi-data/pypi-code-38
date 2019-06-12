

import logging
import string

from trosnoth.const import ZONE_CAP_DISTANCE
from trosnoth.utils import math

log = logging.getLogger(__name__)


class ZoneDef(object):
    '''Stores static information about the zone.

    Attributes:
        adjacentZones - mapping from adjacent ZoneDef objects to collection of
            map blocks joining the zones.
        id - the zone id
        initialOwnerIndex - the team that initially owned this zone,
            represented as a number (0 for neutral, 1 or 2 for a team).
        pos - the coordinates of this zone in the map
    '''

    def __init__(
            self, id, initialOwnerIndex, xCoord, yCoord,
            initialDarkState=True):
        self.id = id
        self.initialOwnerIndex = initialOwnerIndex
        self.initialDarkState = initialDarkState
        self.pos = xCoord, yCoord

        primes, index = divmod(id, 26)
        self.label = string.ascii_uppercase[index] + "'" * primes

        self.cached_adjacentZones = set()
        self.cached_unblockedNeighbours = set()
        self.cache_serial = 0

    def __str__(self):
        if self.id is None:
            return 'Z---'
        return 'Z%3d' % self.id


class DynamicZoneLogic(object):
    '''
    Contains all the methods for performing logic about whether zones are
    capturable and what happens if they are captured.

    This serves as a useful base class for both the in-game ZoneState class,
    and simulation classes used by bots to evaluate different options.
    '''

    def __init__(self, universe, zoneDef):
        self.defn = zoneDef
        self.id = zoneDef.id
        self.world = universe
        self.adjacentZonesCache = None

        # Subclasses may initialise these differently
        self.owner = None
        self.dark = False
        self.players = set()
        self.frozen = False

    def __str__(self):
        # Debug: uniquely identify this zone within the universe.
        if self.id is None:
            return 'Z---'
        return 'Z%3d' % self.id

    def getZoneFromDefn(self, zoneDef):
        '''
        Helper function for getAdjacentZones(), getUnblockedNeighbours(), and
        functions that rely on these. Should return the zone object that
        corresponds to the given ZoneDef.
        '''
        raise NotImplementedError('{}.getZoneFromDefn'.format(
            self.__class__.__name__))

    def isNeutral(self):
        return self.owner is None

    def isEnemyTeam(self, team):
        return team != self.owner and team is not None

    def isDark(self):
        return self.dark

    def makeDarkIfNeeded(self):
        '''This method should be called by an adjacent friendly zone that has
        been tagged and gained. It will check to see if it now has all
        surrounding orbs owned by the same team, in which case it will
        change its zone ownership.'''

        # If the zone is already owned, ignore it
        if not self.dark and self.owner is not None:
            for zone in self.getAdjacentZones():
                if self.isEnemyTeam(zone.owner):
                    break
            else:
                self.dark = True
                self.world.onZoneStateChanged(self)

    def playerIsWithinTaggingDistance(self, player):
        if player.team and not player.team.abilities.zoneCaps:
            return False
        distance = math.distance(self.defn.pos, player.pos)
        return distance < ZONE_CAP_DISTANCE

    def getContiguousZones(self, ownerGetter=None):
        '''
        Returns a set of all contiguous zones with orb owned by the same team
        as this zone.
        '''
        if ownerGetter is None:
            ownerGetter = lambda z: z.owner

        myOwner = ownerGetter(self)
        sector = set()
        stack = [self]
        while stack:
            zone = stack.pop()
            if zone in sector:
                continue
            sector.add(zone)
            for adjacentZone in zone.getAdjacentZones():
                if ownerGetter(adjacentZone) == myOwner:
                    stack.append(adjacentZone)
        return sector

    def getCurrentCaptureInfo(self):
        '''
        Checks to see whether the zone is being captured this tick. If not,
        return None. Otherwise, return a dict with information about the
        capture.

        The returned dict contains:
            team - the team that should now own the zone (None if zone
                neutralised due to multiple simultaneous tags)
            player - the player who captured the zone (None if zone
                neutralised due to multiple simultaneous tags)
            defenders - players in the zone who are on the defending team
            attackers - players in the zone who are on the team(s) who
                tagged the zone
        '''
        teamsToPlayers = self.getCountedPlayersByTeam()
        teamsWhoCanTag = self.teamsAbleToTag()
        taggingPlayers = []

        if (len(teamsWhoCanTag) == 1 and list(teamsWhoCanTag)[0] ==
                self.owner):
            # No need to check again - we are already the owner
            return None

        attackers = set()
        for team in teamsWhoCanTag:
            for player in teamsToPlayers[team]:
                if self.playerIsWithinTaggingDistance(player):
                    taggingPlayers.append(player)
                    if player.team != self.owner:
                        attackers.update(teamsToPlayers[team])
                    # Only allow one player from each team to have tagged it.
                    break

        result = {
            'attackers': attackers,
            'defenders': set(teamsToPlayers.get(self.owner, [])),
        }
        if len(taggingPlayers) > 1:
            # Both teams tagged - becomes neutral
            if self.owner is None:
                return None

            result['player'] = None
            result['team'] = None
        elif (len(taggingPlayers) == 1 and list(taggingPlayers)[0].team !=
                self.owner):
            result['player'] = taggingPlayers[0]
            result['team'] = taggingPlayers[0].team
        else:
            return None

        return result

    def clearPlayers(self):
        self.players.clear()

    def addPlayer(self, player):
        self.players.add(player)

    def removePlayer(self, player):
        self.players.remove(player)

    def getCountedPlayersByTeam(self):
        result = dict((team, []) for team in self.world.teams)

        for player in self.players:
            if player.dead:
                continue
            if player.team is not None:
                result[player.team].append(player)
        return result

    def getPlayerCounts(self):
        '''
        Returns a list of (count, teams) ordered by count descending, where
        count is the number of counted (living) players in the zone
        and teams is the teams with that number of players. Excludes teams
        which do not own the zone and cannot capture it.
        '''
        teamsByCount = {}
        for team, players in self.getCountedPlayersByTeam().items():
            if (
                    team != self.owner
                    and not self.adjacentToAnotherZoneOwnedBy(team)):
                # If the enemy team doesn't have an adjacent zone, they don't
                # count towards numerical advantage.
                continue
            teamsByCount.setdefault(len(players), []).append(team)

        return sorted(iter(teamsByCount.items()), reverse=True)

    def isCapturableBy(self, team):
        '''
        Returns True or False depending on whether this zone can be captured by
        the given team. This takes into account both the zone location and the
        number of players in the zone.
        '''
        return team != self.owner and team in self.teamsAbleToTag()

    def isBorderline(self):
        '''
        Returns a value indicating whether this is a borderline zone. A borderline
        zone is defined as a zone which cannot be tagged by any enemy team, but
        could be if there was one more enemy player in the zone.
        '''
        moreThanThreeDefenders = False

        playerCounts = self.getPlayerCounts()
        while playerCounts:
            count, teams = playerCounts.pop(0)
            if moreThanThreeDefenders and count < 3:
                return False

            if count == 0:
                if any(t != self.owner for t in teams):
                    # There is a team which could tag if it had one attacker
                    return True

            elif count < 3:
                if len(teams) == 1:
                    # If it's an attacking team it's capturable, if it's a
                    # defending team it's not borderline.
                    return False

                # If an attacking team had one more player they could capture
                return True

            elif count == 3:
                if moreThanThreeDefenders:
                    return True

                if len(teams) == 1:
                    # If it's an attacking team it's capturable, if it's a
                    # defending team it's not borderline.
                    return False

                # Team could capture if it had 4 attackers
                return True

            else:
                if any(t != self.owner for t in teams):
                    # Already capturable
                    return False

                moreThanThreeDefenders = True

        return False

    def getAdjacentZones(self):
        '''
        Iterates through ZoneStates adjacent to this one.
        '''
        if self.adjacentZonesCache is None:
            self.adjacentZonesCache = {
                self.world.zoneWithDef[adjZoneDef] for adjZoneDef in
                    self.world.layout.getAdjacentZoneDefs(self.defn)
            }
        return iter(self.adjacentZonesCache)

    def getNextZone(self, xDir, yDir):
        x, y = self.defn.pos
        map = self.world.map
        return map.getZoneAtPoint((
            x + xDir * (map.layout.zoneBodyWidth +
                        map.layout.zoneInterfaceWidth),
            y + yDir * 1.5 * map.layout.halfZoneHeight,
        ))

    def getUnblockedNeighbours(self):
        '''
        Iterates through ZoneStates adjacent to this one which are not blocked
        off.
        '''
        for adjZoneDef in self.world.layout.getUnblockedNeighbours(self.defn):
            yield self.world.zoneWithDef[adjZoneDef]

    def adjacentToAnotherZoneOwnedBy(self, team):
        '''
        Returns whether or not this zone is adjacent to a zone whose orb is
        owned by the given team.
        '''
        for adjZone in self.getAdjacentZones():
            if adjZone.owner == team:
                return True
        return False

    def teamsAbleToTag(self):
        '''
        Returns the set of teams who have enough players to tag a zone
        (ignoring current zone ownership). Teams must have:
         (a) strict numerical advantage in this zone; or
         (b) more than 3 players in this zone.
        '''
        result = set()

        playerCounts = self.getPlayerCounts()
        while playerCounts:
            count, teams = playerCounts.pop(0)
            if count <= 3:
                if not result and len(teams) == 1 and count > 0:
                    result.update(teams)
                break
            result.update(teams)
        return result

    def consequenceOfCapture(self):
        '''
        Uses the zone neutralisation logic to calculate how many zone points an
        enemy team would gain by capturing this zone. That is, 2 points for the
        zone itself, plus one for each zone neutralised in the process.
        '''
        if self.owner is None:
            # Always one point for capturing a neutral zone
            return 1

        seen = {self}
        explore = [z for z in self.getAdjacentZones() if z.owner == self.owner]
        sectors = []
        while explore:
            zone = explore.pop(0)
            if zone in seen:
                continue

            thisSector = [zone]
            score = 0
            while thisSector:
                score += 1
                zone = thisSector.pop(0)
                seen.add(zone)
                for z in zone.getAdjacentZones():
                    if z.owner == self.owner and z not in seen:
                        thisSector.append(z)
            sectors.append(score)

        if sectors:
            # Largest sector is not lost
            sectors.remove(max(sectors))

        # Two points for capture, plus one for each zone neutralised
        return 2 + sum(sectors)


class ZoneState(DynamicZoneLogic):
    '''
    Represents information about the dynamic state of a given zone during a
    game.
    '''

    def __init__(self, universe, zoneDef):
        super(ZoneState, self).__init__(universe, zoneDef)

        universe.zoneWithDef[zoneDef] = self

        teamIndex = zoneDef.initialOwnerIndex
        if teamIndex is None:
            self.owner = None
            self.dark = False
        else:
            self.owner = universe.teams[teamIndex]
            self.dark = zoneDef.initialDarkState

            # Tell the team object that it owns one more zone
            self.owner.zoneGained()

        self.previousOwner = self.owner

    def getZoneFromDefn(self, zoneDef):
        return self.world.zoneWithDef[zoneDef]

    def tag(self, player):
        '''This method should be called when the orb in this zone is tagged'''
        self.previousOwner = self.owner
        self.dark = False

        # Inform the team objects
        if self.owner:
            self.owner.zoneLost()
        if player is not None:
            team = player.team
            if team is not None:
                team.zoneGained()
        else:
            team = None

        self.owner = team
        for zone in self.getAdjacentZones():
            if zone.owner == team or self.isNeutral():
                # Allow the adjacent zone to check if it is entirely
                # surrounded by non-enemy zones
                zone.makeDarkIfNeeded()
        self.makeDarkIfNeeded()
        self.world.onZoneStateChanged(self)

    def updateByTrosballPosition(self, position):
        self.dark = False
        oldOwner = self.owner
        if abs(position[0] - self.defn.pos[0]) < 1e-5:
            self.owner = None
        elif position[0] < self.defn.pos[0]:
            self.owner = self.world.teams[1]
        else:
            self.owner = self.world.teams[0]
        if oldOwner != self.owner:
            self.world.onZoneStateChanged(self)

    def setOwnership(self, team, dark):
        if self.owner is not None:
            self.owner.zoneLost()
        self.owner = team
        if team is not None:
            team.zoneGained()
        self.dark = dark

    @staticmethod
    def canTag(numTaggers, numDefenders):
        '''
        Deprecated, do not use.
        '''
        return numTaggers > numDefenders or numTaggers > 3
