import logging

from trosnoth.model.map import MapLayout
from trosnoth.model.utils import Rect

log = logging.getLogger(__name__)


class MapBlockDef(object):
    '''Represents the static information about a particular map block. A map
    block is a grid square, and may contain a single zone, or the interface
    between two zones.'''

    def __init__(self, kind, x, y):
        self.pos = (x, y)       # Pos is the top-left corner of this block.
        assert kind in ('top', 'btm', 'fwd', 'bck')
        self.kind = kind
        self.layout = None

        self.indices = MapLayout.getMapBlockIndices(x, y)

        self.rect = Rect(x, y, 0, 0)
        self.rect.size = self.getSize(kind)

        self.graphics = None
        self.blocked = True     # There's a barrier somewhere depending on type

        # For body block.
        self.zone = None

        # For interface block.
        self.zone1 = None
        self.zone2 = None

    def __repr__(self):
        return 'MapBlockDef(%r @ %r)' % (self.kind, self.indices)

    def __str__(self):
        return 'Block @ %r' % (self.indices,)

    @staticmethod
    def getSize(kind):
        height = MapLayout.halfZoneHeight
        width = (
            MapLayout.zoneBodyWidth if kind in ('top', 'btm')
            else MapLayout.zoneInterfaceWidth)
        return (width, height)

    def spawnState(self, universe, zoneWithDef):
        if self.kind == 'top':
            return TopBodyMapBlock(
                universe, self, zoneWithDef.get(self.zone, None))
        elif self.kind == 'btm':
            return BottomBodyMapBlock(
                universe, self, zoneWithDef.get(self.zone, None))
        elif self.kind == 'fwd':
            return ForwardInterfaceMapBlock(
                universe, self,
                zoneWithDef.get(self.zone1, None),
                zoneWithDef.get(self.zone2, None))
        elif self.kind == 'bck':
            return BackwardInterfaceMapBlock(
                universe, self,
                zoneWithDef.get(self.zone1, None),
                zoneWithDef.get(self.zone2, None))
        else:
            assert False

    def getZones(self):
        result = []
        for z in (self.zone, self.zone1, self.zone2):
            if z is not None:
                result.append(z)
        return result

    def getZoneAtPoint(self, x, y):
        '''getZoneAtPoint(x, y)
        Returns the zone def for the zone at the specified point, ASSUMING
        that the point is in fact within this map block.'''
        if self.kind == 'fwd':
            # Equation of interface line:
            #   (y - self.y) = -(halfZoneHeight / interfaceWidth)(x - self.x)
            #                        + halfZoneHeight
            deltaY = y - self.pos[1] - MapLayout.halfZoneHeight
            deltaX = x - self.pos[0]

            if (deltaY * MapLayout.zoneInterfaceWidth >
                    -MapLayout.halfZoneHeight * deltaX):
                return self.zone2
            return self.zone1
        elif self.kind == 'bck':
            # Equation of interface line:
            #   (y - self.y) = (halfZoneHeight / interfaceWidth)(x - self.x)
            deltaY = y - self.pos[1]
            deltaX = x - self.pos[0]

            if (deltaY * MapLayout.zoneInterfaceWidth >
                    MapLayout.halfZoneHeight * deltaX):
                return self.zone1
            return self.zone2
        else:
            return self.zone


class MapBlock(object):
    '''
    Represents a grid square of the map which may contain a single zone,
    or the interface between two zones.
    '''

    def __init__(self, universe, defn):
        self.universe = universe
        self.defn = defn

    def __contains__(self, point):
        '''Checks whether a given point is within this zone.'''
        return self.defn.rect.collidepoint(*point)

    def _getBlockLeft(self):
        try:
            i, j = self.defn.indices
            if j == 0:
                return None
            return self.universe.zoneBlocks[i][j - 1]
        except IndexError:
            return None
    blockLeft = property(_getBlockLeft)

    def _getBlockRight(self):
        try:
            i, j = self.defn.indices
            if j >= len(self.universe.zoneBlocks[i]) - 1:
                return None
            return self.universe.zoneBlocks[i][j + 1]
        except IndexError:
            return None
    blockRight = property(_getBlockRight)

    def _getBlockAbove(self):
        try:
            i, j = self.defn.indices
            if i == 0:
                return None
            return self.universe.zoneBlocks[i - 1][j]
        except IndexError:
            return None
    blockAbove = property(_getBlockAbove)

    def _getBlockBelow(self):
        try:
            i, j = self.defn.indices
            if i >= len(self.universe.zoneBlocks) - 1:
                return None
            return self.universe.zoneBlocks[i + 1][j]
        except IndexError:
            return None
    blockBelow = property(_getBlockBelow)

    def getZoneAtPoint(self, x, y):
        '''getZoneAtPoint(x, y)
        Returns what zone is at the specified point, ASSUMING that the point
        is in fact within this map block.'''
        raise NotImplementedError('getZoneAtPoint not implemented.')

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is'''
        return


class BodyMapBlock(MapBlock):
    '''Represents a map block which contains only a single zone.'''

    def __init__(self, universe, defn, zone):
        super(BodyMapBlock, self).__init__(universe, defn)
        self.zone = zone

    def __str__(self):
        return '< %s >' % self.zone

    def getZoneAtPoint(self, x, y):
        return self.zone

    def getZones(self):
        if self.zone is not None:
            yield self.zone


class TopBodyMapBlock(BodyMapBlock):
    '''Represents a map block containing the top half of a zone.'''

    def orbPos(self, drawRect):
        return drawRect.midbottom

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is'''

        return min(
            abs(player.pos[1] - self.defn.rect.top),
            self.blockLeft.fromEdge(player),
            self.blockRight.fromEdge(player))


class BottomBodyMapBlock(BodyMapBlock):
    '''Represents a map block containing the bottom half of a zone.'''

    def orbPos(self, drawRect):
        return drawRect.midtop

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is'''

        return min(
            abs(self.defn.rect.bottom - player.pos[1]),
            self.blockLeft.fromEdge(player),
            self.blockRight.fromEdge(player))


class InterfaceMapBlock(MapBlock):
    '''Base class for map blocks which contain the interface between two
    zones.'''

    def __init__(self, universe, defn, zone1, zone2):
        super(InterfaceMapBlock, self).__init__(universe, defn)

        self.zone1 = zone1
        self.zone2 = zone2

    def getZones(self):
        if self.zone1 is not None:
            yield self.zone1
        if self.zone2 is not None:
            yield self.zone2


class ForwardInterfaceMapBlock(InterfaceMapBlock):
    '''Represents a map block which contains the interface between two
    zones, split in the direction of a forward slash '/'.
    Note that exactly on the diagonal counts as being in the left-hand zone.
    '''

    def __str__(self):
        return '< %s / %s >' % (self.zone1, self.zone2)

    def getZoneAtPoint(self, x, y):
        # Equation of interface line:
        #   (y - self.y) = -(halfZoneHeight / interfaceWidth)(x - self.x)
        #                        + halfZoneHeight
        deltaY = y - self.defn.pos[1] - MapLayout.halfZoneHeight
        deltaX = x - self.defn.pos[0]

        if (deltaY * MapLayout.zoneInterfaceWidth > -MapLayout.halfZoneHeight *
                deltaX):
            return self.zone2
        return self.zone1

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is.
        Assumes that the player is actually in this map block.'''
        relPos = (
            self.defn.rect.left - player.pos[0],
            self.defn.rect.top - player.pos[1])

        # Note: this following formula relies upon the dimensions:
        # MapLayout.halfZoneHeight = 384
        # MapLayout.zoneInterfaceWidth = 512
        # Should they be changed, should change this to:
        # d = sin(theta) * abs(relPos[1] + relPos[0] *
        # MapLayout.halfZoneHeight / MapLayout.zoneInterfaceWidth + 384)
        # (where theta is the angle formed by the diagonal line separating the
        # zones, and a vertical line).
        d = 0.8 * abs(relPos[1] + relPos[0] * 0.75 + 384)
        return d


class BackwardInterfaceMapBlock(InterfaceMapBlock):
    '''Represents a map block which contains the interface between two
    zones, split in the direction of a backslash '\'.
    Note that a point exactly on the diagonal counts as being in the left-hand
    zone.
    '''

    def __str__(self):
        return '< %s \ %s >' % (self.zone1, self.zone2)

    def getZoneAtPoint(self, x, y):
        # Equation of interface line:
        #   (y - self.y) = (halfZoneHeight / interfaceWidth)(x - self.x)
        deltaY = y - self.defn.pos[1]
        deltaX = x - self.defn.pos[0]

        if (
                deltaY * MapLayout.zoneInterfaceWidth >
                MapLayout.halfZoneHeight * deltaX):
            return self.zone1
        return self.zone2

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is.
        Assumes that the player is actually in this map block.'''
        relPos = (
            self.defn.rect.left - player.pos[0],
            self.defn.rect.top - player.pos[1])

        # Note: this following formula relies upon the dimensions:
        # MapLayout.halfZoneHeight = 384
        # MapLayout.zoneInterfaceWidth = 512
        # Should they be changed, should change this to:
        # d = sin(theta) * abs(relPos[1] - relPos[0] *
        # MapLayout.halfZoneHeight / MapLayout.zoneInterfaceWidth)
        # where theta is the angle formed by the diagonal line separating the
        # zones, and a vertical line.
        d = 0.8 * abs(relPos[1] - relPos[0] * 3 / 4)
        return d
