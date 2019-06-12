import logging
import os
import random

from trosnoth.data import getPath, user
from trosnoth.model import maptree

from trosnoth.model.zone import ZoneDef, ZoneState
from trosnoth.utils.unrepr import unrepr

log = logging.getLogger(__name__)


class ZoneLayoutLocationDelta(object):
    '''
    Represents the difference between two possible zone locations in a
    ZoneLayout representation.
    '''

    def __init__(self, xDelta, yDelta):
        if (xDelta + yDelta) % 2 != 0:
            raise ValueError('Invalid location deltas')
        self.xDelta = xDelta
        self.yDelta = yDelta

    def __repr__(self):
        return '{}({}, {})'.format(
            self.__class__.__name__, self.xDelta, self.yDelta)

    def __neg__(self):
        return self.__class__(-self.xDelta, -self.yDelta)

    def __hash__(self):
        return hash((self.xDelta, self.yDelta))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return (self.xDelta, self.yDelta) == (other.xDelta, other.yDelta)

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(
            self.xDelta + other.xDelta, self.yDelta + other.yDelta)

    def __sub__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self + (-other)

    def __invert__(self):
        '''
        Mirror in the x direction, for use with symmetrical layouts.
        '''
        return self.__class__(-self.xDelta, self.yDelta)


class ZoneStep(object):
    '''
    All possible ZoneLayoutLocationDeltas which occur between two adjacent
    zones.
    '''
    NORTH = ZoneLayoutLocationDelta(0, -2)
    NORTHEAST = ZoneLayoutLocationDelta(1, -1)
    NORTHWEST = ZoneLayoutLocationDelta(-1, -1)
    SOUTH = ZoneLayoutLocationDelta(0, 2)
    SOUTHEAST = ZoneLayoutLocationDelta(1, 1)
    SOUTHWEST = ZoneLayoutLocationDelta(-1, 1)

    OPTIONS = {NORTH, NORTHEAST, NORTHWEST, SOUTH, SOUTHEAST, SOUTHWEST}


class ZoneLayoutLocation(object):
    '''
    Represents a possible zone location inside the ZoneLayout representation.
    '''

    def __init__(self, xIndex, yIndex):
        if (xIndex + yIndex) % 2 != 0:
            raise ValueError('Invalid location indices')
        self.xIndex = xIndex
        self.yIndex = yIndex

    def __repr__(self):
        return '{}({}, {})'.format(
            self.__class__.__name__, self.xIndex, self.yIndex)

    def __hash__(self):
        return hash((self.xIndex, self.yIndex))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return (self.xIndex, self.yIndex) == (other.xIndex, other.yIndex)

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        if not isinstance(other, ZoneLayoutLocationDelta):
            return NotImplemented
        return self.__class__(
            self.xIndex + other.xDelta, self.yIndex + other.yDelta)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return ZoneLayoutLocationDelta(
                self.xIndex - other.xIndex,
                self.yIndex - other.yIndex
            )
        if isinstance(other, ZoneLayoutLocationDelta):
            return self + (-other)
        return NotImplemented

    def __invert__(self):
        return self.__class__(-self.xIndex, self.yIndex)


class ZoneLayout(object):
    '''
    Represents a distribution of zones on a map, with information about
    which zones are connected to which. Does not store information about
    actual terrain etc. beyond whether transitions between adjacent zones are
    blocked or open.

    When a ZoneLayout() is newly constructed, it has a single zone, located
    at z.firstLocation.

    If symmetryEnforced is True, this zone layout will be symmetrical around
    the column in which the first zone is located.
    '''

    @classmethod
    def generate(cls, halfMapWidth, mapHeight, blockRatio):
        '''
        Generates and returns a new symmetrical ZoneLayout with the given
        parameters. A blockRatio of zero will result in a completely open
        map. A blockRatio of one will result in a completely blocked map.
        '''
        result = ZoneLayout(symmetryEnforced=True)

        if halfMapWidth % 2 == 0:
            middleHeight = mapHeight + 2
            evenHeight = mapHeight + 1
            oddHeight = mapHeight
        else:
            middleHeight = oddHeight = mapHeight + 1
            evenHeight = mapHeight

        def addColumn(startLocation, columnHeight, previousHeight):
            if not result.hasZoneAt(startLocation):
                result.addZoneAt(startLocation)

            current = startLocation
            connections = []
            for i in range(columnHeight - 1):
                next = current + ZoneStep.SOUTH
                result.addZoneAt(next)
                connections.append((current, ZoneStep.SOUTH))
                current = next

            if previousHeight:
                if previousHeight < columnHeight:
                    assert previousHeight == columnHeight - 1
                    connections.append((startLocation, ZoneStep.SOUTHWEST))
                    connections.append((current, ZoneStep.NORTHWEST))
                    current = startLocation + ZoneStep.SOUTH
                    count = previousHeight - 1
                else:
                    assert previousHeight == columnHeight + 1
                    current = startLocation
                    count = columnHeight

                for i in range(count):
                    connections.append((current, ZoneStep.NORTHWEST))
                    connections.append((current, ZoneStep.SOUTHWEST))
                    current += ZoneStep.SOUTH

            while connections:
                location, direction = connections.pop(0)
                if random.random() >= blockRatio:
                    result.connectZone(location, direction)

        location = result.firstLocation
        prevHeight = middleHeight
        addColumn(location, middleHeight, 0)
        for i in range(halfMapWidth):
            if i % 2 == 0:
                height = evenHeight
            else:
                height = oddHeight

            if height < prevHeight:
                location += ZoneStep.SOUTHEAST
            else:
                location += ZoneStep.NORTHEAST

            addColumn(location, height, prevHeight)
            prevHeight = height

        result.makeEverywhereReachable()

        return result

    def __init__(self, symmetryEnforced=False):
        self.symmetryEnforced = symmetryEnforced
        self.zoneConnections = {}
        self.firstLocation = ZoneLayoutLocation(0, 0)
        self.zoneOwners = {}
        self.addZoneAt(self.firstLocation)

    def isSymmetrical(self):
        for location in self.zoneConnections:
            mirror = ~location
            if not self.hasZoneAt(mirror):
                return False
            thisConnected = self.getConnectedDirections(location)
            mirrorConnected = self.getConnectedDirections(mirror)
            if len(thisConnected) != len(mirrorConnected):
                return False
            for direction in thisConnected:
                if ~direction not in mirrorConnected:
                    return False
        return True

    def enforceSymmetry(self, symmetryEnforced):
        if symmetryEnforced:
            if not self.isSymmetrical():
                raise RuntimeError('Layout is not symmetrical')
            self.symmetryEnforced = symmetryEnforced

    def addZoneAt(
            self, location, ownerIndex=-1, dark=False, _bypassSymmetry=False):
        if location in self.zoneConnections:
            raise KeyError('zone at that location already exists')
        self.zoneConnections[location] = {
            ZoneStep.SOUTH: False,
            ZoneStep.SOUTHEAST: False,
            ZoneStep.SOUTHWEST: False,
        }
        if ownerIndex != -1:
            self.setZoneOwner(location, ownerIndex, dark)
        if not _bypassSymmetry and self.symmetryEnforced:
            if location != ~location:
                reverseOwner = self._getReverseOwner(ownerIndex)
                self.addZoneAt(~location, ownerIndex, _bypassSymmetry=True)

        return location

    def _getReverseOwner(self, ownerIndex):
        if ownerIndex in (0, 1):
            return 1 - ownerIndex
        return ownerIndex

    def hasZoneAt(self, location):
        return location in self.zoneConnections

    def connectZone(
            self, startLocation, direction, ownerIndex=-1, dark=False,
            _bypassSymmetry=False):
        '''
        Connects the zone at the given location to the zone in the given
        direction. The zone at the start location must exist. The final zone
        will be created if it doesn't already exist.

        Returns the location of the final zone.
        '''
        if direction not in ZoneStep.OPTIONS:
            raise ValueError('can only join adjacent zones')
        if not self.hasZoneAt(startLocation):
            raise ValueError('zone does not exist')

        endLocation = startLocation + direction
        if not self.hasZoneAt(endLocation):
            self.addZoneAt(endLocation, ownerIndex, dark)
        if direction.yDelta > 0:
            self.zoneConnections[startLocation][direction] = True
        else:
            self.zoneConnections[endLocation][-direction] = True

        if not _bypassSymmetry and self.symmetryEnforced:
            reverseOwner = self._getReverseOwner(ownerIndex)
            self.connectZone(
                ~startLocation, ~direction, reverseOwner, dark,
                _bypassSymmetry=True)

        return startLocation + direction

    def setZoneOwner(self, location, ownerIndex, dark=False):
        '''
        Sets the starting ownership of the given zone to the given team.
        '''
        if location not in self.zoneConnections:
            raise KeyError('no zone at that location')
        self.zoneOwners[location] = (ownerIndex, dark)

    def clearZoneOwner(self, location):
        '''
        Forgets any pre-set starting ownership of this zone, and instead
        uses automatic calculation for this zone.
        '''
        try:
            del self.zoneOwners[location]
        except KeyError:
            pass

    def isConnected(self, location, direction):
        '''
        Checks whether the given zone is connected in the given direction.
        A zone must exist at the given location, but there need not be a
        zone at the end location.
        '''
        if direction not in ZoneStep.OPTIONS:
            raise ValueError('zones are not adjacent')
        if not self.hasZoneAt(location):
            raise ValueError('zone does not exist')

        if direction.yDelta > 0:
            return self.zoneConnections[location][direction]

        endLocation = location + direction
        if not self.hasZoneAt(endLocation):
            return False
        return self.zoneConnections[endLocation][-direction]

    def getConnectedDirections(self, location):
        '''
        Returns all directions which can be directly reached from the zone
        at the given location. The zone must exist.
        '''
        for direction in ZoneStep.OPTIONS:
            if self.isConnected(location, direction):
                yield direction

    def isEverywhereReachable(self):
        '''
        Calculates and returns whether or not every zone in this layout can
        be reached from every other zone.
        '''
        reachable = self.getReachablesFrom(self.firstLocation)
        return len(reachable) == len(self.zoneConnections)

    def getReachablesFrom(self, location):
        '''
        Returns a set of all zone locations that can be reached from the
        zone at the given location (including the zone itself).
        '''
        if not self.hasZoneAt(location):
            raise ValueError('zone not found')
        stack = [location]
        seen = set(stack)
        while stack:
            current = stack.pop(0)
            for direction in self.getConnectedDirections(current):
                target = current + direction
                if target not in seen:
                    seen.add(target)
                    stack.append(target)

        return seen

    def makeEverywhereReachable(self):
        '''
        Opens up zone connections until every zone in this layout can be
        reached by every other zone. If the layout consists of separate
        partitions of zones that are not even adjacent to one another,
        raises a RuntimeError.addZoneAt(a.firstLocation + ZoneStep.NORTHEAST)
        '''
        reachable = self.getReachablesFrom(self.firstLocation)
        if len(reachable) == len(self.zoneConnections):
            return

        options = []
        for location in reachable:
            for direction in ZoneStep.OPTIONS:
                target = location + direction
                if self.hasZoneAt(target) and target not in reachable:
                    options.append((location, direction))

        while len(reachable) < len(self.zoneConnections):
            if not options:
                raise RuntimeError('impossible to connect zones')
            location, direction = random.choice(options)
            partition = self.getReachablesFrom(location + direction)
            if self.symmetryEnforced:
                partition.update(
                    self.getReachablesFrom(~location + ~direction))
            self.connectZone(location, direction)
            reachable.update(partition)
            options = [
                (l, d) for (l, d) in options
                if (l + d) not in partition]
            for location in partition:
                for direction in ZoneStep.OPTIONS:
                    target = location + direction
                    if self.hasZoneAt(target) and target not in reachable:
                        options.append((location, direction))

    def createMapLayout(self, layoutDatabase, autoOwner=True):
        '''
        Creates and returns a MapLayout object that corresponds to this
        layout of zones, using appropriate random map blocks.
        '''
        if len(self.zoneConnections) == 0:
            raise RuntimeError('map is empty')

        it = iter(self.zoneConnections)
        location = next(it)
        xMin = xMax = location.xIndex
        yMin = yMax = location.yIndex
        for location in it:
            xMin = min(xMin, location.xIndex)
            yMin = min(yMin, location.yIndex)
            xMax = max(xMax, location.xIndex)
            yMax = max(yMax, location.yIndex)

        result = MapLayout(
            zonesWide=(xMax - xMin + 1),
            halfZonesHigh=(yMax - yMin + 2),
            startForward=((xMin + yMin) % 2 == 0),
        )

        locations = sorted(
            self.zoneConnections, key=lambda l: (l.xIndex, l.yIndex))
        for location in locations:
            topRow = (location.yIndex - yMin)
            topCol = ((location.xIndex - xMin) * 2 + 1)

            startDark = True
            if location in self.zoneOwners:
                startTeamIndex, startDark = self.zoneOwners[location]
            elif location.xIndex == 0 or not autoOwner:
                startTeamIndex = None
            elif location.xIndex < 0:
                startTeamIndex = 0
            else:
                startTeamIndex = 1

            result.addZone(topRow, topCol, startTeamIndex, startDark)
            if self.isConnected(location, ZoneStep.SOUTH):
                result.blocks[topRow + 1][topCol].blocked = False
                result.blocks[topRow + 2][topCol].blocked = False
            if self.isConnected(location, ZoneStep.SOUTHEAST):
                result.blocks[topRow + 1][topCol + 1].blocked = False
            if self.isConnected(location, ZoneStep.SOUTHWEST):
                result.blocks[topRow + 1][topCol - 1].blocked = False

        if layoutDatabase:
            for row in result.blocks:
                for i, block in enumerate(row):
                    if not (block.zone or block.zone1 or block.zone2):
                        continue

                    if self.symmetryEnforced:
                        if 2 * i > len(row):
                            break
                        opposite = row[len(row) - i - 1]
                    else:
                        opposite = None

                    layoutDatabase.randomiseBlock(block, opposite)

        result.setupComplete()
        return result


class MapLayout(object):
    '''Stores static info about the layout of the map.

    Attributes:
        centreX, centreY: the x and y coordinates of the map centre.
        zones: collection of zoneDefs
        blocks: collection of blockDefs
    '''

    # The dimensions of zones. See diagram below.
    halfZoneHeight = 384        # a / 2
    zoneBodyWidth = 1024        # b
    zoneInterfaceWidth = 512    # c

    # This diagram explains the dimensions defined above.
    #     \___________/ _ _ _ _
    #     /           \       ^
    #    /             \      |
    # __/               \___  a
    #   \               /|    |
    #    \             / |    |
    #     \___________/ _|_ _ v
    #     /|         |\  |
    #      |<-- b -->|<c>|

    def __init__(self, zonesWide, halfZonesHigh, startForward):
        from trosnoth.model.mapblocks import MapBlockDef

        self.serial = 1

        self.cachedTrosballTargetZones = None
        self.worldSize = (
            zonesWide * self.zoneBodyWidth +
                (zonesWide + 1) * self.zoneInterfaceWidth,
            halfZonesHigh * self.halfZoneHeight)

        # Calculate position of centre.
        self.centreX = self.worldSize[0] // 2
        self.centreY = self.worldSize[1] // 2

        # Collection of all zone definitions:
        self.zones = set()

        self.blocks = []

        offset = 0 if startForward else 2
        y = 0
        for i in range(halfZonesHigh):
            row = []
            x = 0
            self.blocks.append(row)
            for j in range(2 * zonesWide + 1):
                index = (offset + 2 * i + j) % 4
                blockType = ('fwd', 'top', 'bck', 'btm')[index]
                row.append(MapBlockDef(blockType, x, y))
                if blockType in ('fwd', 'bck'):
                    x += MapLayout.zoneInterfaceWidth
                else:
                    x += MapLayout.zoneBodyWidth
            y = y + MapLayout.halfZoneHeight

        self.pathFinder = None

    def setupComplete(self, pathFinderFactory=None):
        if pathFinderFactory is None:
            from trosnoth.bots.pathfinding import RunTimePathFinder
            pathFinderFactory = RunTimePathFinder
        self.pathFinder = pathFinderFactory(self)

    def addZone(self, topRow, topCol, startTeamIndex, startDark=True):
        '''
        Adds a zone to this map layout, with its top body block in the given
        row and column of the map block grid.
        '''
        self.serial += 1
        self.cachedTrosballTargetZones = None

        topBlock = self.blocks[topRow][topCol]
        if topBlock.kind != 'top':
            raise IndexError('indices do not refer to a "top" block')
        if topBlock.zone is not None:
            raise IndexError('there is already a zone here')

        x = topBlock.pos[0] + MapLayout.zoneBodyWidth // 2
        y = topBlock.pos[1] + MapLayout.halfZoneHeight
        zone = ZoneDef(len(self.zones), startTeamIndex, x, y, startDark)
        self.zones.add(zone)

        topBlock.zone = zone
        self.blocks[topRow + 1][topCol].zone = zone
        self.blocks[topRow][topCol - 1].zone2 = zone
        self.blocks[topRow + 1][topCol - 1].zone2 = zone
        self.blocks[topRow][topCol + 1].zone1 = zone
        self.blocks[topRow + 1][topCol + 1].zone1 = zone

    def getAdjacentZoneDefs(self, zoneDef):
        if zoneDef.cache_serial != self.serial:
            self._recalculateZoneCache(zoneDef)
        return zoneDef.cached_adjacentZones

    def _recalculateZoneCache(self, zoneDef):
        x, y = zoneDef.pos
        rowIndex, colIndex = self.getMapBlockIndices(x, y - 10)

        zoneDef.cached_adjacentZones = adjacent = set()
        zoneDef.cached_unblockedNeighbours = unblocked = set()
        if rowIndex > 0:
            above = self.blocks[rowIndex - 1][colIndex]
            upleft = self.blocks[rowIndex][colIndex - 1]
            upright = self.blocks[rowIndex][colIndex + 1]
            if above.zone is not None:
                adjacent.add(above.zone)
                if not above.blocked:
                    unblocked.add(above.zone)
            if upleft.zone1 is not None:
                adjacent.add(upleft.zone1)
                if not upleft.blocked:
                    unblocked.add(upleft.zone1)
            if upright.zone2 is not None:
                adjacent.add(upright.zone2)
                if not upright.blocked:
                    unblocked.add(upright.zone2)
        if rowIndex + 2 < len(self.blocks):
            below = self.blocks[rowIndex + 2][colIndex]
            downleft = self.blocks[rowIndex + 1][colIndex - 1]
            downright = self.blocks[rowIndex + 1][colIndex + 1]
            if below.zone is not None:
                adjacent.add(below.zone)
                if not below.blocked:
                    unblocked.add(below.zone)
            if downleft.zone1 is not None:
                adjacent.add(downleft.zone1)
                if not downleft.blocked:
                    unblocked.add(downleft.zone1)
            if downright.zone2 is not None:
                adjacent.add(downright.zone2)
                if not downright.blocked:
                    unblocked.add(downright.zone2)

        zoneDef.cache_serial = self.serial

    def getUnblockedNeighbours(self, zoneDef):
        if zoneDef.cache_serial != self.serial:
            self._recalculateZoneCache(zoneDef)
        return zoneDef.cached_unblockedNeighbours

    def getZoneCount(self):
        return len(self.zones)

    def getTrosballTargetZoneDefn(self, team):
        if team.id == b'A':
            return self.getTrosballTargetZones()[0]
        elif team.id == b'B':
            return self.getTrosballTargetZones()[1]

    def getTrosballTargetZones(self):
        if self.cachedTrosballTargetZones is None:
            self.cachedTrosballTargetZones = [
                min(self.zones, key=lambda z: (-z.pos[0], z.pos[1])),
                min(self.zones, key=lambda z: z.pos),
            ]

        return self.cachedTrosballTargetZones

    def dumpState(self):
        '''
        Serialises this MapLayout into a string that can be sent over the
        network, then reconstructed with fromDumpedState().
        '''
        startForward = (self.blocks[0][0].kind == 'fwd')

        blockInfo = []
        for blockRow in self.blocks:
            row = []
            blockInfo.append(row)
            for block in blockRow:
                if block.layout is None:
                    row.append(None)
                else:
                    row.append(block.layout.key)

        zoneInfo = []
        zones = sorted(self.zones, key=lambda z: z.id)
        for i, zone in enumerate(zones):
            assert i == zone.id
            topRow, topCol = self.getMapBlockIndices(
                zone.pos[0], zone.pos[1] - 10)
            zoneInfo.append([
                zone.initialOwnerIndex, topRow, topCol, zone.initialDarkState])

        return [startForward, blockInfo, zoneInfo]

    @staticmethod
    def unknownBlockKeys(layoutDatabase, data):
        '''
        Goes through a MapLayout's dumpState() representation and checks for
        and returns a collection of map block keys for all map blocks not
        known by the given layoutDatabase.
        '''
        result = set()
        assert isinstance(data, list)
        discard, data, discard = data
        for row in data:
            for key in row:
                if key is not None:
                    fKey = layoutDatabase.getFundamentalKey(key)
                    if fKey is not None:
                        result.add(fKey)

        return result

    @staticmethod
    def fromDumpedState(layoutDatabase, data):
        '''
        Reconstructs a MapLayout from its dumpState() result. Assumes that all
        map block definitions are available in the LayoutDatabase given.
        '''
        assert isinstance(data, list)
        startForward, blockData, zoneData = data
        halfZonesHigh = len(blockData)
        zonesWide = (len(blockData[0]) - 1) // 2

        result = MapLayout(zonesWide, halfZonesHigh, startForward)
        for i, row in enumerate(blockData):
            for j, key in enumerate(row):
                if key is not None:
                    layout = layoutDatabase.getLayoutByKey(key)
                    layout.applyTo(result.blocks[i][j])

        assert len(result.zones) == 0
        for zoneInfo in zoneData:
            initialOwnerIndex, topRow, topCol, initialDarkState = zoneInfo
            result.addZone(topRow, topCol, initialOwnerIndex, initialDarkState)

        result.setupComplete()
        return result

    @staticmethod
    def fromFile(layoutDatabase, filename):
        mapDir = getPath(user, 'maps')
        filename = os.path.join(mapDir, filename)
        if not os.path.exists(filename):
            raise IOError("Map could not be loaded; it doesn't exist!")

        with open(filename, 'rU') as f:
            layoutStr = f.read()

        return MapLayout.fromDumpedState(layoutDatabase, unrepr(layoutStr))

    @staticmethod
    def getMapBlockIndices(xCoord, yCoord):
        '''Returns the index in Universe.zoneBlocks of the map block which the
        given x and y-coordinates belong to.
        (0, 0) is the top-left corner.

        To find a zone, use MapBlock.getZoneAtPoint()'''

        blockY = int(yCoord // MapLayout.halfZoneHeight)

        blockX, remainder = divmod(
            xCoord, MapLayout.zoneBodyWidth + MapLayout.zoneInterfaceWidth)
        if remainder >= MapLayout.zoneInterfaceWidth:
            blockX = int(2 * blockX + 1)
        else:
            blockX = int(2 * blockX)

        return blockY, blockX

    def getCandidatePolygons(self, x0, y0, x1, y1):
        for blockDef in self.getBlockDefsInBounds(x0, y0, x1, y1):
            if blockDef.layout is None:
                continue
            if blockDef.layout.reversed:
                offset = blockDef.rect.topright
            else:
                offset = blockDef.rect.topleft
            yield from maptree.getRelevantLeaves(
                blockDef.layout.newLayout.tree, offset,
                blockDef.layout.reversed, x0, y0, x1, y1)

    def getBlockDefsInBounds(self, x0, y0, x1, y1):
        '''
        Returns an iterator of the blocks in the given rect.
        '''
        i, j0 = self.getMapBlockIndices(x0, y0)
        j0 = max(0, j0)
        i = max(0, i)

        while i < len(self.blocks):
            row = self.blocks[i]
            j = j0
            while j < len(row):
                block = row[j]
                blockLeft, blockTop = block.pos
                if blockTop >= y1:
                    return
                if blockLeft >= x1:
                    break
                yield block
                j += 1
            i += 1


class MapState(object):
    '''Stores dynamic info about the layout of the map including who owns what
    zone.

    Attributes:
        layout - the static MapLayout
        zones - a set of zones
        blocks - a set of blocks
        zoneWithId - mapping from zone id to zone
    '''

    def __init__(self, universe, layout):
        self.layout = layout

        self.zones = set()
        self.zoneWithDef = {}
        for zone in self.layout.zones:
            newZone = ZoneState(universe, zone)

            self.zones.add(newZone)
            self.zoneWithDef[zone] = newZone

        self.zoneWithId = {}
        for zone in self.zones:
            self.zoneWithId[zone.id] = zone

        self.zoneBlocks = []
        for row in self.layout.blocks:
            newRow = []
            for blockDef in row:
                newRow.append(blockDef.spawnState(universe, self.zoneWithDef))
            self.zoneBlocks.append(newRow)

    def getMapBlockAtPoint(self, pos):
        i, j = MapLayout.getMapBlockIndices(*pos)
        if i < 0 or j < 0:
            raise IndexError
        return self.zoneBlocks[i][j]

    def getZoneAtPoint(self, pos):
        try:
            return self.getMapBlockAtPoint(pos).getZoneAtPoint(*pos)
        except IndexError:
            return None

    def isInMap(self, pos):
        i, j = MapLayout.getMapBlockIndices(*pos)
        if i < 0 or j < 0:
            return False
        if i >= len(self.zoneBlocks) or j >= len(self.zoneBlocks[0]):
            return False
        return True
