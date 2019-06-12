import logging

log = logging.getLogger(__name__)


enabled = False


# Treat every incoming instruction as if we've observed a delay of at least
# this number of ticks.
forceDelay = 0

# Slows down the universe game loop by this factor
slowMotionFactor = 1

# Maximum number of shots allowed on the map - for debugging shots
# (ignored if falsey)
shotLimit = None


# Displays where the local server thinks sprites are
showSpriteCircles = False

# Displays obstacle locations
showObstacles = True


def getSpriteCircles():
    '''
    Returns a sequence of (point, radius) pairs for positions in the server
    universe where sprites are.
    '''
    if serverUniverse is None:
        return
    for unit in serverUniverse.getCollectableUnits():
        if localPlayerDelay == 0:
            pos = unit.pos
        else:
            if localPlayerDelay >= len(unit.history) or localPlayerDelay < 0:
                continue
            pos = unit.history[-localPlayerDelay]
        yield (pos, unit.playerCollisionTolerance)

    for player in serverUniverse.playerWithId.values():
        yield (player.pos, 3)


# Updated by other parts of the code
localPlayerDelay = 0
localPlayerId = None
serverUniverse = None

# This flag is set to True when globaldebug is enabled and the middle mouse
# button is being held.
debugKey = False
