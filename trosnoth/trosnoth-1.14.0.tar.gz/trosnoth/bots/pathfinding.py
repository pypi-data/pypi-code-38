if __name__ == '__main__':
    # Just to make sure the correct one is imported if this is run directly
    import os, sys
    sys.path.insert(
        0, os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', '..'))

import functools
import heapq
import io
import logging
from math import pi, ceil, sin, cos, floor
import os
import pickle
import random
from typing import TypeVar, Callable, Iterable, Tuple, Any, List

from trosnoth import data
from trosnoth.const import (
    PATH_FINDING_DISCRETISATION_UNIT,
    ZONE_CAP_DISTANCE,
)
from trosnoth.model.map import MapLayout
from trosnoth.model.mapblocks import MapBlockDef
from trosnoth.model.mapLayout import LayoutDatabase
from trosnoth.model.player import Player, PlayerInputState
from trosnoth.model.universe import Universe
from trosnoth.model.utils import Rect
from trosnoth.utils.math import distance, isNear

log = logging.getLogger(__name__)


# When this flag is on, extra path-finding debugging is recorded
DEBUG = False


PATHFINDING_FILENAME = data.getPath(data, 'edges.db')
DISCRETISATION_FILENAME = data.getPath(data, 'points.db')

NORTH = 'n'
SOUTH = 's'
EAST = 'e'
WEST = 'w'
ORB = 'o'
MULTIPLE = 'm'
DIRECTIONS = {NORTH, SOUTH, EAST, WEST}

WAYPOINTS = {
    'btmBlockedBasic.block': [
        ((-98, -38), {NORTH, WEST}),
        ((98, -38), {NORTH, EAST}),
        ((0, -28), {NORTH}),
        ((-125, 28), {WEST}),
        ((125, 28), {EAST}),
    ],
    'btmOpenBasic.block': [
        ((-28, -24), {NORTH, WEST}),
        ((28, -24), {NORTH, EAST}),
        ((-115, 34), {SOUTH, WEST}),
        ((115, 34), {SOUTH, EAST}),
    ],
    'topBlockedEmpty.block': [
        ((-96, 36), {SOUTH, WEST}),
        ((96, 36), {SOUTH, EAST}),
        ((-119, -28), {WEST}),
        ((119, -28), {EAST}),
    ],
    'topOpenPlatforms.block': [
        ((-84, -15), {NORTH, WEST}),
        ((84, -15), {NORTH, EAST}),
        ((-96, 36), {SOUTH, WEST}),
        ((96, 36), {SOUTH, EAST}),
        ((0, 10), {SOUTH}),
    ],
    'bckBlockedIslands.block': [
        ((-50, -9), {WEST}),
        ((-18, 19), {SOUTH}),
        ((-27, -26), {NORTH}),
        ((50, -13), {EAST}),
    ],
    'fwdOpenRectangles.block': [
        ((28, -19), {NORTH, EAST}),
        ((49, 34), {SOUTH, EAST}),
        ((-41, 28), {SOUTH, WEST}),
        ((-59, -2), {WEST}),
        ((-31, -19), {NORTH}),
    ],
    'topBlockedPurple.block': [
        ((0, 32), {SOUTH}),
        ((-98, 39), {SOUTH, WEST}),
        ((98, 39), {SOUTH, EAST}),
        ((-108, -24), {WEST}),
        ((108, -24), {EAST}),
    ],
    'topBlockedCurves.block': [
        ((-32, 38), {SOUTH}),
        ((32, 38), {SOUTH}),
        ((110, 4), {SOUTH, EAST}),
        ((-110, 4), {SOUTH, WEST}),
    ],
    'bckOpenTetris.block': [
        ((38, -26), {NORTH, EAST}),
        ((-38, -26), {NORTH, WEST}),
        ((-48, 14), {SOUTH, WEST}),
        ((-26, 34), {SOUTH}),
        ((59, -5), {EAST}),
    ],
    'topOpenPokemon.block': [
        ((114, 3), {SOUTH, EAST}),
        ((-114, 3), {SOUTH, WEST}),
        ((32, 38), {SOUTH}),
        ((-32, 38), {SOUTH}),
        ((89, -29), {NORTH}),
        ((-89, -29), {NORTH}),
    ],
    'btmBlockedHumps.block': [
        ((98, -41), {NORTH, EAST}),
        ((-98, -41), {NORTH, WEST}),
        ((18, -39), {NORTH}),
        ((-18, -39), {NORTH}),
        ((99, 3), {EAST}),
        ((-99, 3), {WEST}),
    ],
    'btmOpenMario.block': [
        ((64, 38), {SOUTH}),
        ((-64, 38), {SOUTH}),
        ((17, -38), {NORTH}),
        ((-17, -38), {NORTH}),
        ((100, 3), {EAST}),
        ((-100, 3), {WEST}),
    ],
    'bckOpenEmpty.block': [
        ((-13, -1), {NORTH, EAST, WEST}),
        ((51, 33), {SOUTH, EAST}),
    ],
    'fwdOpenLadder.block': [
        ((19, -40), {NORTH}),
        ((14, 7), {SOUTH}),
        ((-59, 28), {WEST, SOUTH}),
        ((50, 30), {SOUTH, EAST}),
    ],
    'btmOpenCaves.block': [
        ((105, -31), {NORTH, EAST}),
        ((116, 31), {SOUTH, EAST}),
        ((64, 36), {SOUTH}),
        ((-78, 36), {SOUTH}),
        ((-125, 28), {WEST}),
        ((-103, -39), {NORTH}),
        ((0, -42), {NORTH}),
    ],
    'btmBlockedAliens.block': [
        ((12, -32), {NORTH}),
        ((-12, -32), {NORTH}),
        ((105, -20), {NORTH, EAST}),
        ((-105, -20), {NORTH, WEST}),
        ((125, 28), {EAST}),
        ((-125, 28), {WEST}),
    ],
}
DIRECTIONS_BY_WAYPOINT = {
    (regionName, waypoint): directions
    for regionName, waypoints in WAYPOINTS.items()
    for waypoint, directions in waypoints
}

EDGES_KEY = 'edges'
NODES_KEY = 'nodes'
KEY_KEY = 'key'
TARGETS_KEY = 'targets'
SCORES_KEY = 'scores'
SOURCE_KEY = 'source'
COST_KEY = 'cost'
ACTIONS_KEY = 'actions'
TARGET_MAP_BLOCK_KEY = 'targetMapBlock'
TARGET_KEY = 'target'
TRANSITIONS_KEY = 'transitions'

OPPOSITE_DIRECTION = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST: WEST,
    WEST: EAST,
}
HORIZONTAL_OPPOSITE = {
    NORTH: NORTH,
    SOUTH: SOUTH,
    EAST: WEST,
    WEST: EAST,
}

ADJACENT_KINDS = {
    'top': {
        NORTH: 'btm',
        SOUTH: 'btm',
        EAST: 'bck',
        WEST: 'fwd',
    },
    'btm': {
        NORTH: 'top',
        SOUTH: 'top',
        EAST: 'fwd',
        WEST: 'bck',
    },
    'fwd': {
        NORTH: 'bck',
        SOUTH: 'bck',
        EAST: 'top',
        WEST: 'btm',
    },
    'bck': {
        NORTH: 'fwd',
        SOUTH: 'fwd',
        EAST: 'btm',
        WEST: 'top',
    },
}

REVERSED = {'top': 'top', 'btm': 'btm', 'fwd': 'bck', 'bck': 'fwd'}

COLLISION_POINT_TEST_DISTANCE = PATH_FINDING_DISCRETISATION_UNIT * 0.6
MIN_EDGES_PER_LOC_KEY = 15
MIN_REGION_EXITS_PER_DIRECTION = 30
NEARBY_ROUTE_BOX_WIDTH = 20
NEARBY_ROUTE_BOX_HEIGHT = 40


class NoStationaryPointHere(Exception):
    pass


class ActionKindCollection(object):
    def __init__(self):
        self.store = {}

    def register(self, cls):
        key = cls.__name__
        if key in self.store:
            raise KeyError('Another %s already registered', key)
        self.store[key] = cls
        return cls

    def getByString(self, key):
        return self.store[key]

    def actionKindToString(self, actionKind):
        key = actionKind.__name__
        assert self.store[key] == actionKind
        return key


actionKindClasses = ActionKindCollection()


class PathFindingAction(object):
    '''
    Represents a possible action for player path-finding.
    '''
    def __init__(self, *args):
        self._args = args
        self.failed = False
        self.init(*args)

    def __repr__(self):
        return '{}({})'.format(
            type(self).__name__, ', '.join(repr(a) for a in self._args))

    def init(self, *args):
        pass

    def run(self, player):
        raise NotImplementedError('{}.run'.format(type(self).__name__))

    def encode(self):
        return (actionKindClasses.actionKindToString(type(self)), self._args)

    def reverse(self):
        raise NotImplementedError('{}.reverse'.format(type(self).__name__))

    @staticmethod
    def decode(encodedAction):
        kind, args = encodedAction
        cls = actionKindClasses.getByString(kind)
        return cls(*args)

    @staticmethod
    def decodeGroup(encodedActions, flipped):
        actions = [PathFindingAction.decode(a) for a in encodedActions]
        if flipped:
            actions = [action.reverse() for action in actions]
        return actions

    def faceRight(self, player):
        if player.isFacingRight():
            return player.angleFacing
        return pi / 2

    def faceLeft(self, player):
        if not player.isFacingRight():
            return player.angleFacing
        return -pi / 2


@actionKindClasses.register
class Wait(PathFindingAction):
    def init(self, ticks):
        self.ticks = ticks

    def reverse(self):
        return self

    def run(self, player):
        for _ in range(self.ticks):
            yield PlayerInputState(angle=player.angleFacing)


@actionKindClasses.register
class FallDown(PathFindingAction):
    def reverse(self):
        return self

    def run(self, player):
        while not player.isStationary():
            yield PlayerInputState(angle=player.angleFacing)


@actionKindClasses.register
class FallLeft(PathFindingAction):
    def init(self, ticks):
        self.ticks = ticks

    def reverse(self):
        return FallRight(self.ticks)

    def run(self, player):
        ticks = self.ticks
        while ticks > 0:
            ticks -= 1
            yield PlayerInputState(angle=self.faceLeft(player), left=True)
            if player.isStationary():
                return
        while not player.isStationary():
            yield PlayerInputState(angle=self.faceLeft(player))


@actionKindClasses.register
class FallRight(PathFindingAction):
    def init(self, ticks):
        self.ticks = ticks

    def reverse(self):
        return FallLeft(self.ticks)

    def run(self, player):
        ticks = self.ticks
        while ticks > 0:
            ticks -= 1
            yield PlayerInputState(angle=self.faceRight(player), right=True)
            if player.isStationary():
                return
        while not player.isStationary():
            yield PlayerInputState(angle=self.faceRight(player))


@actionKindClasses.register
class Grapple(PathFindingAction):
    def init(self, angle, ticks):
        self.angle = angle
        self.ticks = ticks

    def reverse(self):
        return Grapple(-self.angle, self.ticks)

    def run(self, player):
        inputState = PlayerInputState(angle=self.angle, hook=True, jump=True)
        yield inputState

        while not player.grapplingHook.isAttached():
            if player.isStationary() or not player.grapplingHook.isActive():
                self.failed = True
                return
            yield inputState

        ticks = self.ticks
        lastPos = player.pos
        while ticks > 0:
            ticks -= 1
            if player.isStationary():
                return
            yield inputState
            if isNear(distance(player.pos, lastPos), 0):
                break
            lastPos = player.pos


@actionKindClasses.register
class Drop(PathFindingAction):
    def reverse(self):
        return self

    def run(self, player):
        yield PlayerInputState(angle=player.angleFacing, drop=True)


@actionKindClasses.register
class JumpUp(PathFindingAction):
    def reverse(self):
        return self

    def run(self, player):
        while True:
            yield PlayerInputState(angle=player.angleFacing, jump=True)
            if player.yVel >= 0:
                return


@actionKindClasses.register
class JumpLeft(PathFindingAction):
    def reverse(self):
        return JumpRight()

    def run(self, player):
        while True:
            yield PlayerInputState(
                angle=self.faceLeft(player), jump=True, left=True)
            if player.yVel >= 0:
                return


@actionKindClasses.register
class JumpRight(PathFindingAction):
    def reverse(self):
        return JumpLeft()

    def run(self, player):
        while True:
            yield PlayerInputState(
                angle=self.faceRight(player), jump=True, right=True)
            if player.yVel >= 0:
                return


@actionKindClasses.register
class MoveLeft(PathFindingAction):
    def init(self, ticks):
        self.ticks = ticks

    def reverse(self):
        return MoveRight(self.ticks)

    def run(self, player):
        ticks = self.ticks
        while ticks > 0:
            ticks -= 1
            yield PlayerInputState(angle=self.faceLeft(player), left=True)
            if player.isStationary():
                return
        while player.getGroundCollision() and not player.isStationary():
            yield PlayerInputState(angle=self.faceLeft(player))


@actionKindClasses.register
class MoveRight(PathFindingAction):
    def init(self, ticks):
        self.ticks = ticks

    def reverse(self):
        return MoveLeft(self.ticks)

    def run(self, player):
        ticks = self.ticks
        while ticks > 0:
            ticks -= 1
            yield PlayerInputState(angle=self.faceRight(player), right=True)
            if player.isStationary():
                return
        while player.getGroundCollision() and not player.isStationary():
            yield PlayerInputState(angle=self.faceRight(player))


@actionKindClasses.register
class SlowStepLeft(PathFindingAction):
    def init(self, ticks):
        self.ticks = ticks

    def reverse(self):
        return SlowStepRight(self.ticks)

    def run(self, player):
        ticks = self.ticks
        while ticks > 0:
            ticks -= 1
            yield PlayerInputState(angle=self.faceRight(player), left=True)
            if player.isStationary():
                return
        while player.getGroundCollision() and not player.isStationary():
            yield PlayerInputState(angle=self.faceRight(player))


@actionKindClasses.register
class SlowStepRight(PathFindingAction):
    def init(self, ticks):
        self.ticks = ticks

    def reverse(self):
        return SlowStepLeft(self.ticks)

    def run(self, player):
        ticks = self.ticks
        while ticks > 0:
            ticks -= 1
            yield PlayerInputState(angle=self.faceLeft(player), right=True)
            if player.isStationary():
                return
        while player.getGroundCollision() and not player.isStationary():
            yield PlayerInputState(angle=self.faceLeft(player))


def buildWorldAndBlockDefForSingleLayout(
        layout, layoutDb=None, pathFinderFactory=None):
    '''
    Creates a dummy world containing the given map block layout for simulation.

    :return: (world, blockDef)
    '''
    if layoutDb is None:
        layoutDb = LayoutDatabase()

    world = Universe(layoutDb)
    mapLayout = MapLayout(3, 4, False)

    if layout.kind in ('fwd', 'bck'):
        i, j = 2, 1
    else:
        mapLayout.addZone(1, 1, 0)
        if layout.kind == 'top':
            i, j = 1, 1
        else:
            i, j = 1, 2

    block = mapLayout.blocks[j][i]
    layout.applyTo(block)
    mapLayout.setupComplete(pathFinderFactory=pathFinderFactory)
    world.setLayout(mapLayout)

    return world, block


def shiftIndices(indices, direction):
    '''
    :param indices: the map block indices in the same order that they're
        used to index mapLayout.blocks (i.e., (row index, column index))
    :param direction: the direction to move
    :return: the indices of the map block in the given direction from the
        original indices
    '''
    j, i = indices
    if direction == NORTH:
        j -= 1
    elif direction == SOUTH:
        j += 1
    elif direction == EAST:
        i += 1
    else:
        if direction != WEST:
            raise ValueError('unknown direction {!r}'.format(direction))
        i -= 1
    return j, i


def buildWorldAndBlockDefsForLayoutCombination(
        startLayout, endLayout, direction, layoutDb=None,
        pathFinderFactory=None):
    if layoutDb is None:
        layoutDb = LayoutDatabase()

    world, startBlockDef = buildWorldAndBlockDefForSingleLayout(
        startLayout, layoutDb, pathFinderFactory)

    if startLayout.kind in ('fwd', 'bck'):
        i, j = 2, 1
    elif startLayout.kind == 'top':
        i, j = 1, 1
    else:
        i, j = 1, 2

    j, i = shiftIndices((j, i), direction)

    endBlockDef = world.map.layout.blocks[j][i]
    endLayout.applyTo(endBlockDef)
    world.map.layout.setupComplete(pathFinderFactory=pathFinderFactory)

    return world, startBlockDef, endBlockDef


class PathFindingStoreBuilder(object):
    def __init__(self):
        self.discretisationDatabase = DiscretisationDatabase.get()
        self.pathFindingDatabase = PathFindingDatabase.get()

        self.regions = {os.path.basename(layout.filename): layout
            for layout in LayoutDatabase(custom=False).allLayouts()}

        self.pendingInternalTransitionRegions = set()
        self.pendingInterRegionPairs = set()
        self.currentRegion = None
        self.pendingPoints = None

    def buildPathFinder(self, mapLayout):
        return BuildTimePathFinder(self, mapLayout)

    def build(self):
        try:
            log.info('First pass: calculating discretisation points...')
            for regionName in self.regions:
                log.info('  %s', regionName)
                self.calculateDiscretisationLocations(regionName)

            log.info('Second pass: calculating transitions and way costs...')
            self.pendingInternalTransitionRegions = set(self.regions)
            self.pendingInterRegionPairs = self.allRegionCombos()

            while True:
                while self.pendingInternalTransitionRegions:
                    regionName = self.pendingInternalTransitionRegions.pop()
                    log.info(
                        '  %s: calculating internal transitions...',
                        regionName)
                    self.calculateSingleRegionTransitions(regionName)
                    log.info(
                        '  %s: pruning edges...', regionName)
                    self.pruneInternalEdges(regionName)
                    log.info(
                        '  %s: calculating travel costs...', regionName)
                    self.calculateWayCosts(regionName)

                self.currentRegion = None
                if self.pendingInterRegionPairs:
                    combo = self.pendingInterRegionPairs.pop()
                    log.info('  %s: calculating combination...', combo)
                    self.calculateTwoRegionTransitions(combo)
                elif not self.pendingInternalTransitionRegions:
                    break

            log.info('Third pass: pruning combination edges...')
            for combo in self.allRegionCombos():
                log.info('  %s', combo)
                self.pruneCombinationEdges(combo)

            log.info('Fourth pass: calculating navigation costs...')
            self.calculateComboNavigationCosts()

            log.info('Fifth pass: checking and filling nearby routes...')
            for regionName in self.regions:
                log.info('  %s', regionName)
                self.checkPrefilledRoutes(regionName)
        finally:
            self.save()

    def profileBuild(self):
        import cProfile
        from trosnoth.utils.profiling import KCacheGrindOutputter

        prof = cProfile.Profile()
        try:
            prof.runcall(self.build)
        finally:
            kg = KCacheGrindOutputter(prof)
            with open('pathfinding.log', 'w') as f:
                kg.output(f)

    def shell(self):
        sys.stderr.flush()
        print('Starting interactive shell...')
        import code
        local = {'builder': self, 'db': self.pathFindingDatabase}
        local.update(actionKindClasses.store)
        code.interact(local=local)

    def save(self):
        if self.discretisationDatabase.dirty:
            self.discretisationDatabase.save()
        if self.pathFindingDatabase.dirty:
            self.pathFindingDatabase.save()

    def dropRegion(self, regionName):
        '''
        Drops all data related to the given region and its combinations.
        '''
        self.discretisationDatabase.dropRegion(regionName)
        self.pathFindingDatabase.getRegion(regionName).drop()
        for direction in DIRECTIONS:
            for combo in self.getRegionCombosFrom(regionName, direction):
                combo.drop()

    def allRegionCombos(self):
        '''
        Returns a set of all valid combinations of regions in self.regions.
        '''
        result = set()

        for regionName in self.regions:
            for direction in DIRECTIONS:
                for combo in self.getRegionCombosFrom(regionName, direction):
                    result.add(combo)
        return result

    def getRegionCombosFrom(self, regionName, direction):
        '''
        Iterates through all valid region combos that transition in the
        given direction from the given region (not mirrored).
        '''
        for halfCombo in self.getHalfCombosFrom(regionName, direction):
            yield halfCombo.getCanonicalCombo()

    def getHalfCombosFrom(self, regionName, direction):
        startLayout = self.regions[regionName]
        startKind = startLayout.kind
        endKind = ADJACENT_KINDS[startKind][direction]
        if startLayout.newLayout.blocked:
            if (startKind, direction) == ('top', NORTH):
                return
            if (startKind, direction) == ('btm', SOUTH):
                return

        for layout2 in self.regions.values():
            for endLayout in {layout2, layout2.mirrorLayout}:
                kind = REVERSED[
                    endLayout.kind] if endLayout.reversed else endLayout.kind
                if kind != endKind:
                    continue
                if endLayout.newLayout.blocked:
                    if (endKind, direction) == ('top', SOUTH):
                        continue
                    if (endKind, direction) == ('btm', NORTH):
                        continue

                yield self.pathFindingDatabase.getHalfCombo(
                    startLayout, layout2, False,
                    endLayout.reversed, direction)

    def getCombo(self, name1, name2, rev1, rev2, direction):
        return self.pathFindingDatabase.getHalfCombo(
            self.regions[name1], self.regions[name2],
            rev1, rev2, direction).getCanonicalCombo()

    def calculateDiscretisationLocations(self, regionName):
        db = self.discretisationDatabase
        if db.isRegionFullyBuilt(regionName):
            log.info('    already cached.')
            return
        log.info('    calculating discretisation locations...')

        layout = self.regions[regionName]
        world, block = buildWorldAndBlockDefForSingleLayout(layout)

        test_dist = COLLISION_POINT_TEST_DISTANCE

        symmetrical = self.regionIsSymmetrical(regionName)
        width, height = block.rect.size
        x0, y0 = block.rect.center
        n = ceil(width / 2 / PATH_FINDING_DISCRETISATION_UNIT)
        m = ceil(height / 2 / PATH_FINDING_DISCRETISATION_UNIT)
        lowerBound = 0 if symmetrical else -n
        for i in range(lowerBound, n + 1):
            self.printProgressBar(i - lowerBound, n + 1 - lowerBound)
            x = i * PATH_FINDING_DISCRETISATION_UNIT
            centralMirror = (i == 0) and symmetrical
            for j in range(-m, m + 1):
                y = j * PATH_FINDING_DISCRETISATION_UNIT
                centre = (x0 + x, y0 + y)

                if not any(world.layout.getCandidatePolygons(
                        centre[0] - test_dist - Player.HALF_WIDTH,
                        centre[1] - test_dist - Player.HALF_HEIGHT,
                        centre[0] + test_dist + Player.HALF_WIDTH,
                        centre[1] + test_dist + Player.HALF_HEIGHT)):
                    continue

                if centralMirror:
                    self.findSymmetricalCollisionPoint(
                        regionName, world, block, centre)
                else:
                    self.findCollisionPoint(regionName, world, block, centre)
        self.printProgressBar(1, 1)

        log.info(
            '      %s stationary points',
            db.getLocationCount(regionName, raw=True))
        db.markRegionAsFullyBuilt(regionName)

    def findCollisionPoint(self, regionName, world, block, centre):
        x0, y0 = block.rect.center
        player = Player(world, 'PathFinding', None, None, bot=True)
        test_dist = COLLISION_POINT_TEST_DISTANCE

        tried = succeeded = 0
        boundary = False
        while tried < 15 and succeeded < 5:
            tried += 1
            angle = random.random() * 2 * pi
            delta = self.getDeltaOnSquare(angle, test_dist)
            player.pos = centre

            collision = world.physics.getCollision(player, delta)
            if not collision:
                continue
            if collision.travelDistance < 0.055:
                break
            if not block.rect.collidepoint(collision.end):
                continue

            offset = (collision.end[0] - x0, collision.end[1] - y0)
            if self.collisionPointIsBorderline(offset):
                boundary = True
                continue
            self.addCollisionPoint(regionName, offset, collision.angle)
            succeeded += 1

        while tried < 30 and succeeded < 7:
            tried += 1
            angle = random.random() * 2 * pi
            delta = self.getDeltaOnSquare(angle, test_dist)
            player.pos = (centre[0] - delta[0], centre[1] - delta[1])

            collision = world.physics.getCollision(player, delta)
            if not collision:
                continue
            if collision.travelDistance < 0.055:
                continue
            if not block.rect.collidepoint(collision.end):
                continue

            offset = (collision.end[0] - x0, collision.end[1] - y0)
            if self.collisionPointIsBorderline(offset):
                boundary = True
                continue
            self.addCollisionPoint(regionName, offset, collision.angle)
            succeeded += 1

        if boundary and not succeeded:
            raise Exception(
                'Discrete point is on boundary and is susceptible to '
                'floating point rounding errors: {}: {}'.format(
                    regionName, (centre[0] - x0, centre[1] - y0)))

    def findSymmetricalCollisionPoint(self, regionName, world, block, centre):
        x0, y0 = block.rect.center
        player = Player(world, 'PathFinding', None, None, bot=True)
        test_dist = COLLISION_POINT_TEST_DISTANCE
        boundary = False
        succeeded = False

        for angle in (-pi / 2, pi / 2):
            delta = self.getDeltaOnSquare(angle, test_dist)
            player.pos = centre

            collision = world.physics.getCollision(player, delta)
            if not collision:
                continue
            if collision.travelDistance < 0.055:
                break
            if not block.rect.collidepoint(collision.end):
                continue

            offset = (0, collision.end[1] - y0)
            if self.collisionPointIsBorderline(offset):
                boundary = True
                continue
            self.addCollisionPoint(regionName, offset, collision.angle)
            succeeded = True

        for angle in (-pi / 2, pi / 2):
            angle = random.random() * 2 * pi
            delta = self.getDeltaOnSquare(angle, test_dist)
            player.pos = (centre[0] - delta[0], centre[1] - delta[1])

            collision = world.physics.getCollision(player, delta)
            if not collision:
                continue
            if collision.travelDistance < 0.055:
                continue
            if not block.rect.collidepoint(collision.end):
                continue

            offset = (0, collision.end[1] - y0)
            if self.collisionPointIsBorderline(offset):
                boundary = True
                continue
            self.addCollisionPoint(regionName, offset, collision.angle)
            succeeded = True

        if boundary and not succeeded:
            raise Exception(
                'Discrete point is on boundary and is susceptible to '
                'floating point rounding errors: {}: {}'.format(
                    regionName, (centre[0] - x0, centre[1] - y0)))

    def collisionPointIsBorderline(self, offset):
        '''
        :return: True iff the given offset is very close to a boundary
            between locKey indices, and therefore could be susceptible to
            floating point rounding errors.
        '''
        x, y = offset
        locKey = DiscretisationDatabase.getLocKey(offset)
        for dx, dy in [(0, 1e-5), (0, -1e-5), (1e-5, 0), (-1e-5, 0)]:
            if DiscretisationDatabase.getLocKey((x + dx, y + dy)) != locKey:
                return True
        return False

    def addCollisionPoint(self, regionName, offset, angle):
        region = self.pathFindingDatabase.getRegion(regionName)

        self.discretisationDatabase.addLocation(regionName, offset, angle)
        locKey = self.discretisationDatabase.getLocKey(offset)
        try:
            direction = region.isBorderPoint(locKey)
        except NoStationaryPointHere:
            return

        if direction is None:
            if regionName == self.currentRegion:
                self.pendingPoints.add(locKey)
            else:
                self.pendingInternalTransitionRegions.add(regionName)
        elif direction != MULTIPLE:
            if regionName != self.currentRegion:
                self.pendingInterRegionPairs.update(
                    self.getRegionCombosFrom(regionName, direction))

    def regionIsSymmetrical(self, regionName):
        layout = self.regions[regionName]
        return layout is layout.mirrorLayout

    @staticmethod
    def getDeltaOnSquare(angle, d):
        sinTheta, cosTheta = sin(angle), cos(angle)
        if abs(sinTheta) > abs(cosTheta):
            if sinTheta > 0:
                return (d * cosTheta / sinTheta, d)
            else:
                return (-d * cosTheta / sinTheta, -d)
        elif cosTheta > 0:
            return (d, d * sinTheta / cosTheta)
        else:
            return (-d, -d * sinTheta / cosTheta)

    def calculateSingleRegionTransitions(self, regionName):
        region = self.pathFindingDatabase.getRegion(regionName)
        self.currentRegion = regionName
        regionPoints = set(region.getNonBorderLocKeys(raw=True))
        examinedPoints = set(region.getAlreadyExaminedLocKeys())
        if examinedPoints - regionPoints:
            raise RuntimeError(
                'Region {} contains invalid points. Drop region to '
                'recalculate.'.format(regionName))

        self.pendingPoints = regionPoints - examinedPoints
        if not self.pendingPoints:
            log.info('    already cached.')
            return

        layout = self.regions[regionName]
        world, block = buildWorldAndBlockDefForSingleLayout(
            layout, pathFinderFactory=self.buildPathFinder)
        total = 0

        initial = len(self.pendingPoints)
        while self.pendingPoints:
            self.printProgressBar(initial - len(self.pendingPoints), initial)

            locKey = self.pendingPoints.pop()
            if region.isBorderPoint(locKey):
                continue
            count = 0
            for i in range(10):
                count += self.expandTransitions(
                    world, block, regionName, locKey)
                if count > 0:
                    break
            total += count
            region.markLocKeyAsExamined(locKey)
        self.printProgressBar(initial, initial)

        log.info('    %s new internal edges', total)

    def calculateTransitionsFromSinglePoint(self, regionName, locKey):
        '''For debugging.'''
        world, block = buildWorldAndBlockDefForSingleLayout(
            self.regions[regionName], pathFinderFactory=self.buildPathFinder)
        count = self.expandTransitions(world, block, regionName, locKey)
        log.info('%s new edges', count)
        return count

    def setupComboWorld(self, combo):
        layout1 = self.regions[combo.name1]
        if combo.flip1:
            layout1 = layout1.mirrorLayout
        layout2 = self.regions[combo.name2]
        if combo.flip2:
            layout2 = layout2.mirrorLayout
        return buildWorldAndBlockDefsForLayoutCombination(
            layout1, layout2, combo.direction,
            pathFinderFactory=self.buildPathFinder)

    def calculateTwoRegionTransitions(self, combo):
        queue = list(self.getNewComboEdges(combo))
        if not queue:
            log.info('    already cached.')
            return

        world, block0, block1 = self.setupComboWorld(combo)
        total = len(queue)
        added = 0
        for i, (point, path, flipPath) in enumerate(queue):
            self.printProgressBar(i, total)
            for j in range(5):
                count = self.expandTwoRegionTransition(
                    combo, world, block0, block1, point, path, flipPath)
                if count:
                    break
            added += count
            combo.markPointAsExamined(point)

        self.printProgressBar(total, total)
        log.info('    %s new transition edges', added)

    def getNewComboEdges(self, combo):
        '''
        Iterates through (point, path, flipPath) tuples for all starting points
        that aren't yet in the database for this PathFindingRegionCombination.
        This includes edges from the adjacent regions, as well as border
        points.
        '''

        # Start with exit points from neighbouring regions
        inward = combo.getExpectedInwardTransitions()
        points = set(inward)

        # Add all points really close the this boundary
        for index in (0, 1):
            region = combo.getRegion(index)
            direction = combo.getDirectionRelativeToRegion(index)
            for locKey in self.discretisationDatabase.getAllLocKeys(
                    region.name):
                if region.isBorderPoint(locKey) == direction:
                    points.add((index, locKey))

        # If any points in the database shouldn't be there, then probably all
        # the data for the region combination is invalid.
        examinedPoints = combo.getExaminedPoints()
        if examinedPoints - points:
            raise RuntimeError(
                'Invalid points in {}. Drop combo to recalculate.'.format(
                    combo))

        # Yield the remaining (point, path) combinations
        for point in points - examinedPoints:
            if point in inward:
                for path, flipPath in inward[point]:
                    yield point, path, flipPath
            else:
                yield point, (), False

    def printProgressBar(self, iteration, total, width=70, fill='#'):
        if total == 0:
            percent = '100.0'
            filledLength = width
        else:
            percent = '{:.1f}'.format(min(100, 100 * iteration / total))
            filledLength = min(width, int(width * iteration // total))
        bar = fill * filledLength + '-' * (width - filledLength)
        print('\r[%s] %s%% ' % (bar, percent), end='')
        if iteration >= total:
            print(flush=True)

    def expandTransitions(self, world, block, regionName, locKey):
        region = self.pathFindingDatabase.getRegion(regionName)
        x0, y0 = block.rect.center
        offset, angle = self.discretisationDatabase.getDiscretisationLocationByKey(
            regionName, locKey)

        player = Player(world, 'PathFinding', None, None, bot=True)
        player.setDiscreteLocation((x0 + offset[0], y0 + offset[1]), angle)
        pending = self.buildStartQueue(player)

        count = 0
        processor = OneBlockActionProcessor(
            region, locKey, block.rect,
            functools.partial(self.addDepartingEdge, region),
        )

        for ticks, path, endKey, _ in processor.run(pending):
            count += 1
            self.checkAndAddInternalEdge(
                region, world, block, locKey, endKey, ticks, path)
        return count

    def addInternalTransition(self, regionName, locKey, actions):
        '''
        Useful for manually adding transitions to the database in order to
        try to reach a location which didn't become reachable by the random
        transitions during general database building.
        '''
        region = self.pathFindingDatabase.getRegion(regionName)
        world, block = buildWorldAndBlockDefForSingleLayout(
            self.regions[regionName], pathFinderFactory=self.buildPathFinder)
        x0, y0 = block.rect.center
        offset, angle = self.discretisationDatabase.getDiscretisationLocationByKey(
            regionName, locKey)

        player = Player(world, 'PathFinding', None, None, bot=True)
        player.setDiscreteLocation((x0 + offset[0], y0 + offset[1]), angle)

        processor = OneBlockActionProcessor(
            region, locKey, block.rect, lambda *a, **kw: None)
        totalTicks = 0
        fullPath = ()
        for action in actions:
            player, ticks, path, pointData = processor.runSingleAction(
                player, action)
            endKey, endData = processor.checkFinalPosition(player, pointData)
            totalTicks += ticks
            fullPath += path

        if not player.isStationary():
            raise RuntimeError('final point is not stationary')

        endKey, endData = processor.checkFinalPosition(player, pointData)
        if endKey is None:
            raise RuntimeError('ended up back at start!')
        log.info('Resulting point: %r', endKey)
        self.checkAndAddInternalEdge(
            region, world, block, locKey, endKey, totalTicks, fullPath)

    def checkAndAddInternalEdge(
            self, region, world, block, locKey, endKey, totalTicks, fullPath):
        if region.symmetrical:
            # Check if this edge will hit a physics corner case when reflected
            x0, y0 = block.rect.center
            i, j = locKey
            ddb = self.discretisationDatabase
            offset, angle = ddb.getDiscretisationLocationByKey(
                region.name, (-i, j))

            player = Player(world, 'PathFinding', None, None, bot=True)
            player.setDiscreteLocation(
                (x0 + offset[0], y0 + offset[1]), angle)

            total = 0
            actions = PathFindingAction.decodeGroup(fullPath, True)
            for action in actions:
                for inputState in action.run(player):
                    player.setInputState(inputState)
                    player.advance()
                    if player.movementProhibited:
                        log.warning('Edge motion did not match mirror')
                        return
                    total += 1
            if not player.isStationary():
                log.warning(
                    'Mirror edge motion did not end at stationary point')
                return
            if total != totalTicks:
                log.warning('Edge motion duration did not match mirror')
                return
            x, y = player.pos
            u1, v1 = endKey
            u2, v2 = ddb.getLocKey((x - x0, y - y0))
            if not isNear(u1, -u2) or not isNear(v1, v2):
                log.warning('Edge final position did not match mirror')
                return

        region.addInternalEdge(locKey, endKey, totalTicks, fullPath)

    def addDepartingEdge(self, region, locKey, path, direction):
        region.addDepartingEdge(locKey, path, direction)
        self.pendingInterRegionPairs.update(
            self.getRegionCombosFrom(region.name, direction))

    def buildStartQueue(self, player):
        result = [
            (0, (), player, JumpUp(), 0),
            (0, (), player, JumpLeft(), 0),
            (0, (), player, JumpRight(), 0),
            (0, (), player, Drop(), 0),
            (0, (), player, SlowStepLeft(1), 0),
            (0, (), player, SlowStepRight(1), 0),
            (0, (), player, Grapple((random.random() - 0.5) * pi, 5), 0),
            (0, (), player, Grapple((random.random() - 0.5) * pi, 10), 0),
        ]
        for ticks in (1, 2, 3, 5, 8, 13, 21, 34, 55):
            result.append((0, (), player, MoveLeft(ticks), 0))
            result.append((0, (), player, MoveRight(ticks), 0))
        return result

    def plotAction(self, regionName, locKey, actions):
        '''For debugging.'''
        region = self.pathFindingDatabase.getRegion(regionName)
        layout = self.regions[regionName]
        world, block = buildWorldAndBlockDefForSingleLayout(
            layout, pathFinderFactory=self.buildPathFinder)

        x0, y0 = block.rect.center
        offset, angle = self.discretisationDatabase.getDiscretisationLocationByKey(
                regionName, locKey)

        player = Player(world, 'PathFinding', None, None, bot=True)
        player.setDiscreteLocation((x0 + offset[0], y0 + offset[1]), angle)

        processor = PlotterActionProcessor(block.rect)
        pts = processor.plotActions(player, actions)
        region.plot(extra=pts)

    def plotComboAction(self, combo, point, actions):
        '''For debugging.'''
        world, block0, block1 = self.setupComboWorld(combo)
        index, locKey = point
        block = block1 if index else block0
        offset, angle = self.discretisationDatabase.getDiscretisationLocationByKey(
            combo.getRegionName(index), locKey)
        startPos, angle = getAbsolutePosAndAngle(block, offset, angle)

        player = Player(world, 'PathFinding', None, None, bot=True)
        player.setDiscreteLocation(startPos, angle)

        processor = ComboPlotterActionProcessor(combo, block0, block1, point)
        pts = processor.plotActions(player, actions)
        combo.plot(extra=pts)

    def expandTwoRegionTransition(
            self, combo, world, block0, block1, point, initialPath, flipPath):
        # Create and place the simulated player
        index, locKey = point
        block = block1 if index else block0
        offset, angle = self.discretisationDatabase.getDiscretisationLocationByKey(
            combo.getRegionName(index), locKey)
        startPos, angle = getAbsolutePosAndAngle(block, offset, angle)

        player = Player(world, 'PathFinding', None, None, bot=True)
        player.setDiscreteLocation(startPos, angle)

        # Simulate everything up to the action that leaves the first region
        startActions = PathFindingAction.decodeGroup(
            initialPath, flipPath ^ block.layout.reversed)
        path = ()
        ticks = 0
        while len(startActions) > 1:
            action = startActions.pop(0)
            path = path + (action.encode(),)
            for inputState in action.run(player):
                player.setInputState(inputState)
                player.advance()
                ticks += 1
                if player.movementProhibited:
                    return 0

        # Simulate further possible actions
        count = 0
        if startActions:
            pending = [(ticks, path, player, startActions.pop(0), ticks)]
        else:
            pending = self.buildStartQueue(player)
        for ticks, path, endPoint, initialCost in TwoBlockActionProcessor(
                combo, block0, block1, point).run(pending):
            combo.addEdge(point, ticks, path, endPoint, initialCost)
            count += 1
        return count

    def tryNewComboEdges(self, combo, startPoint):
        '''
        Useful if a combo point doesn't have any outgoing edges. Tries to
        find new routes out of here.
        '''
        world, block0, block1 = self.setupComboWorld(combo)
        added = 0
        for i in range(10):
            added += self.expandTwoRegionTransition(
                combo, world, block0, block1, startPoint, [], False)
        return added

    def prefillRemainingRoutes(self, regionName):
        region = self.pathFindingDatabase.getRegion(regionName)
        i0, i1, j0, j1 = region.getNearbyRouteIndexBounds()
        knownRouteIndices = region.getAllIndicesWithNearbyRoutes()
        count = 0
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                try:
                    region.getNearbyRouteByIndices((i, j))
                except KeyError:
                    count += 1
                    dist = min(
                        distance(indices, (i, j))
                        for indices in knownRouteIndices)
                    choice = random.choice([
                        indices for indices in knownRouteIndices
                        if isNear(distance(indices, (i, j)), dist)])
                    region.copyNearbyRoute(choice, (i, j))
        log.info('    filled %s new nearby routes', count)

    def checkPrefilledRoutes(self, regionName):
        region = self.pathFindingDatabase.getRegion(regionName)
        i0, i1, j0, j1 = region.getNearbyRouteIndexBounds()

        failed = set()
        someSucceeded = False
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                try:
                    startLocKey, path, routeFlipped = \
                        region.getNearbyRouteByIndices((i, j))
                except KeyError:
                    continue

                if routeFlipped:
                    startLocKey = (-startLocKey[0], startLocKey[1])
                if not region.pointIsReachable(startLocKey):
                    # There is no path to this locKey
                    failed.add((i, j))
                else:
                    someSucceeded = True

        if not someSucceeded:
            log.info('    no inward routes! Not pruning prefilled routes.')
        elif failed:
            for i, j in failed:
                region.forgetNearbyRoute((i, j))
            log.info('    pruned %s nearby routes', len(failed))
            self.rerunAllEdgesForNearbyRoutes(region)
        else:
            log.info('    all nearby routes are valid')
        self.prefillRemainingRoutes(regionName)

    def rerunAllEdgesForNearbyRoutes(self, region):
        layout = self.regions[region.name]
        world, block = buildWorldAndBlockDefForSingleLayout(
            layout, pathFinderFactory=self.buildPathFinder)
        x0, y0 = block.rect.center

        edges = list(region.getInternalEdges())
        total = len(edges)
        for i, (startKey, endKey, ticks, path, flipPath) in enumerate(edges):
            self.printProgressBar(i, total)
            if not region.pointIsReachable(startKey):
                # No path to this locKey, so don't bother trying it
                continue

            offset, angle = self.discretisationDatabase.getDiscretisationLocationByKey(
                region.name, startKey)
            player = Player(world, 'PathFinding', None, None, bot=True)
            player.setDiscreteLocation(
                (x0 + offset[0], y0 + offset[1]), angle)

            actions = PathFindingAction.decodeGroup(path, flipPath)
            ticks = 0
            points = []
            while actions:
                action = actions.pop(0)
                for inputState in action.run(player):
                    points.append(player.pos)
                    player.setInputState(inputState)
                    player.advance()
                    offset = (player.pos[0] - x0, player.pos[1] - y0)
                    region.addNearbyRoute(
                        offset, startKey, ticks, path, flipPath)
                    ticks += 1
                    assert not player.movementProhibited

            locKey = DiscretisationDatabase.getLocKey(offset)
            assert locKey == endKey
        self.printProgressBar(total, total)

    def pruneInternalEdges(self, regionName):
        # We want to reduce the number of edges in the database, but we
        # don't want to stop a locKey from being reachable in the process
        region = self.pathFindingDatabase.getRegion(regionName)
        edges = list(region.getInternalEdges(raw=True))

        while edges:
            i = random.randrange(len(edges))
            startKey, endKey, ticks, path, flipPath = edges.pop(i)
            if len(list(region.getOutwardEdges(
                    startKey))) <= MIN_EDGES_PER_LOC_KEY:
                continue
            if len(list(region.getInwardEdges(
                    endKey))) <= MIN_EDGES_PER_LOC_KEY:
                continue
            region.removeEdge(startKey, endKey, ticks, path, flipPath)

        # Also prune number of routes to orb
        routes = list(region.getOrbRoutes())
        while len(routes) > MIN_EDGES_PER_LOC_KEY:
            i = random.randrange(len(routes))
            region.removeOrbRoute(routes.pop(i))

    def pruneCombinationEdges(self, combo):
        # The aim of this phase is to reduce the number of edges needed to
        # get between regions. In the first pass, region combinations
        # generate hundreds of combination edges, but really we only need,
        # say, 30 different ways to get between each pair of neighbouring
        # regions.
        inwardCount = [0, 0]
        outwardCount = [0, 0]

        # First take note of how many edges leave each region
        edges = list(combo.getEdges())
        for startPoint, endPoint, *_ in edges:
            if not combo.isBorderPoint(startPoint):
                outwardCount[startPoint[0]] += 1
            if not combo.isBorderPoint(endPoint):
                inwardCount[endPoint[0]] += 1

        # Then prune any that we can afford to prune
        count = 0
        while edges:
            i = random.randrange(len(edges))
            startPoint, endPoint, ticks, path = edges.pop(i)

            borderStart = combo.isBorderPoint(startPoint)
            borderEnd = combo.isBorderPoint(endPoint)

            if borderStart:
                if len(combo.getOutwardEdges(startPoint)) <= MIN_EDGES_PER_LOC_KEY:
                    continue
            elif outwardCount[startPoint[0]] <= MIN_REGION_EXITS_PER_DIRECTION:
                continue

            if borderEnd:
                if len(combo.getInwardEdges(endPoint)) <= MIN_EDGES_PER_LOC_KEY:
                    continue
            elif inwardCount[endPoint[0]] <= MIN_REGION_EXITS_PER_DIRECTION:
                continue

            combo.removeEdge(startPoint, endPoint, ticks, path)
            if not borderStart:
                outwardCount[startPoint[0]] -= 1
            if not borderEnd:
                inwardCount[endPoint[0]] -= 1
            count += 1

        log.info('    pruned %s edges', count)

    def calculateComboNavigationCosts(self):
        for combo in self.allRegionCombos():
            combo.clearCosts()
            log.info('    %s: edges', combo)
            self.calculateComboEdgeCosts(combo)
            log.info('    %s: waypoint transitions', combo)
            self.calculateComboWaypointTransitionCosts(combo)

    def calculateWayCosts(self, regionName):
        region = self.pathFindingDatabase.getRegion(regionName)
        region.clearCosts()

        self.checkWaypoints(regionName)
        self.calculateCostsFromWaypoints(regionName)
        self.calculateCostsToWaypoints(regionName)

    def checkWaypoints(self, regionName):
        ddb = self.discretisationDatabase
        seenDirections = set()
        # Check that defined waypoints are stationary points
        for locKey, directions in WAYPOINTS.get(regionName, ()):
            try:
                ddb.getDiscretisationLocationByKey(regionName, locKey)
            except NoStationaryPointHere:
                raise Exception(
                    'Waypoint {} for {} is not a stationary point'.format(
                        locKey, regionName))
            seenDirections.update(directions)

        # Check that the waypoints defined for this region cover all the
        # directions you should be able to enter and exit from
        region = self.pathFindingDatabase.getRegion(regionName)
        layout = region.getLayout()
        expectedDirections = DIRECTIONS
        if layout.newLayout.blocked:
            if layout.kind == 'top':
                expectedDirections = {SOUTH, EAST, WEST}
            elif layout.kind == 'btm':
                expectedDirections = {NORTH, EAST, WEST}

        if expectedDirections - seenDirections:
            raise Exception('{} should have waypoints for {}'.format(
                regionName, ', '.join(expectedDirections - seenDirections)))
        if seenDirections - expectedDirections:
            raise Exception('{} should not have waypoints for {}'.format(
                regionName, ', '.join(seenDirections - expectedDirections)))

    def calculateCostsToWaypoints(self, regionName):
        region = self.pathFindingDatabase.getRegion(regionName)

        def visitVertex(vertex, cost):
            region.setCostToWaypoint(vertex, waypoint, cost)

        def expandVertex(vertex):
            for ticks, startKey, *_ in region.getInwardEdges(vertex):
                yield ticks, None, startKey

        for waypoint, directions in WAYPOINTS[regionName]:
            exhaustiveDijkstra(visitVertex, expandVertex, [(waypoint, 0)])

        self.checkAllPointsCanReachWaypoints(region)
        self.checkAllWaypointsConnectCorrectly(region)

    def checkAllPointsCanReachWaypoints(self, region):
        for locKey in self.discretisationDatabase.getAllLocKeys(region.name):
            if region.isBorderPoint(locKey):
                continue
            if not region.pointCanReachWaypoints(locKey):
                raise Exception(
                    '{region}: {locKey} cannot reach any waypoints\n'
                    'To visualise, use db.getRegion({region!r}).plot().\n'
                    'To fix this, either edit the layout of the region and '
                    'call builder.dropRegion({region!r}) before '
                    'rebuilding the db, or use builder.plotAction({region!r}, '
                    '{locKey}, <actions>) to find a set of actions, then '
                    'record it using builder.addInternalTransition() and '
                    'db.save().'.format(
                        region=region.name,
                        locKey=locKey))

    def checkAllWaypointsConnectCorrectly(self, region):
        # After we're using hexagonal rooms as regions (instead of
        # rectangular map blocks), we won't need partitions - every waypoint
        # in a region should then be able to reach every other waypoint.
        partitions = []
        layout = region.getLayout()
        if layout.kind == 'bck' and layout.newLayout.blocked:
            partitions = [{NORTH, EAST}, {SOUTH, WEST}]
        elif layout.kind == 'fwd' and layout.newLayout.blocked:
            partitions = [{NORTH, WEST}, {SOUTH, EAST}]
        else:
            partitions = [DIRECTIONS]

        for partition in partitions:
            waypoints = {
                wp for wp, dirs in WAYPOINTS[region.name]
                if partition.intersection(dirs)}

            for waypoint in waypoints:
                costs = region.getCostsToWaypoints(waypoint)
                if not all(wp in costs for wp in waypoints):
                    raise Exception(
                        '{}: waypoint {} cannot reach all other waypoints in '
                        'its partition'.format(region.name, waypoint))

    def calculateCostsFromWaypoints(self, regionName):
        region = self.pathFindingDatabase.getRegion(regionName)

        def visitVertex(vertex, cost):
            region.setCostFromWaypoint(vertex, waypoint, cost)

        def expandVertex(vertex):
            for ticks, endKey, path, flipPath in region.getOutwardEdges(
                    vertex):
                yield ticks, None, endKey

        for waypoint, directions in WAYPOINTS[regionName]:
            exhaustiveDijkstra(visitVertex, expandVertex, [(waypoint, 0)])

    def calculateComboEdgeCosts(self, combo):

        def buildOutwardStartData():
            for point in combo.getEdgeStartPoints():
                index, locKey = point
                if combo.isBorderPoint(point) or index != waypointIndex:
                    continue
                wayCosts = combo.getRegion(index).getCostsFromWaypoints(locKey)
                if waypoint not in wayCosts:
                    continue
                yield point, wayCosts[waypoint]

        def buildInwardStartData():
            for point in combo.getEdgeEndPoints():
                index, locKey = point
                if combo.isBorderPoint(point) or index != waypointIndex:
                    continue
                wayCosts = combo.getRegion(index).getCostsToWaypoints(locKey)
                if waypoint not in wayCosts:
                    continue
                yield point, wayCosts[waypoint]

        def actsAsBorderPoint(vertex):
            if combo.isBorderPoint(vertex):
                return True

            # Point couldn't previously reach any waypoints, so perhaps it
            # can now as part of the combo.
            index, locKey = vertex
            if not combo.getRegion(index).pointCanReachWaypoints(locKey):
                return True

            return False

        def outwardVisit(vertex, cost):
            if actsAsBorderPoint(vertex):
                combo.setCostFromWaypoint(
                    vertex, (waypointIndex, waypoint), cost)

        def inwardVisit(vertex, cost):
            if actsAsBorderPoint(vertex):
                combo.setCostToWaypoint(
                    vertex, (waypointIndex, waypoint), cost)

        def outwardExpand(vertex):
            for cost, point, actions in combo.getOutwardEdges(vertex):
                if not actsAsBorderPoint(point):
                    continue
                yield cost, None, point

        def inwardExpand(vertex):
            for cost, point, actions in combo.getInwardEdges(vertex):
                if not actsAsBorderPoint(point):
                    continue
                yield cost, None, point

        for waypointIndex in 0, 1:
            for waypoint, _ in WAYPOINTS[combo.getRegionName(waypointIndex)]:
                exhaustiveDijkstra(
                    outwardVisit, outwardExpand, buildOutwardStartData())
                exhaustiveDijkstra(
                    inwardVisit, inwardExpand, buildInwardStartData())

        # Double check that every point can reach a waypoint - the
        # path-finding algorithm used at run-time relies on this.
        for cIndex in 0, 1:
            for cLocKey in self.discretisationDatabase.getAllLocKeys(
                    combo.getRegionName(cIndex)):
                if combo.isBorderPoint((cIndex, cLocKey)) and not \
                        combo.getCostsToWaypoints((cIndex, cLocKey)):
                    raise Exception(
                        '{}: Border point {} cannot reach any '
                        'waypoints. Consider using tryNewComboEdges() '
                        'to rectify.'.format(combo, (cIndex, cLocKey)))

    def calculateComboWaypointTransitionCosts(self, combo):
        for index in (0, 1):
            region = combo.getRegion(index)
            direction = combo.getDirectionRelativeToRegion(index)
            for waypoint, directions in WAYPOINTS[region.name]:
                if direction not in directions:
                    continue
                self.calculateSingleWaypointTransitionCosts(
                    combo, (index, waypoint))

    def calculateSingleWaypointTransitionCosts(self, combo, waypoint):
        '''
        Fills in all transitions costs needed in order for a path to be
        followed from the given waypoint to the closest waypoint in the
        other half of the given combo.
        '''
        otherWaypoint = self.findClosestTransitionWaypoint(combo, waypoint)
        costs = self.findPossibleCostsForWaypointTransition(
            combo, waypoint, otherWaypoint)

        self.fillNecessaryCostsForWaypointTransition(
            combo, waypoint, otherWaypoint, costs)

        # Record the cost in the other direction too, so we can do a two-way A*
        cost = combo.getCostsToWaypoints(waypoint)[otherWaypoint]
        combo.setCostFromWaypoint(otherWaypoint, waypoint, cost)

    def findClosestTransitionWaypoint(self, combo, waypoint):
        result = []
        targetIndex = not waypoint[0]
        targets = {
            (targetIndex, locKey)
            for locKey, _ in WAYPOINTS[combo.getRegionName(targetIndex)]}

        def buildStartData():
            for point0, point1, ticks, _ in combo.getEdges():
                wayCosts = combo.getCostsFromWaypoints(point0)
                if waypoint not in wayCosts:
                    # Edge end can't be reached by this waypoint
                    continue
                if point1[0] == waypoint[0]:
                    # End ends in starting region
                    continue
                yield point1, wayCosts[waypoint] + ticks

        def visit(vertex, cost):
            if vertex in targets:
                result.append(vertex)
                raise StopIteration()

        def expand(vertex):
            for cost, point, _ in combo.getOutwardEdges(vertex):
                if point[0] == waypoint[0]:
                    # Back in the starting region
                    continue
                yield cost, None, point

            index, locKey = vertex
            if index != waypoint[0]:
                for cost, endKey, *_ in combo.getRegion(
                        index).getOutwardEdges(locKey):
                    yield cost, None, (index, endKey)

        exhaustiveDijkstra(visit, expand, buildStartData())
        if not result:
            raise Exception(
                '{}: no transition path found from {} to another '
                'waypoint'.format(combo, waypoint))
        return result[0]

    def findPossibleCostsForWaypointTransition(self, combo, src, dest):
        '''
        Uses Dijkstra's algorithm to find the cost to get to dest for all
        points that are both in the same half of the combo as src,
        and are closer to dest than src is.
        '''
        srcIndex, srcLocKey = src
        result = {}

        def buildStartData():
            for point0, point1, ticks, _ in combo.getEdges():
                wayCosts = combo.getCostsToWaypoints(point1)
                if dest not in wayCosts:
                    # Edge end can't reach this waypoint
                    continue
                if point0[0] != srcIndex:
                    # End starts in wrong region
                    continue
                yield point0, wayCosts[dest] + ticks

        def visit(vertex, cost):
            index, locKey = vertex
            result[locKey] = cost
            if vertex == src:
                raise StopIteration()

        def expand(vertex):
            for cost, point, _ in combo.getInwardEdges(vertex):
                if point[0] != srcIndex:
                    # Not in the correct region
                    continue
                yield cost, None, point

            index, locKey = vertex
            if index == srcIndex:
                for cost, startKey, *_ in combo.getRegion(
                        index).getInwardEdges(locKey):
                    yield cost, None, (index, startKey)

        exhaustiveDijkstra(visit, expand, buildStartData())
        return result

    def fillNecessaryCostsForWaypointTransition(self, combo, src, dest, costs):
        '''
        Uses the costs calculated by findPossibleCostsForWaypointTransition
        and saves them in the combo, but only if they can be reached in a
        downhill walk from src.
        '''
        index, srcLocKey = src
        region = combo.getRegion(index)

        pending = [srcLocKey]
        seen = set(pending)
        while pending:
            locKey = pending.pop(0)
            combo.setCostToWaypoint((index, locKey), dest, costs[locKey])
            for _, endKey, *_ in region.getOutwardEdges(locKey):
                if endKey in seen or endKey not in costs:
                    continue
                if costs[locKey] <= costs[endKey]:
                    continue
                pending.append(endKey)
                seen.add(endKey)


class ActionQueueProcessor:
    identification = None

    def run(self, pending):
        byEndKey = {}

        while pending:
            ticks, path, player, action, pointData = pending.pop(0)
            player, ticks, path, pointData = self.runSingleAction(
                player, action, ticks, path, pointData)
            if not player:
                continue

            if player.isStationary():
                endKey, endData = self.checkFinalPosition(player, pointData)
                if endKey is None:
                    continue
                if endKey not in byEndKey:
                    byEndKey[endKey] = (ticks, path, endData)
                else:
                    oldTicks, oldPath, oldData = byEndKey[endKey]
                    if ticks < oldTicks:
                        byEndKey[endKey] = (ticks, path, endData)
            else:
                options = [FallDown(), FallLeft(5), FallRight(5)]
                # Don't chain multiple grapples
                if not any(record[0] == Grapple.__name__ for record in path):
                    options.append(Grapple((random.random() - 0.5) * pi, 5))
                    options.append(Grapple((random.random() - 0.5) * pi, 10))

                for nextPoint in options:
                    pending.append((ticks, path, player, nextPoint, pointData))

        for endKey, (ticks, path, endData) in byEndKey.items():
            yield ticks, path, endKey, endData

    def runSingleAction(
            self, player, action, ticks=0, path=(), pointData=None):
        path = path + (action.encode(),)
        player = player.clone()
        pointData = self.simulationStarted(path, player, action, pointData)

        hook = player.getGrapplingHook()
        lastInputState = None
        lastPos = None
        lastHookPos = None
        staticTicks = 0
        for inputState in action.run(player):
            hookPos = hook.pos if hook.isActive() else None
            if inputState == lastInputState and isNear(
                    distance(player.pos, lastPos), 0) and (
                    lastHookPos is None is hookPos or
                    (lastHookPos is not None and hookPos is not None and
                     isNear(distance(hookPos, lastHookPos), 0))):
                staticTicks += 1
                if staticTicks >= 15:
                    # If this ever happens, it's probably worth putting
                    # a breakpoint here and commenting out the
                    # return line, to figure out what's going on.
                    log.error('Infinite action: %s', type(action).__name__)
                    log.error('  start: %s', self.identification)
                    log.error('  path: %s', path)
                    pointData = self.simulationFinished(
                        pointData, success=False)
                    return None, ticks, path, pointData
            else:
                staticTicks = 0
            lastInputState = inputState
            lastPos = player.pos
            lastHookPos = hookPos

            player.setInputState(inputState)
            player.advance()
            ticks += 1
            if player.movementProhibited:
                pointData = self.simulationFinished(pointData, success=False)
                return None, ticks, path, pointData
            if self.playerHasLeftBlock(player, path, ticks):
                pointData = self.simulationFinished(pointData, success=False)
                return None, ticks, path, pointData
            pointData = self.simulationAdvanced(
                path, player, action, ticks, pointData)
        pointData = self.simulationFinished(
            pointData, success=not action.failed)
        if action.failed:
            player = None
        return player, ticks, path, pointData

    def simulationStarted(self, path, player, action, pointData):
        return pointData

    def simulationAdvanced(self, path, player, action, ticks, pointData):
        return pointData

    def simulationFinished(self, pointData, *, success):
        return pointData

    def playerHasLeftBlock(self, player, path, ticks):
        raise NotImplementedError('playerHasLeftBlock')

    def checkFinalPosition(self, player, pointData):
        raise NotImplementedError('checkFinalPosition')


class OneBlockActionProcessor(ActionQueueProcessor):
    def __init__(
            self, region, locKey, regionRect, departingEdgeCallback):
        self.region = region
        self.locKey = locKey
        self.regionRect = regionRect
        self.addDepartingEdge = departingEdgeCallback
        self.identification = '{}@{}'.format(
            region.name if region else '?', locKey)

    def checkFinalPosition(self, player, pointData):
        x0, y0 = self.regionRect.center
        x, y = player.pos
        locKey = DiscretisationDatabase.getLocKey((x - x0, y - y0))
        if locKey == self.locKey:
            # Landed back where we started
            return None, None
        return locKey, None

    def playerHasLeftBlock(self, player, path, ticks):
        # If the player is even partly outside the region, we consider them
        # to have left the region.
        leaveDirection = playerLeavesRect(self.regionRect, player.pos)
        if leaveDirection:
            if leaveDirection != MULTIPLE:
                self.addDepartingEdge(self.locKey, path, leaveDirection)
            return True

        # If the grappling hook is outside the block, we consider this
        # action to leave the block
        if player.grapplingHook.isActive():
            leaveDirection = leavesRect(
                self.regionRect, player.grapplingHook.pos, 0, 0)
            if leaveDirection:
                if leaveDirection != MULTIPLE:
                    self.addDepartingEdge(self.locKey, path, leaveDirection)
                return True

        return False

    def simulationAdvanced(self, path, player, action, ticks, pointData):
        # Every tick, notice what grid squares the player's centre passes
        # through in case a bot needs to move to a non-stationary location.
        mapLayout = player.world.map.layout
        blockDef, offset = getRegionAndRelativePos(mapLayout, player.pos)
        self.region.addNearbyRoute(offset, self.locKey, ticks, path, False)

        # If the player is within capping distance of an orb, record the fact
        zone = player.getZone()
        if zone and zone.playerIsWithinTaggingDistance(player):
            self.region.addOrbRoute(self.locKey, path, ticks)
        return pointData


def playerLeavesRect(rect, pos):
    return leavesRect(rect, pos, Player.HALF_WIDTH, Player.HALF_HEIGHT)


def leavesRect(rect, pos, halfWidth, halfHeight):
    x, y = pos
    north = (y - halfHeight < rect.top)
    west = (x - halfWidth < rect.left)
    south = (y + halfHeight > rect.bottom)
    east = (x + halfWidth > rect.right)

    if not (north or south or east or west):
        return None
    if north and not (south or east or west):
        return NORTH
    if south and not (north or east or west):
        return SOUTH
    if east and not (north or south or west):
        return EAST
    if west and not (north or south or east):
        return WEST
    return MULTIPLE


class PlotterActionProcessor(OneBlockActionProcessor):
    def __init__(self, regionRect):
        super().__init__(None, None, regionRect, lambda *args, **kwargs: None)

    def simulationStarted(self, path, player, action, pointData):
        self.pts = [player.pos]
        return pointData

    def simulationAdvanced(self, path, player, action, ticks, pointData):
        self.pts.append(player.pos)
        return pointData

    def simulationFinished(self, pointData, *, success):
        self.simulationSuccess = success
        return pointData

    def plotActions(self, player, actions):
        results = []
        world = player.world
        for action in actions:
            player, *_ = self.runSingleAction(player, action)
            for pos in self.pts:
                blockDef, rel = getRegionAndRelativePos(world.map.layout, pos)
                results.append(DiscretisationDatabase.getLocKey(rel))
            if not self.simulationSuccess:
                break
        return results


class TwoBlockActionProcessor(ActionQueueProcessor):
    def __init__(self, combo, block0, block1, startPoint):
        self.combo = combo
        self.blocks = [block0, block1]
        self.startPoint = startPoint
        self.identification = '{}@{}'.format(combo, startPoint)

    def getRegionIndex(self, pos):
        indices = MapLayout.getMapBlockIndices(*pos)
        for i in (0, 1):
            if indices == MapLayout.getMapBlockIndices(
                    *self.blocks[i].rect.center):
                return i
        raise KeyError('{} not in allowed regions'.format(pos))

    def checkFinalPosition(self, player, pointData):
        try:
            index = self.getRegionIndex(player.pos)
        except KeyError:
            # Outside regions in question
            return None, None

        blockDef, relPos = getRegionAndRelativePos(
            player.world.map.layout, player.pos)

        endLocKey = DiscretisationDatabase.getLocKey(relPos)

        startIndex, startLocKey = self.startPoint
        endPoint = (index, endLocKey)
        if index == startIndex:
            pointData = None

            # Ignore any path that ends up back at the same point
            if self.startPoint == endPoint:
                return None, None

            # Ignore anything that doesn't either change regions or at least
            # end up in the border zone.
            if not (self.combo.isBorderPoint(self.startPoint) or
                    self.combo.isBorderPoint(endPoint)):
                return None, None

        return endPoint, pointData

    def playerHasLeftBlock(self, player, path, ticks):
        x, y = player.pos
        try:
            self.getRegionIndex((
                x - Player.HALF_WIDTH, y - Player.HALF_HEIGHT))
            self.getRegionIndex((
                x + Player.HALF_WIDTH, y + Player.HALF_HEIGHT))
            if player.grapplingHook.isActive():
                self.getRegionIndex(player.grapplingHook.pos)
        except KeyError:
            return True
        return False

    def simulationAdvanced(self, path, player, action, ticks, pointData):
        '''
        Use pointData to keep track of how many ticks passed before the
        player passed into the other region.
        '''
        try:
            index = self.getRegionIndex(player.pos)
        except KeyError:
            # Outside regions in question
            return pointData

        startIndex, startLocKey = self.startPoint
        if startIndex == index:
            pointData += 1
        return pointData


class ComboPlotterActionProcessor(TwoBlockActionProcessor):
    def simulationStarted(self, path, player, action, pointData):
        self.pts = [player.pos]
        return pointData

    def simulationAdvanced(self, path, player, action, ticks, pointData):
        self.pts.append(player.pos)
        return pointData

    def simulationFinished(self, pointData, *, success):
        self.simulationSuccess = success
        return pointData

    def plotActions(self, player, actions):
        results = []
        for action in actions:
            player, *_ = self.runSingleAction(player, action)
            for x, y in self.pts:
                rel = (
                    x - self.blocks[0].rect.centerx,
                    y - self.blocks[0].rect.centery,
                )
                results.append(DiscretisationDatabase.getLocKey(rel))
            if not self.simulationSuccess:
                break
        return results


class PathFindingStep:
    empty = False
    end = None      # type: StationaryPoint

    def run(self, route, bot):
        raise NotImplementedError()


class DoNothing(PathFindingStep):
    empty = True

    def __init__(self, end):
        self.end = end

    def run(self, route, bot):
        return iter([])


class PerformActions(PathFindingStep):
    def __init__(self, actions, end):
        self.actions = actions
        self.end = end

    def run(self, route, bot):
        for action in self.actions:
            # We need to reset ignoreState at the start of each action
            bot.applyInputState(PlayerInputState())

            route.debug('Starting action {}', action)
            yield from action.run(bot.player)

        pause = random.randrange(bot.pauseBetweenActions + 1)
        if pause:
            yield from Wait(pause).run(bot.player)


class FollowWaypoints(PathFindingStep):
    def __init__(self, waypoints):
        self.waypoints = waypoints
        self.end = waypoints[-1]

    def run(self, route, bot):
        perfectionism = bot.pathfindingPerfectionism
        waypoints = list(self.waypoints)
        currentEnd = waypoints.pop(0)

        while waypoints:
            waypoint = waypoints.pop(0)

            if waypoint not in currentEnd.getCostsToWaypoints():
                # Special case: the final item in the list does not have to
                # be a waypoint
                assert not waypoints
                for step in self.walkTowardsWaypoint(
                        perfectionism, waypoint, currentEnd, reverse=True):
                    yield from step.run(route, bot)
                return

            for step in self.walkTowardsWaypoint(
                    perfectionism, currentEnd, waypoint,
                    nextPoint=waypoints[0] if waypoints else None):
                currentEnd = step.end
                yield from step.run(route, bot)

    def walkTowardsWaypoint(
            self, perfectionism, point, waypoint, reverse=False,
            nextPoint=None):
        if reverse:
            getEdges = lambda p: p.inwardEdges()
            getCosts = lambda p: p.getCostsFromWaypoints()
        else:
            getEdges = lambda p: p.outwardEdges()
            getCosts = lambda p: p.getCostsToWaypoints()

        firstPoint = point
        steps = []
        costs = getCosts(point)
        while point != waypoint:
            if nextPoint and nextPoint in costs:
                break

            options = []
            for ticks, actions, newPoint in getEdges(point):
                newCosts = getCosts(newPoint)
                if waypoint not in newCosts:
                    continue
                improvement = costs[waypoint] - newCosts[waypoint]
                if improvement / ticks >= perfectionism:
                    options.append((newPoint, newCosts, actions))

            if DEBUG and not options:
                log.error('***** No route options found *****')
                log.error('point: {}'.format(point))
                log.error('  region: {}'.format(point.region.name))
                log.error('  region flipped: {}'.format(point.regionFlipped))
                log.error('target waypoint: {}'.format(waypoint))
                log.error('waycost: {}'.format(costs.get(waypoint)))
                log.error('edges:')
                for ticks, actions, newPoint in getEdges(point):
                    newCosts = getCosts(newPoint)
                    log.error('  %s / %s', newPoint, newCosts.get(waypoint))
                    if waypoint not in newCosts:
                        log.error('    CANNOT REACH WAYPOINT')
                        continue
                    log.error('    improvement: {}'.format(
                        costs[waypoint] - newCosts[waypoint]))
                    log.error('    edge cost: {}'.format(ticks))
                log.error('no more edges\n')
            lastPoint = point
            point, costs, actions = options.pop(random.randrange(len(options)))
            end = lastPoint if reverse else point
            steps.append(PerformActions(actions, end))

        if reverse:
            steps.reverse()
        yield from steps


class PathFindingRoute(object):
    '''
    Represents a route that a bot player uses to navigate the map. When
    created, represents an empty route from the player's current position.
    Use extendTo() to make the route non-empty.
    '''

    def __init__(self, playerState):
        self.steps = []
        self.nextTargetPos = None
        self.debugInfo = io.StringIO()
        self.runningStep = None
        self.world = playerState.world
        self.pathFinder = playerState.world.map.layout.pathFinder

        self.completeReset(playerState, 'PathFindingRoute created')

    def debug(self, message, *args, **kwargs):
        if DEBUG:
            self.debugInfo.write(message.format(*args, **kwargs) + '\n')

    def completeReset(self, playerState, note='completeReset()'):
        self.steps = []
        self.nextTargetPos = None
        self.debugInfo = io.StringIO()
        self.debug(note)
        self.debug('  lastTickId: {} ', playerState.world.lastTickId)
        self.debug('  playerState at {}', playerState.pos)
        if playerState.isStationary():
            self.debug('  stationary')
            playerState.discretiseLocation()
            try:
                endPoint = self.pathFinder.getStationaryPoint(playerState)
            except NoStationaryPointHere:
                self.appendRandomActions()
            else:
                self.steps.append(DoNothing(endPoint))
        else:
            self.debug('  not stationary')
            self.steps.append(PerformActions([FallDown()], None))
        self.debug('  end: {}', self.end)

    def appendRandomActions(self):
        actions = []
        for i in range(3):
            actions.append(random.choice([
                JumpUp(),
                JumpLeft(),
                JumpRight(),
                Drop(),
                Grapple((random.random() - 0.5) * pi, 5),
            ]))
        self.steps.append(PerformActions(actions, None))

    def isFinished(self):
        '''
        :return: True iff the player has already reached the end of this route.
        '''
        if self.runningStep:
            return False
        if self.nextTargetPos:
            return False
        if not self.steps:
            return True
        if len(self.steps) == 1 and self.steps[0].empty:
            return True
        return False

    @property
    def end(self):
        return self.steps[-1].end

    @property
    def finishPoint(self):
        return self.end.pos if self.end else None

    def truncateAtNextOpportunity(self):
        '''
        Causes this route to be truncated as soon as the player reaches a
        stationary position.
        '''
        self.steps[1:] = []
        self.nextTargetPos = None
        self.debug('** truncateAtNextOpportunity()')
        self.debug('    remaining actions: {}', self.steps)

    def extendTo(self, pos):
        self.debug('** extendTo({})', pos)
        if self.end is None:
            self.debug("  don't yet know where we're finishing", pos)
            self.nextTargetPos = pos
            return

        # 1. If the given pos has a corresponding discretisation key,
        # try to find a route there.
        try:
            point = StationaryPoint.fromPos(self.pathFinder, pos)
        except NoStationaryPointHere:
            pass
        else:
            if self.attemptPathTo(point):
                return

        # 2a. Check if the target is in the orb, and navigate there
        zone = self.world.map.getZoneAtPoint(pos)
        if zone and distance(zone.defn.pos, pos) < ZONE_CAP_DISTANCE:
            if self.attemptPathToOrb(zone.defn):
                return

        # 2b. Try to find a route to the recorded nearbyRoute for the point
        try:
            nearbyPoint, actions = self.pathFinder.getNearbyRoute(pos)
        except KeyError:
            pass
        else:
            if self.attemptPathTo(nearbyPoint):
                self.steps.append(PerformActions(actions, None))
                return

        # 3. If the current position is in the DB, then no route is
        # possible, so just do a few actions from getPossibleActions().
        for i in range(3):
            edges = list(self.end.outwardEdges())
            if not edges:
                break
            self.extendWithEdge(random.choice(edges))
        else:
            return

        # 4. By this point we know the current position is not in the DB, so
        # try doing 3 random actions in case that puts us somewhere more
        # manageable.
        self.appendRandomActions()

        # 5. Once we finish the random actions, look for a route to the new
        # position.
        self.nextTargetPos = pos

    def started(self, bot):
        '''
        We don't know whether applyOneFrame() will be called the same tick
        as this, or next tick, so it used to be essential to make the fall
        predictable - this is no longer strictly necessary, but doesn't hurt.
        '''
        bot.applyInputState(PlayerInputState())

    def applyOneFrame(self, bot):
        if not self.steps:
            raise RuntimeError('route already complete')

        self.debug(' - lastTickId: {} -', bot.player.world.lastTickId)
        while True:
            if not self.runningStep:
                if not self.steps:
                    if self.nextTargetPos:
                        targetPos = self.nextTargetPos
                        self.completeReset(
                            bot.player, note='Aiming for nextTargetPos')
                        self.extendTo(targetPos)
                    else:
                        self.debug('No more actions to do.')
                        return
                self.runningStep = self.steps[0].run(self, bot)

            if DEBUG:
                self.debug('  prev state: {}', bot.player._lastAdvanceState)
                self.debug('  new state: {}', bot.player.getPlayerUpdateArgs())
                self.debug('  pos: {}', bot.player.pos)
                self.debug('  state: {}', ', '.join(
                    k.decode() for k, v in bot.player._state.items() if v))
                self.debug('    ignore: {}', ', '.join(
                    k.decode() for k in bot.player.ignoreState))
                self.debug('  angle: {}', bot.player.angleFacing)

            try:
                inputState = next(self.runningStep)
            except StopIteration:
                self.debug('  step complete.')
                self.runningStep = None
                self.popStep(bot.player)
            else:
                self.debug('  applying input state: {}', inputState)
                bot.applyInputState(inputState)
                return

    def popStep(self, playerState):
        step = self.steps.pop(0)
        end = step.end
        if end and not isNear(distance(end.pos, playerState.pos), 0):
            self.debug('*** Bot in unexpected pos ***')
            self.debug('  expected: {}', end)
            self.debug('    pos: {}', end.pos)
            self.debug('  actual: {}', playerState.pos)
            self.debug(
                '       locKey: {}', DiscretisationDatabase.getLocKey(
                    getPosRelativeToRegion(end.blockDef, playerState.pos)))
            self.debug(
                '      region: {}', playerState.getMapBlock().defn.layout.name)
            self.debug(
                '      region mirrored: {}',
                playerState.getMapBlock().defn.layout.reversed)
            if DEBUG:
                log.error('Bot in unexpected pos - log follows')
                self.debug('--- end of log ---')
                log.error(self.debugInfo.getvalue())

            # This should only happen if the path-finding database is corrupt.
            # Recalculate the route from the new position, but start with a
            # one second pause as a rate limitter.
            if self.nextTargetPos:
                target = self.nextTargetPos
            elif self.steps:
                target = self.finishPoint
            else:
                target = end.pos
            self.completeReset(playerState)
            self.extendWithPause(10)
            if target is not None:
                self.extendTo(target)
            end = self.steps[0].end
        else:
            self.debugInfo = io.StringIO()
            self.debug('popActionSet successful')
            self.debug('  lastTickId: {} ', playerState.world.lastTickId)

        self.debug('Current point: {}', end)
        if end:
            self.debug('  current pos: {}', end.pos)
            self.debug('  current region: {}', end.region.name)
            self.debug('  region mirrored: {}', end.regionFlipped)
        if self.steps:
            self.debug('Attempting step: {}',  self.steps[0])
            self.debug('  expected destination: {}', self.steps[0].end)

    def extendWithEdge(self, edge):
        ticks, actions, endPoint = edge
        self.steps.append(PerformActions(actions, endPoint))

    def extendWithPause(self, ticks):
        self.steps.append(PerformActions([Wait(ticks)], self.end))

    def attemptPathTo(self, point):
        if self.attemptLocalPathTo(point):
            return True
        return self.attemptWaypointPathTo([(point, 0)])

    def attemptPathToOrb(self, zoneDef):
        dests = []

        x, y = zoneDef.pos
        blockDefs = [
            self.world.map.getMapBlockAtPoint((x, y - 10)).defn,
            self.world.map.getMapBlockAtPoint((x, y + 10)).defn,
        ]
        paths = {}
        for blockDef in blockDefs:
            regionName = blockDef.layout.name
            region = self.pathFinder.getRegion(regionName)
            regionFlipped = blockDef.layout.reversed
            for ticks, locKey, path, flipPath in region.getOrbRoutes():
                point = StationaryPoint(self.pathFinder, blockDef, locKey)
                dests.append((point, ticks))
                paths[point] = (path, regionFlipped ^ flipPath)
        if not self.attemptWaypointPathTo(dests):
            return False

        path, flipped = paths[self.end]
        actions = PathFindingAction.decodeGroup(path, flipped)
        self.steps.append(PerformActions(actions, None))
        return True

    def attemptLocalPathTo(self, destination):
        '''
        Attempts to extend this path to the given point using a heuristic
        based on common waypoints. This will only work if the points are
        sufficiently close to have waypoints in common.

        :param destination: the target point
        '''
        destToWaypoints = destination.getCostsToWaypoints()
        destSeesWaypoints = set(destToWaypoints)
        waypointsToDest = destination.getCostsFromWaypoints()
        waypointsSeeingDest = set(waypointsToDest)
        srcToWaypoints = self.end.getCostsToWaypoints()
        srcSeesWaypoints = set(srcToWaypoints)
        waypointsToSrc = self.end.getCostsFromWaypoints()
        waypointsSeeingSrc = set(waypointsToSrc)

        if not destSeesWaypoints.intersection(srcSeesWaypoints) and not \
                waypointsSeeingDest.intersection(waypointsSeeingSrc):
            # No common waypoints between source and destination
            return False

        def fwdHeuristic(point):
            costsToWaypoints = point.getCostsToWaypoints()
            costsFromWaypoints = point.getCostsFromWaypoints()
            return max([
                costsToWaypoints[waypoint] - costFromDest
                for waypoint, costFromDest in destToWaypoints.items()
                if waypoint in costsToWaypoints
            ] + [
                costToDest - costsFromWaypoints[waypoint]
                for waypoint, costToDest in waypointsToDest.items()
                if waypoint in costsFromWaypoints
            ])

        def fwdExpand(point):
            for ticks, actions, newPoint in point.outwardEdges():
                hereToWaypoints = newPoint.getCostsToWaypoints()
                waypointsToHere = newPoint.getCostsFromWaypoints()
                if destSeesWaypoints.intersection(hereToWaypoints) or \
                        waypointsSeeingDest.intersection(waypointsToHere):
                    yield ticks, actions, newPoint

        def bckHeuristic(point):
            costsToWaypoints = point.getCostsToWaypoints()
            costsFromWaypoints = point.getCostsFromWaypoints()
            return max([
                costFromSrc - costsToWaypoints[waypoint]
                for waypoint, costFromSrc in srcToWaypoints.items()
                if waypoint in costsToWaypoints
            ] + [
                costsFromWaypoints[waypoint] - costToSrc
                for waypoint, costToSrc in waypointsToSrc.items()
                if waypoint in costsFromWaypoints
            ])

        def bckExpand(point):
            for ticks, actions, newPoint in point.inwardEdges():
                hereToWaypoints = newPoint.getCostsToWaypoints()
                waypointsToHere = newPoint.getCostsFromWaypoints()
                if srcSeesWaypoints.intersection(hereToWaypoints) or \
                        waypointsSeeingSrc.intersection(waypointsToHere):
                    yield ticks, actions, newPoint

        aStar = TwoWayAStar(fwdHeuristic, fwdExpand, bckHeuristic, bckExpand)
        vertices, edges = aStar.run([(self.end, 0)], [(destination, 0)])
        if not vertices:
            return False

        self.steps.extend(
            PerformActions(action, end)
                for action, end in zip(edges, vertices[1:]))
        return True

    def attemptWaypointPathTo(self, destinations):
        def fwdHeuristic(point):
            return 0

        def bckHeuristic(point):
            return 0

        def fwdExpand(point):
            for waypoint, ticks in point.getCostsToWaypoints().items():
                yield ticks, None, waypoint

        def bckExpand(point):
            for waypoint, ticks in point.getCostsFromWaypoints().items():
                yield ticks, None, waypoint

        aStar = TwoWayAStar(fwdHeuristic, fwdExpand, bckHeuristic, bckExpand)
        vertices, edges = aStar.run([(self.end, 0)], destinations)
        if not vertices:
            return False

        self.steps.append(FollowWaypoints(vertices))
        return True


class TwoWayAStar:
    def __init__(self, fwdHeuristic, fwdExpand, bckHeuristic, bckExpand):
        self.forwardSearch = BasicAStar(
            fwdHeuristic, fwdExpand, self.checkForwardSolution)
        self.backwardSearch = BasicAStar(
            bckHeuristic, bckExpand, self.checkBackwardSolution)

    def run(self, forwardStartVertices, backwardStartVertices):
        self.forwardSearch.initialise(forwardStartVertices)
        self.backwardSearch.initialise(backwardStartVertices)
        while True:
            self.forwardSearch.step()
            if self.forwardSearch.finished:
                return self.getPath(self.forwardSearch.current)
            self.backwardSearch.step()
            if self.backwardSearch.finished:
                return self.getPath(self.backwardSearch.current)

    def checkForwardSolution(self, vertex):
        return vertex in self.backwardSearch.trace

    def checkBackwardSolution(self, vertex):
        return vertex in self.forwardSearch.trace

    def getPath(self, vertex):
        if self.forwardSearch.failed or self.backwardSearch.failed:
            return [], []
        fVertices, fEdges = self.forwardSearch.getPath(vertex)
        bVertices, bEdges = self.backwardSearch.getPath(vertex)
        return fVertices[:-1] + list(reversed(bVertices)), fEdges + list(
            reversed(bEdges))


Vertex = TypeVar('Vertex')
EdgeInfo = Tuple[float, Any, Vertex]


class BasicAStar:
    def __init__(
            self,
            heuristic: Callable[[Vertex], float],
            expandVertex: Callable[[Vertex], Iterable[EdgeInfo]],
            checkSolution: Callable[[Vertex], bool],
    ):
        '''
        :param heuristic: a function accepting a vertex and returning the
            heuristic estimate of the cost from the given vertex to the
            solution.
        :param expandVertex: a function accepting a vertex and returning an
            iterable of (edgeCost, edgeData, newVertex), where edgeCost is
            the cost of an edge from vertex to newVertex, and edgeData is
            any arbitrary data that is associated with the edge. The value
            of edgeData is retrieved as part of the result of a call to
            getData().
        :param checkSolution: a function accepting a vertex and returning
            True or False depending on whether the given vertex is a
            solution point.
        '''
        self.started = False
        self.heap = []
        self.trace = {}
        self.index = 0
        self.counter = 0
        self.current = None
        self.currentCost = 0
        self.failed = False
        self.succeeded = False
        self.rawHeuristic = heuristic
        self.expandVertex = expandVertex
        self.checkSolution = checkSolution

    def heuristic(self, vertex):
        if self.checkSolution(vertex):
            return 0
        return max(0, self.rawHeuristic(vertex))

    def run(self, startVertices: Iterable[Tuple[Vertex, float]]):
        self.initialise(startVertices)
        while not self.finished:
            self.step()
        return self.getPath()

    def initialise(self, startVertices):
        if self.started:
            raise RuntimeError('already started')
        self.started = True
        counter = -1
        for startVertex, startCost in startVertices:
            heuristic = self.heuristic(startVertex)
            heapq.heappush(self.heap, (
                startCost + heuristic, counter, startVertex, startCost, None))
            counter -= 1

    def step(self):
        if not self.started:
            raise RuntimeError('not yet started')
        if self.finished:
            raise RuntimeError('already finished')

        self.index += 1
        self.current = None
        self.currentCost = 0
        while self.heap:
            _, _, vertex, costSoFar, edge = heapq.heappop(self.heap)
            if vertex in self.trace:
                continue

            self.current = vertex
            self.currentCost = costSoFar
            self.trace[vertex] = edge

            if self.checkSolution(vertex):
                self.succeeded = True
                return

            for edgeCost, edgeData, newVertex in self.expandVertex(vertex):
                heuristic = self.heuristic(newVertex)
                if heuristic is None:
                    continue
                heapq.heappush(self.heap, (
                    costSoFar + edgeCost + heuristic, self.counter,
                    newVertex, costSoFar + edgeCost, (vertex, edgeData)))
                self.counter += 1
            return

        self.failed = True

    @property
    def finished(self):
        return self.succeeded or self.failed

    def getPath(self, vertex=None) -> Tuple[List[Vertex], List[Any]]:
        '''
        Shows the path to the given or current vertex from the start vertex
        of the search.

        :param vertex: if provided, the vertex to show the path to. If not
            provided, the vertex of the current iteration is used.
        :return: (vertices, edges) where vertices is a list of all vertices
            in the path (including the start and end vertices), and edges is
            a list of the edgeData for each edge in the path.
        '''
        if self.failed:
            return [], []

        if vertex is None:
            vertex = self.current
            if vertex is None:
                raise RuntimeError('no current vertex')

        vertices = [vertex]
        edges = []
        while True:
            edge = self.trace[vertex]
            if edge is None:
                return vertices, edges

            prevVertex, edgeData = edge
            edges.insert(0, edgeData)
            vertices.insert(0, prevVertex)
            vertex = prevVertex


def exhaustiveDijkstra(visitVertex, expandVertex, startVertices):
    '''
    Performs Dijkstra's algorithm exhaustively over the search space.

    :param visitVertex: a function that is called with parameters (vertex,
        cost), indicating the minimum cost from the start vertex to the given
        vertex.
    :param expandVertex: see BasicAStar()
    :param startVertices: iterable of (vertex, startCost) for vertices to
        start search from.
    :return:
    '''

    def heuristic(vertex):
        return 0

    def checkSolution(vertex):
        return False

    aStar = BasicAStar(heuristic, expandVertex, checkSolution)
    aStar.initialise(startVertices)
    while not aStar.finished:
        aStar.step()
        if aStar.current is not None:
            try:
                visitVertex(aStar.current, aStar.currentCost)
            except StopIteration:
                break


class DiscretisationDatabase:
    _instance = None

    def __init__(self, path=DISCRETISATION_FILENAME):
        self.path = path
        self.data = {}
        self.fullyBuiltRegions = set()
        self.dirty = False
        self.symmetricalNames = {}
        self.reload()

    @staticmethod
    def get():
        if DiscretisationDatabase._instance is None:
            DiscretisationDatabase._instance = DiscretisationDatabase()
        return DiscretisationDatabase._instance

    def reload(self):
        try:
            f = open(self.path, 'rb')
        except FileNotFoundError:
            log.warning(
                'Discretisation database not found: {!r}'.format(self.path))
            self.data = {}
            self.fullyBuiltRegions = set()
            self.dirty = False
            return

        with f:
            self.data, self.fullyBuiltRegions = pickle.load(f)
        self.dirty = False

    def save(self):
        with open(self.path, 'wb') as f:
            data = (self.data, self.fullyBuiltRegions)
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        self.dirty = False

    def getDiscretisationLocation(self, regionName, pos):
        return self.getDiscretisationLocationByKey(
            regionName, self.getLocKey(pos))

    def regionIsSymmetrical(self, regionName):
        if regionName not in self.symmetricalNames:
            layout = getLayoutDB().getLayoutByName(regionName)
            self.symmetricalNames[regionName] = (
                    layout and layout.mirrorLayout is layout)
        return self.symmetricalNames[regionName]

    def symmetrise(self, regionName, locKey):
        if not self.regionIsSymmetrical(regionName):
            return False, locKey
        i, j = locKey
        return i < 0, (abs(i), j)

    def getDiscretisationLocationByKey(self, regionName, locKey):
        flipped, dbLocKey = self.symmetrise(regionName, locKey)
        try:
            result = self.data[regionName][dbLocKey]
        except KeyError:
            raise NoStationaryPointHere((regionName, locKey))
        if flipped:
            offset, angle = result
            result = mirrorOffsetAndAngle(offset, angle)
        return result

    @staticmethod
    def getLocKey(pos):
        x, y = pos
        flipped = (x < 0)

        # Due to the nature of hand-drawn maps, some stationary locations
        # are fairly likely to occur on discretisation unit boundaries. To
        # avoid floating point imprecisions in these cases, this code
        # shifts this boundary by epsilon.
        # There is also code in findCollisionPoint() which complains if a
        # stationary location lies on the (shifted) boundary.
        epsilon = 1e-3

        # Uses abs(x) and sign to ensure symmetrical regions are treated
        # symmetrically.
        i = round((abs(x) + epsilon) / PATH_FINDING_DISCRETISATION_UNIT)
        j = round((y + epsilon) / PATH_FINDING_DISCRETISATION_UNIT)
        if flipped:
            i = -i
        return i, j

    def getAllLocKeys(self, regionName, raw=False):
        result = self.data.get(regionName, {}).keys()
        if not raw and self.regionIsSymmetrical(regionName):
            return {flipKey(k) for k in result}.union(result)
        return set(result)

    def getLocationCount(self, regionName, raw=False):
        return len(self.getAllLocKeys(regionName, raw=raw))

    def isRegionFullyBuilt(self, regionName):
        return regionName in self.fullyBuiltRegions

    def plot(self, regionName):
        from matplotlib import pyplot

        xs = []
        ys = []
        for (i, j) in self.getAllLocKeys(regionName):
            xs.append(i)
            ys.append(-j)
        pyplot.plot(xs, ys, 'b.')
        pyplot.show()

    def dropRegion(self, regionName):
        self.dirty = True
        self.fullyBuiltRegions.discard(regionName)
        try:
            del self.data[regionName]
        except KeyError:
            pass

    def markRegionAsFullyBuilt(self, regionName):
        self.dirty = True
        self.fullyBuiltRegions.add(regionName)

    def addLocation(self, regionName, offset, angle):
        self.dirty = True

        flipped, (i, j) = self.symmetrise(regionName, self.getLocKey(offset))
        if flipped:
            offset, angle = mirrorOffsetAndAngle(offset, angle)
        x = i * PATH_FINDING_DISCRETISATION_UNIT
        y = j * PATH_FINDING_DISCRETISATION_UNIT

        if regionName not in self.data:
            self.data[regionName] = {}

        if self.regionIsSymmetrical(regionName) and i == 0 \
                and not isNear(offset[0], 0):
            # We must keep symmetrical regions symmetrical
            return

        if (i, j) not in self.data[regionName]:
            self.data[regionName][i, j] = (offset, angle)
            return

        if self.isRegionFullyBuilt(regionName):
            return

        oldOffset, oldAngle = self.data[regionName][i, j]
        oldDist = distance(oldOffset, (x, y))
        newDist = distance(offset, (x, y))
        if newDist < oldDist:
            self.data[regionName][i, j] = (offset, angle)


class PathFindingDatabase:
    _instance = None

    def __init__(self, path=PATHFINDING_FILENAME):
        self.path = path
        self.dirty = False
        self.data = {}
        self.regionObjects = {}
        self.halfCombos = {}

        self.reload()

    @staticmethod
    def get():
        if PathFindingDatabase._instance is None:
            PathFindingDatabase._instance = PathFindingDatabase()
        return PathFindingDatabase._instance

    def reload(self):
        try:
            f = open(self.path, 'rb')
        except FileNotFoundError:
            log.warning(
                'Pathfinding database not found: {!r}'.format(self.path))
            self.data = {}
            self.dirty = False
            return

        with f:
            self.data = pickle.load(f)
        self.dirty = False

    def save(self):
        with open(self.path, 'wb') as f:
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)
        self.dirty = False

    def getRegion(self, regionName):
        try:
            return self.regionObjects[regionName]
        except KeyError:
            result = PathFindingRegion(self, regionName)
            self.regionObjects[regionName] = result
            return result

    def getHalfCombo(self, region1, region2, flip1, flip2, direction):
        key = (region1.name, region2.name, flip1, flip2, direction)
        try:
            return self.halfCombos[key]
        except KeyError:
            ref = RegionCombinationReference(
                region1, region2, flip1, flip2, direction)
            result = self.halfCombos[key] = ref.getHalfCombination(self)
            return result


def flipKey(locKey):
    i, j = locKey
    return -i, j


class PathFindingRegion:
    _layoutDB = None

    def __init__(self, db, regionName):
        self.db = db
        self.name = regionName
        self.rect = self.buildRect()
        self.symmetrical = self.isSymmetrical()

        data = db.data.setdefault('regions', {}).setdefault(regionName, {})
        self.edges = data.setdefault('edges', {})
        self.nearbyRoutes = data.setdefault('nearby', {})
        self.orbRoutes = data.setdefault('orb', set())
        self.exits = data.setdefault('exits', {})
        self.examined = data.setdefault('examined', set())
        self.costsToWaypoints = data.setdefault('toway', {})
        self.costsFromWaypoints = data.setdefault('fromway', {})

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.db == other.db and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def drop(self):
        self.db.dirty = True
        self.edges.clear()
        self.nearbyRoutes.clear()
        self.orbRoutes.clear()
        self.exits.clear()
        self.examined.clear()
        self.costsToWaypoints.clear()
        self.costsFromWaypoints.clear()

    def getLayout(self):
        return getLayoutDB().getLayoutByName(self.name)

    def buildRect(self):
        layout = self.getLayout()
        result = Rect((0, 0), MapBlockDef.getSize(layout.kind))
        result.center = (0, 0)
        return result

    def isSymmetrical(self):
        layout = self.getLayout()
        return layout.mirrorLayout is layout

    def plot(self, extra=()):
        from matplotlib import pyplot

        ddb = DiscretisationDatabase.get()
        regionPoints = set(ddb.getAllLocKeys(self.name))

        x = []
        y = []
        c = []
        for (i, j) in regionPoints:
            x.append(i)
            y.append(-j)
            c.append(
                'c' if self.isBorderPoint((i, j))
                else 'g' if self.pointCanReachWaypoints((i, j))
                else 'r')
        for (i, j) in extra:
            x.append(i)
            y.append(-j)
            c.append('m')

        x2 = []
        y2 = []
        for (i, j), directions in WAYPOINTS.get(self.name, ()):
            x2.append(i)
            y2.append(-j)

        pyplot.scatter(x, y, c=c, marker='.')
        pyplot.scatter(x2, y2, c='r', marker='x', label='waypoint')
        pyplot.show()

    def plotCosts(self, index, outward=False):
        from matplotlib import pyplot

        waypoint, directions = WAYPOINTS[self.name][index]
        getCosts = self.getCostsFromWaypoints if outward else \
            self.getCostsToWaypoints
        ddb = DiscretisationDatabase.get()

        x1 = []
        y1 = []
        c1 = []
        x2 = []
        y2 = []
        c2 = []
        x3 = []
        y3 = []
        for (i, j) in set(ddb.getAllLocKeys(self.name)):
            if waypoint in getCosts((i, j)):
                x1.append(i)
                y1.append(-j)
                c1.append(getCosts((i, j))[waypoint])
            else:
                x2.append(i)
                y2.append(-j)
                c2.append('c' if self.isBorderPoint((i, j)) else 'r')

            if (i, j) == waypoint:
                x3.append(i)
                y3.append(-j)

        pyplot.scatter(x1, y1, c=c1, marker='.', label='score')
        pyplot.scatter(x2, y2, c=c2, marker='+', label='no score')
        pyplot.scatter(x3, y3, c='r', marker='x', label='waypoint')
        pyplot.show()

    def getNonBorderLocKeys(self, raw=False):
        ddb = DiscretisationDatabase.get()
        for locKey in ddb.getAllLocKeys(self.name, raw=raw):
            if not self.isBorderPoint(locKey):
                yield locKey

    def getEdgeStartKeys(self, raw=False):
        result = set(locKey for locKey, (o, i) in self.edges.items() if o)
        if not raw and self.symmetrical:
            result.update({flipKey(k) for k in result})
            pass
        return result

    def symmetrise(self, locKey):
        if not self.symmetrical:
            return False, locKey
        i, j = locKey
        return i < 0, (abs(i), j)

    def getOutwardEdges(self, locKey):
        flipped, locKey = self.symmetrise(locKey)
        if locKey not in self.edges:
            return
        for ticks, endKey, path, flipPath in self.edges[locKey][0]:
            if flipped:
                endKey = flipKey(endKey)
            yield ticks, endKey, path, flipPath ^ flipped

    def getInternalEdges(self, raw=False):
        for startKey in self.getEdgeStartKeys(raw=raw):
            for ticks, endKey, path, flipPath in self.getOutwardEdges(
                    startKey):
                yield startKey, endKey, ticks, path, flipPath

    def getInwardEdges(self, locKey):
        flipped, locKey = self.symmetrise(locKey)
        if locKey not in self.edges:
            return
        for ticks, startKey, path, flipPath in self.edges[locKey][1]:
            if flipped:
                startKey = flipKey(startKey)
            yield ticks, startKey, path, flipPath ^ flipped

    def getAlreadyExaminedLocKeys(self):
        return self.examined

    def markLocKeyAsExamined(self, locKey):
        flipped, locKey = self.symmetrise(locKey)
        self.examined.add(locKey)

    def forgetLocKey(self, locKey):
        try:
            outgoing, incoming = self.edges[locKey]
        except KeyError:
            pass
        else:
            for ticks, endKey, path, flipPath in outgoing:
                self.removeEdge(locKey, endKey, ticks, path, flipPath)
            for ticks, startKey, path, flipPath in incoming:
                self.removeEdge(startKey, locKey, ticks, path, flipPath)
            del self.edges[locKey]
            self.examined.discard(locKey)
            self.db.dirty = True

        try:
            del self.exits[locKey]
        except KeyError:
            pass
        else:
            self.db.dirty = True

    def removeEdge(self, startKey, endKey, ticks, path, flipPath):
        self.db.dirty = True

        def removeEntry(index, key1, key2, preflipped):
            flipped, key1 = self.symmetrise(key1)
            if flipped:
                key2 = flipKey(key2)
            entries = self.edges[key1][index]
            entries.discard((ticks, key2, path, preflipped ^ flipped))
            if not any(entries):
                del self.edges[key1]

        removeEntry(0, startKey, endKey, flipPath)
        removeEntry(1, endKey, startKey, flipPath)
        if self.symmetrical:
            removeEntry(0, flipKey(startKey), flipKey(endKey), not flipPath)
            removeEntry(1, flipKey(endKey), flipKey(startKey), not flipPath)

    def isBorderPoint(self, locKey):
        ddb = DiscretisationDatabase.get()
        pos, angle = ddb.getDiscretisationLocationByKey(self.name, locKey)
        return playerLeavesRect(self.rect, pos)

    def addInternalEdge(self, startKey, endKey, ticks, path, flipPath=False):
        self.db.dirty = True

        def insertEntry(index, key1, key2, preflipped):
            flipped, key1 = self.symmetrise(key1)
            if flipped:
                key2 = flipKey(key2)
            entries = self.edges.setdefault(key1, (set(), set()))[index]
            entries.add((ticks, key2, path, preflipped ^ flipped))

        insertEntry(0, startKey, endKey, flipPath)
        insertEntry(1, endKey, startKey, flipPath)
        if self.symmetrical:
            insertEntry(0, flipKey(startKey), flipKey(endKey), not flipPath)
            insertEntry(1, flipKey(endKey), flipKey(startKey), not flipPath)

    def addDepartingEdge(self, locKey, path, direction, flipPath=False):
        '''
        Records edges that depart from this region. This is not useful at
        run-time, but is useful for calculating transitions between this region
        and others.
        '''
        self.db.dirty = True
        flipped, locKey = self.symmetrise(locKey)
        existing = self.exits.setdefault(locKey, {})
        existing.setdefault(direction, set()).add((path, flipPath ^ flipped))

    def getDepartingEdges(self, direction):
        otherDirection = HORIZONTAL_OPPOSITE[direction]
        for (i, j), exits in self.exits.items():
            result = set(exits.get(direction, set()))
            if self.symmetrical and i == 0:
                for path, flipPath in exits.get(otherDirection, set()):
                    result.add((path, not flipPath))
            if result:
                yield (i, j), result
            if self.symmetrical and i != 0:
                result = set(
                    (path, not flipPath)
                    for (path, flipPath) in exits.get(otherDirection, []))
                if result:
                    yield (-i, j), result

    def addNearbyRoute(self, offset, startLocKey, ticks, path, pathFlipped):
        '''
        Records routes to get near to parts of the map which may not have
        stationary points in them.
        '''
        i = round(offset[0] / NEARBY_ROUTE_BOX_WIDTH)
        j = round(offset[1] / NEARBY_ROUTE_BOX_HEIGHT)

        flipped, routeKey = self.symmetrise((i, j))
        if flipped:
            startLocKey = flipKey(startLocKey)

        if routeKey not in self.nearbyRoutes:
            addRoute = True
        else:
            oldTicks = self.nearbyRoutes[routeKey][0]
            addRoute = ticks < oldTicks

        if addRoute:
            self.db.dirty = True
            self.nearbyRoutes[routeKey] = (
                ticks, startLocKey, path, flipped ^ pathFlipped)

    def forgetNearbyRoute(self, indices):
        try:
            del self.nearbyRoutes[indices]
        except KeyError:
            pass

    def getNearbyRoute(self, offset):
        i = round(offset[0] / NEARBY_ROUTE_BOX_WIDTH)
        j = round(offset[1] / NEARBY_ROUTE_BOX_HEIGHT)
        return self.getNearbyRouteByIndices((i, j))

    def getNearbyRouteByIndices(self, indices):
        flipped, indices = self.symmetrise(indices)
        ticks, startLocKey, path, flipRoute = self.nearbyRoutes[indices]
        return startLocKey, path, flipRoute ^ flipped

    def getNearbyRouteIndexBounds(self):
        return (
            floor(self.rect.left / NEARBY_ROUTE_BOX_WIDTH),
            ceil(self.rect.right / NEARBY_ROUTE_BOX_WIDTH),
            floor(self.rect.top / NEARBY_ROUTE_BOX_HEIGHT),
            ceil(self.rect.bottom / NEARBY_ROUTE_BOX_HEIGHT),
        )

    def getAllIndicesWithNearbyRoutes(self):
        result = set(self.nearbyRoutes)
        if self.symmetrical:
            result = result.union(flipKey(k) for k in result)
        return result

    def copyNearbyRoute(self, indicesFrom, indicesTo):
        self.db.dirty = True
        flip1, indicesFrom = self.symmetrise(indicesFrom)
        flip2, indicesTo = self.symmetrise(indicesTo)
        record = self.nearbyRoutes[indicesFrom]
        if flip1 ^ flip2:
            ticks, (i, j), path, flipped = record
            record = ticks, (-i, j), path, not flipped
        self.nearbyRoutes[indicesTo] = record

    def addOrbRoute(self, startLocKey, path, ticks):
        flipped, startLocKey = self.symmetrise(startLocKey)
        self.orbRoutes.add((ticks, startLocKey, path, flipped))

    def getOrbRoutes(self):
        result = self.orbRoutes
        if self.symmetrical:
            result = result.union(
                (ticks, (-i, j), path, flipped)
                for ticks, (i, j), path, flipped in result)
        return self.orbRoutes

    def removeOrbRoute(self, routeRecord):
        self.orbRoutes.remove(routeRecord)

    def clearCosts(self):
        self.costsToWaypoints.clear()
        self.costsFromWaypoints.clear()

    def setCostToWaypoint(self, locKey, waypoint, cost):
        self.db.dirty = True
        flipped, locKey = self.symmetrise(locKey)
        if flipped:
            waypoint = flipKey(waypoint)
        self.costsToWaypoints.setdefault(locKey, {})[waypoint] = cost
        if self.symmetrical and locKey[0] == 0:
            waypoint = flipKey(waypoint)
            self.costsToWaypoints.setdefault(locKey, {})[waypoint] = cost

    def setCostFromWaypoint(self, locKey, waypoint, cost):
        self.db.dirty = True
        flipped, locKey = self.symmetrise(locKey)
        if flipped:
            waypoint = flipKey(waypoint)
        self.costsFromWaypoints.setdefault(locKey, {})[waypoint] = cost
        if self.symmetrical and locKey[0] == 0:
            waypoint = flipKey(waypoint)
            self.costsFromWaypoints.setdefault(locKey, {})[waypoint] = cost

    def getCostsToWaypoints(self, locKey):
        flipped, locKey = self.symmetrise(locKey)
        result = self.costsToWaypoints.get(locKey, {})
        if flipped:
            return {flipKey(k): cost for k, cost in result.items()}
        return result

    def getCostsFromWaypoints(self, locKey):
        flipped, locKey = self.symmetrise(locKey)
        result = self.costsFromWaypoints.get(locKey, {})
        if flipped:
            return {flipKey(k): cost for k, cost in result.items()}
        return result

    def pointIsReachable(self, locKey):
        flipped, locKey = self.symmetrise(locKey)
        return bool(self.costsFromWaypoints.get(locKey, {}))

    def pointCanReachWaypoints(self, locKey):
        flipped, locKey = self.symmetrise(locKey)
        return bool(self.costsToWaypoints.get(locKey, {}))


class RegionCombinationReference:
    def __init__(self, blockLayout1, blockLayout2, flip1, flip2, direction):
        self.key = (direction, blockLayout1, blockLayout2, flip1, flip2)

    @staticmethod
    def mirrorKey(key):
        d, r1, r2, f1, f2 = key
        newF1 = False if r1.mirrorLayout is r1 else not f1
        newF2 = False if r2.mirrorLayout is r2 else not f2
        return (HORIZONTAL_OPPOSITE[d], r1, r2, newF1, newF2)

    @staticmethod
    def swapKey(key):
        d, r1, r2, f1, f2 = key
        return (OPPOSITE_DIRECTION[d], r2, r1, f2, f1)

    def getHalfCombination(self, db):
        options = [
            (self.key, False, 0),
            (self.mirrorKey(self.key), True, 0),
            (self.swapKey(self.key), False, 1),
            (self.swapKey(self.mirrorKey(self.key)), True, 1),
        ]

        def keyFn(arg):
            (d, r1, r2, f1, f2), m, i = arg
            return (d, r1.name, r2.name, f1, f2), m
        key, mirror, index = min(options, key=keyFn)

        d, r1, r2, f1, f2 = key
        combo = PathFindingRegionCombination(db, r1.name, r2.name, f1, f2, d)
        return HalfCombination(combo, index, mirror)


class PathFindingRegionCombination:
    def __init__(self, db, regionName1, regionName2, flip1, flip2, direction):
        self.db = db
        self.name1 = regionName1
        self.name2 = regionName2
        self.flip1 = flip1
        self.flip2 = flip2
        self.direction = direction

        key = self.getKey()
        combos = db.data.setdefault('combos', {}).setdefault(key, {})
        self.edges = combos.setdefault('edges', {})
        self.examined = combos.setdefault('examined', set())
        self.costsToWaypoints = combos.setdefault('toway', {})
        self.costsFromWaypoints = combos.setdefault('fromway', {})

    def __str__(self):
        return '{}{} > {} > {}{}'.format(
            self.name1, ' (R)' if self.flip1 else '',
            self.direction,
            self.name2, ' (R)' if self.flip2 else '',
        )

    def getKey(self):
        return (self.direction, self.name1, self.name2, self.flip1, self.flip2)

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.getKey() == other.getKey()

    def __hash__(self):
        return hash(self.getKey())

    def drop(self):
        self.edges.clear()
        self.examined.clear()
        self.costsToWaypoints.clear()
        self.costsFromWaypoints.clear()

    def getOffsetToSecondBlock(self):
        r0 = self.getRegion(0)
        r1 = self.getRegion(1)
        if self.direction == NORTH:
            offset = (0, r0.rect.top - r1.rect.bottom)
        elif self.direction == SOUTH:
            offset = (0, r0.rect.bottom - r1.rect.top)
        elif self.direction == EAST:
            offset = (r0.rect.right - r1.rect.left, 0)
        else:
            offset = (r0.rect.left - r1.rect.right, 0)
        return offset

    def plot(self, extra=()):
        from matplotlib import pyplot
        ddb = DiscretisationDatabase.get()

        # Calculate how far we should offset the second block by
        offset = self.getOffsetToSecondBlock()
        discretisedOffset = (
            offset[0] / PATH_FINDING_DISCRETISATION_UNIT,
            offset[1] / PATH_FINDING_DISCRETISATION_UNIT)

        points = [
            (i, locKey) for i in (0, 1)
            for locKey in ddb.getAllLocKeys(self.getRegionName(i))]

        x = []
        y = []
        c = []
        for index, (i, j) in points:
            outward, inward = self.edges.get((index, (i, j)), (set(), set()))
            c.append(
                'g' if outward and inward
                else 'y' if outward
                else 'm' if inward
                else 'r' if self.isBorderPoint((index, (i, j)))
                else 'b')
            if index:
                i += discretisedOffset[0]
                j += discretisedOffset[1]
                j -= 0.1    # To distinguish the edge points
            if self.getFlip(index):
                i = -i
            x.append(i)
            y.append(-j)

        badPoints = (
            point for point, (outward, inward) in self.edges.items()
            if point not in points)
        x1 = []
        y1 = []
        for index, (i, j) in badPoints:
            if index:
                i += discretisedOffset[0]
                j += discretisedOffset[1]
                j -= 0.1    # To distinguish the edge points
            if self.getFlip(index):
                i = -i
            x1.append(i)
            y1.append(-j)

        x2 = []
        y2 = []
        for i, j in extra:
            x2.append(i)
            y2.append(-j)

        pyplot.scatter(x, y, c=c, marker='.')
        pyplot.scatter(x1, y1, c='r', marker='x')
        pyplot.scatter(x2, y2, c='k', marker='o')
        pyplot.show()

    def plotCosts(self, regionIndex, waypointIndex, outward=False):
        from matplotlib import pyplot

        waypoint, directions = WAYPOINTS[
            self.getRegionName(regionIndex)][waypointIndex]
        costs = self.costsFromWaypoints if outward else self.costsToWaypoints
        ddb = DiscretisationDatabase.get()
        log.error('(%s, %s)', regionIndex, waypoint)

        # Calculate how far we should offset the second block by
        offset = self.getOffsetToSecondBlock()
        discretisedOffset = (
            offset[0] / PATH_FINDING_DISCRETISATION_UNIT,
            offset[1] / PATH_FINDING_DISCRETISATION_UNIT)
        log.error(discretisedOffset)

        points = [
            (i, locKey) for i in (0, 1)
            for locKey in ddb.getAllLocKeys(self.getRegionName(i))]

        x1 = []
        y1 = []
        c1 = []
        x2 = []
        y2 = []
        c2 = []
        x3 = []
        y3 = []
        for point in points:
            index, (i, j) = point
            if index:
                i += discretisedOffset[0]
                j += discretisedOffset[1]
                j -= 0.1    # To distinguish the edge points
            if self.getFlip(index):
                i = -i

            if (regionIndex, waypoint) in costs.get(point, {}):
                x1.append(i)
                y1.append(-j)
                c1.append(costs[point][regionIndex, waypoint])
            else:
                x2.append(i)
                y2.append(-j)
                c2.append('r' if self.isBorderPoint(point) else 'c')

            if point == (regionIndex, waypoint):
                x3.append(i)
                y3.append(-j)

        pyplot.scatter(x1, y1, c=c1, marker='.', label='score')
        pyplot.scatter(x2, y2, c=c2, marker='+', label='no score')
        pyplot.scatter(x3, y3, c='r', marker='x', label='waypoint')

        pyplot.show()

    def getRegionName(self, index):
        return self.name2 if index else self.name1

    def getFlip(self, index):
        return self.flip2 if index else self.flip1

    def getRegion(self, index):
        return self.db.getRegion(self.getRegionName(index))

    def getDirectionRelativeToTransition(self, index):
        '''
        From the perspective of the world where this transition is in its
        canonical orientation, returns the direction from the given block
        index to the transition.
        '''
        return OPPOSITE_DIRECTION[self.direction] if index else self.direction

    def getDirectionRelativeToRegion(self, index):
        '''
        From the perspective of the canonical orientation of the region
        specified by the given index, returns the direction of this transition.
        '''
        direction = self.getDirectionRelativeToTransition(index)
        if self.getFlip(index):
            direction = HORIZONTAL_OPPOSITE[direction]
        return direction

    def addEdge(self, startPoint, ticks, path, endPoint, initialCost):
        self.db.dirty = True
        startRecord = self.edges.setdefault(startPoint, (set(), set()))
        startRecord[0].add((ticks, endPoint, path))
        endRecord = self.edges.setdefault(endPoint, (set(), set()))
        endRecord[1].add((ticks, startPoint, path))

    def getEdgeStartPoints(self):
        return set(point for point, (o, i) in self.edges.items() if o)

    def getEdgeEndPoints(self):
        return set(point for point, (o, i) in self.edges.items() if i)

    def getExaminedPoints(self):
        return self.examined

    def markPointAsExamined(self, point):
        self.examined.add(point)

    def getOutwardEdges(self, startPoint):
        try:
            return self.edges[startPoint][0]
        except KeyError:
            return set()

    def getInwardEdges(self, endPoint):
        try:
            return self.edges[endPoint][1]
        except KeyError:
            return set()

    def getEdges(self):
        for startPoint, (outward, inward) in self.edges.items():
            for ticks, endPoint, path in outward:
                yield startPoint, endPoint, ticks, path

    def removeEdge(self, startPoint, endPoint, ticks, path):
        self.db.dirty = True
        self.edges[startPoint][0].remove((ticks, endPoint, path))
        if not any(self.edges[startPoint]):
            del self.edges[startPoint]
        self.edges[endPoint][1].remove((ticks, startPoint, path))
        if not any(self.edges[endPoint]):
            del self.edges[endPoint]

    def forgetPoint(self, point):
        try:
            outgoing, incoming = self.edges[point]
        except KeyError:
            pass
        else:
            self.db.dirty = True
            for ticks, endPoint, path in outgoing:
                self.edges[endPoint][1].remove((ticks, point, path))
            for ticks, startPoint, path in incoming:
                self.edges[startPoint][0].remove((ticks, point, path))
            del self.edges[point]

    def isBorderPoint(self, point):
        index, locKey = point
        direction = self.getRegion(index).isBorderPoint(locKey)
        return direction == self.getDirectionRelativeToRegion(index)

    def getExpectedInwardTransitions(self):
        '''
        Returns a mapping of {point: pathStubs} for all edges that are expected
        to go through this combination from either side, based on the
        departing edges recorded in the neighbouring regions.
        '''
        result = {}
        for index in (0, 1):
            region = self.getRegion(index)
            direction = self.getDirectionRelativeToRegion(index)
            for locKey, pathInfo in region.getDepartingEdges(direction):
                point = (index, locKey)
                result[point] = pathInfo
        return result

    def clearCosts(self):
        self.db.dirty = True
        self.costsToWaypoints.clear()
        self.costsFromWaypoints.clear()

    def setCostToWaypoint(self, point, waypoint, cost):
        self.db.dirty = True
        self.costsToWaypoints.setdefault(point, {})[waypoint] = cost

    def setCostFromWaypoint(self, point, waypoint, cost):
        self.db.dirty = True
        self.costsFromWaypoints.setdefault(point, {})[waypoint] = cost

    def getCostsToWaypoints(self, point):
        return self.costsToWaypoints.get(point, {})

    def getCostsFromWaypoints(self, point):
        return self.costsFromWaypoints.get(point, {})


class HalfCombination:
    def __init__(self, combo, index, mirror):
        self.combo = combo
        self.index = index
        self.mirror = mirror

    def getCanonicalCombo(self):
        return self.combo

    def getOutwardEdges(self, locKey):
        point = self.correctPoint((self.index, locKey))
        for ticks, endPoint, path in self.combo.getOutwardEdges(point):
            endIndex, endLocKey = self.correctPoint(endPoint)
            actions = PathFindingAction.decodeGroup(path, self.mirror)
            yield ticks, (endIndex != self.index), endLocKey, actions

    def getInwardEdges(self, locKey):
        point = self.correctPoint((self.index, locKey))
        for ticks, startPoint, path in self.combo.getInwardEdges(point):
            startIndex, startLocKey = self.correctPoint(startPoint)
            actions = PathFindingAction.decodeGroup(path, self.mirror)
            yield ticks, (startIndex != self.index), startLocKey, actions

    def correctPoint(self, point):
        # This is necessary if the point is in a symmetrical region,
        # to translate between the locKey with regard to the combination and
        #  the locKey with regard to the region.
        index, locKey = point
        if self.mirror:
            region = self.combo.getRegion(index)
            if region.symmetrical:
                locKey = flipKey(locKey)
        return index, locKey

    def allInwardEdgeEnds(self):
        for start, end, *_ in self.combo.getEdges():
            if self.combo.isBorderPoint(end):
                continue
            endIndex, endLocKey = self.correctPoint(end)
            if endIndex != self.index:
                continue
            yield endLocKey

    def getCostsFromWaypoints(self, locKey):
        point = self.correctPoint((self.index, locKey))
        for waypoint, cost in self.combo.getCostsFromWaypoints(point).items():
            yield self.correctPoint(waypoint), cost

    def getCostsToWaypoints(self, locKey):
        point = self.correctPoint((self.index, locKey))
        for waypoint, cost in self.combo.getCostsToWaypoints(point).items():
            yield self.correctPoint(waypoint), cost


def getRegionAndRelativePos(mapLayout, pos):
    i, j = MapLayout.getMapBlockIndices(*pos)
    blockDef = mapLayout.blocks[i][j]
    return blockDef, getPosRelativeToRegion(blockDef, pos)


def getPosRelativeToRegion(blockDef, pos):
    x = pos[0] - blockDef.rect.centerx
    y = pos[1] - blockDef.rect.centery
    if blockDef.layout and blockDef.layout.reversed:
        x = -x
    return (x, y)


def getAbsolutePosAndAngle(blockDef, relPos, angle):
    if blockDef.layout and blockDef.layout.reversed:
        relPos, angle = mirrorOffsetAndAngle(relPos, angle)
    x, y = relPos
    return (blockDef.rect.centerx + x, blockDef.rect.centery + y), angle


def mirrorOffsetAndAngle(relPos, angle):
    x, y = relPos
    return (-x, y), -angle


class RunTimePathFinder:
    def __init__(self, mapLayout, regionFactory=None, ddb=None, pfdb=None):
        if ddb is None:
            ddb = DiscretisationDatabase.get()
        self.ddb = ddb
        self.pfdb = pfdb
        self.layout = mapLayout

    def getRegion(self, regionName):
        if self.pfdb is None:
            self.pfdb = PathFindingDatabase.get()
        return self.pfdb.getRegion(regionName)

    def getHalfCombo(self, *args, **kwargs):
        if self.pfdb is None:
            self.pfdb = PathFindingDatabase.get()
        return self.pfdb.getHalfCombo(*args, **kwargs)

    def getDiscreteLocation(self, pos, grabAngle):
        blockDef, relPos = getRegionAndRelativePos(self.layout, pos)

        if blockDef.layout is None:
            return pos, grabAngle
        relPos, angle = self.getDiscreteLocationByRegion(
            blockDef.layout.forwardLayout, relPos, grabAngle)
        return getAbsolutePosAndAngle(blockDef, relPos, angle)

    def getDiscreteLocationByRegion(self, forwardLayout, pos, grabAngle):
        regionName = os.path.basename(forwardLayout.filename)
        try:
            (rx, ry), angle = self.ddb.getDiscretisationLocation(
                regionName, pos)
        except NoStationaryPointHere:
            self.discretisationKeyNotFound(regionName, pos, grabAngle)
            return pos, grabAngle

        # Double check for sanity
        x, y = pos
        if abs(x - rx) > PATH_FINDING_DISCRETISATION_UNIT or abs(y - ry)\
                > PATH_FINDING_DISCRETISATION_UNIT:
            log.error('Invalid discretisation data for %r:', regionName)
            log.error('\tx_in=%r\ty_in=%r\tx_out=%r\ty_out=%r', x, y, rx, ry)
            return pos, angle

        # Triple check for sanity
        check, _ = self.ddb.getDiscretisationLocation(regionName, (rx, ry))
        if check != (rx, ry):
            log.error(
                'discrete point from database is not within its unit: %s:%s',
                regionName, DiscretisationDatabase.getLocKey(pos))
            return pos, grabAngle
        return (rx, ry), angle

    def discretisationKeyNotFound(self, regionName, pos, grabAngle):
        log.error('pos=%r\tangle=%r', pos, grabAngle)
        log.error(
            'point not found in discretisation locations for %r', regionName)

    def getPossibleActions(self, player):
        if not player.isStationary():
            return [PathFindingRoute(player)]

        try:
            end = self.getStationaryPoint(player)
        except NoStationaryPointHere:
            return []

        result = []
        for edge in end.outwardEdges():
            route = PathFindingRoute(player)
            route.extendWithEdge(edge)
            result.append(route)
        return result

    def getStationaryPoint(self, playerState):
        return StationaryPoint.fromPlayerState(self, playerState)

    def getNearbyRoute(self, pos):
        blockDef, relPos = getRegionAndRelativePos(self.layout, pos)
        locKey = DiscretisationDatabase.getLocKey(relPos)
        region = self.getRegion(blockDef.layout.name)
        startKey, path, routeFlipped = region.getNearbyRoute(relPos)
        if routeFlipped:
            startKey = flipKey(startKey)
        startPoint = StationaryPoint(self, blockDef, startKey)
        actions = PathFindingAction.decodeGroup(
            path, routeFlipped ^ blockDef.layout.reversed)
        return startPoint, actions


class StationaryPoint:
    '''
    Represents a point where a bot may be stationary somewhere on the map.
    Used as intermediate points in pathfinding.
    '''

    def __init__(self, pathFinder, blockDef, locKey):
        self.pathFinder = pathFinder
        self.blockDef = blockDef
        self.locKey = locKey
        regionName = blockDef.layout.name
        self.region = pathFinder.getRegion(regionName)
        self.regionFlipped = blockDef.layout.reversed

        relPos, angle = pathFinder.ddb.getDiscretisationLocationByKey(
            regionName, locKey)
        self.pos, self.angle = getAbsolutePosAndAngle(blockDef, relPos, angle)

    def __repr__(self):
        return '{}: {}@{}'.format(
            type(self).__name__, self.getRegionIndices(), self.locKey)

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.blockDef == other.blockDef and self.locKey == other.locKey

    def __hash__(self):
        return hash(self.blockDef) ^ hash(self.locKey)

    @classmethod
    def fromPlayerState(cls, pathFinder, playerState):
        if not playerState.isStationary():
            raise RuntimeError('Player is not stationary')
        return cls.fromPos(pathFinder, playerState.pos)

    @classmethod
    def fromPos(cls, pathFinder, pos):
        mapLayout = pathFinder.layout
        blockDef, relPos = getRegionAndRelativePos(mapLayout, pos)
        locKey = DiscretisationDatabase.getLocKey(relPos)
        return cls(pathFinder, blockDef, locKey)

    def getRegionIndices(self):
        return self.blockDef.indices

    def outwardEdges(self):
        '''
        Yields (ticks, actionList, stationaryPoint)
        '''
        return self._getDirectionalEdges(
            self.region.getOutwardEdges(self.locKey),
            lambda halfCombo: halfCombo.getOutwardEdges(self.locKey))

    def inwardEdges(self):
        '''
        Yields (ticks, actionList, stationaryPoint)
        '''
        return self._getDirectionalEdges(
            self.region.getInwardEdges(self.locKey),
            lambda halfCombo: halfCombo.getInwardEdges(self.locKey))

    def _getDirectionalEdges(self, regionEdges, halfComboEdgeGetter):
        # Iterate edges within this region
        for ticks, key, path, flipPath in regionEdges:
            point = StationaryPoint(self.pathFinder, self.blockDef, key)
            actions = PathFindingAction.decodeGroup(
                path, flipPath ^ self.regionFlipped)
            yield ticks, actions, point

        # Iterate edges that leave this region
        for otherBlockDef, halfCombo in self.blocksAndCombos():
            for ticks, leaveRegion, key, actions in halfComboEdgeGetter(
                    halfCombo):
                blockDef = otherBlockDef if leaveRegion else self.blockDef
                point = StationaryPoint(self.pathFinder, blockDef, key)
                yield ticks, actions, point

    def blocksAndCombos(self):
        '''
        Yields (blockDef, halfCombo) for each combination that this point
        can reach, or that can reach this point.
        '''
        waypoints = set(self.region.getCostsToWaypoints(self.locKey))
        waypoints.update(self.region.getCostsFromWaypoints(self.locKey))
        directions = {
            d for w in waypoints
            for d in DIRECTIONS_BY_WAYPOINT[self.region.name, w]}
        borderDirection = self.region.isBorderPoint(self.locKey)
        if borderDirection and borderDirection != MULTIPLE:
            directions.add(borderDirection)

        if self.regionFlipped:
            directions = {HORIZONTAL_OPPOSITE[d] for d in directions}
        for direction in directions:
            result = self.getBlockDefAndCombo(direction)
            if result != (None, None):
                yield result

    def adjacentBlockDefsAndHalfCombos(self):
        for direction in DIRECTIONS:
            result = self.getBlockDefAndCombo(direction)
            if result != (None, None):
                yield result

    def getBlockDefAndCombo(self, direction):
        i, j = shiftIndices(self.blockDef.indices, direction)
        blocks = self.pathFinder.layout.blocks
        if (not 0 <= i < len(blocks)) or not (0 <= i <= len(blocks[0])):
            return None, None
        try:
            blockDef = blocks[i][j]
        except IndexError:
            return None, None

        if not blockDef.layout:
            return None, None

        flip2 = blockDef.layout.reversed
        return blockDef, self.pathFinder.getHalfCombo(
            self.blockDef.layout, blockDef.layout,
            self.regionFlipped, flip2, direction)

    def getCostsToWaypoints(self):
        '''
        :return: dict of concreteWaypoint: ticks for all waypoints for which
            this point has precalculated costs.
        '''
        result = {}
        for locKey, cost in self.region.getCostsToWaypoints(
                self.locKey).items():
            waypoint = StationaryPoint(self.pathFinder, self.blockDef, locKey)
            result[waypoint] = cost
        for blockDef, halfCombo in self.adjacentBlockDefsAndHalfCombos():
            for (index, locKey), cost in halfCombo.getCostsToWaypoints(
                    self.locKey):
                wBlockDef = self.blockDef if index == halfCombo.index else blockDef
                waypoint = StationaryPoint(self.pathFinder, wBlockDef, locKey)
                result[waypoint] = cost
        return result

    def getCostsFromWaypoints(self):
        '''
        :return: dict of concreteWaypoint: ticks for all waypoints for which
            this point has precalculated costs.
        '''
        result = {}
        for locKey, cost in self.region.getCostsFromWaypoints(
                self.locKey).items():
            waypoint = StationaryPoint(self.pathFinder, self.blockDef, locKey)
            result[waypoint] = cost
        for blockDef, halfCombo in self.adjacentBlockDefsAndHalfCombos():
            for (index, locKey), cost in halfCombo.getCostsFromWaypoints(
                    self.locKey):
                wBlockDef = self.blockDef if index == halfCombo.index else blockDef
                waypoint = StationaryPoint(self.pathFinder, wBlockDef, locKey)
                result[waypoint] = cost
        return result


class BuildTimePathFinder(RunTimePathFinder):
    def __init__(self, builder, mapLayout):
        self.builder = builder
        super().__init__(mapLayout)

    def discretisationKeyNotFound(self, regionName, pos, grabAngle):
        self.builder.addCollisionPoint(regionName, pos, grabAngle)


_cachedLayoutDB = None

def getLayoutDB():
    global _cachedLayoutDB
    if not _cachedLayoutDB:
        _cachedLayoutDB = LayoutDatabase(custom=False)
    return _cachedLayoutDB


if __name__ == '__main__':
    from trosnoth.utils.utils import initLogging
    initLogging(debug=True)
    builder = PathFindingStoreBuilder()

    try:
        builder.build()
    except Exception:
        log.exception('Error while building pathfinding database')
    builder.shell()
else:
    log.setLevel(logging.ERROR)
