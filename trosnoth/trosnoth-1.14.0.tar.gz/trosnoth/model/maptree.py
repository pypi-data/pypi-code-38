from math import log


KEY_INDEX = 0
RECT_INDEX = 1
CONTENTS_INDEX = 2

POLYGON_KEY = b'p'
LEDGE_KEY = b'l'
NODE_KEY = b'n'
EMPTY_KEY = b'e'


def getRelevantLeaves(tree, offset, reversed, left, top, right, bottom):
    x0 = left - offset[0]
    y0 = top - offset[1]
    x1 = right - offset[0]
    y1 = bottom - offset[1]
    if reversed:
        x0, x1 = -x1, -x0

    return getRelevantLeavesFromRelativeCoordinates(
        tree, offset, reversed, x0, y0, x1, y1)


def getRelevantLeavesFromRelativeCoordinates(
        tree, offset, reversed, x0, y0, x1, y1):
    kind = tree[KEY_INDEX]
    if kind == EMPTY_KEY:
        return

    u0, v0, u1, v1 = tree[RECT_INDEX]
    if u0 > x1 or x0 > u1 or v0 > y1 or y0 > v1:
        return

    if kind == NODE_KEY:
        for child in tree[CONTENTS_INDEX:]:
            yield from getRelevantLeavesFromRelativeCoordinates(
                child, offset, reversed, x0, y0, x1, y1)
    else:
        yield LeafNode(tree, offset, reversed)


class LeafNode(object):
    def __init__(self, leaf, offset, reversed):
        self.data = leaf
        self.offset = offset
        self.reversed = reversed

    def isLedge(self):
        return self.data[KEY_INDEX] == LEDGE_KEY

    def getEdges(self):
        points = list(self.getPoints())
        if len(points) < 2:
            return

        x0, y0 = x1, y1 = points[0]
        for x2, y2 in points[1:]:
            if (x2, y2) == (x1, y1):
                continue
            yield (x1, y1, x2, y2)
            x1, y1 = x2, y2

        if self.data[KEY_INDEX] == POLYGON_KEY:
            # Close the loop
            yield (x2, y2, x0, y0)

    def dataPointToWorld(self, point):
        y = self.offset[1] + point[1]
        if self.reversed:
            x = self.offset[0] - point[0]
        else:
            x = self.offset[0] + point[0]
        return (x, y)

    def getPoints(self):
        if self.reversed:
            for point in self.data[:CONTENTS_INDEX - 1:-1]:
                yield self.dataPointToWorld(point)
        else:
            for point in self.data[CONTENTS_INDEX:]:
                yield self.dataPointToWorld(point)


def buildMapTree(polygons, oneWayPlatforms):
    '''
    Builds a map tree data structure from the given set of convex polygonal
    obstacles and one-way platforms.
    '''
    things = [buildPolygon(p) for p in polygons]
    things += [buildOneWayPlatform(l) for l in oneWayPlatforms]
    return buildBinaryTreeFromLeaves(things)


def buildBinaryTreeFromLeaves(things):
    if len(things) < 1:
        return buildEmptyNode()
    if len(things) == 1:
        return things[0]
    if len(things) == 2:
        return buildTreeNode(things)

    # Find the best place to divide the nodes
    # Try dividing on x-axis
    xThings = sorted(
        things, key=lambda thing: rectCentre(thing[RECT_INDEX])[0])
    bestX = None
    bestXCost = None
    for i in range(1, len(things)):
        side1 = buildTreeNode(xThings[:i])
        side2 = buildTreeNode(xThings[i:])
        cost = rectArea(side1[RECT_INDEX]) * log(i) + rectArea(
            side2[RECT_INDEX]) * log(len(things) - i)
        if bestXCost is None or cost < bestXCost:
            bestXCost = cost
            bestX = i

    # Try dividing on x-axis
    yThings = sorted(
        things, key=lambda thing: rectCentre(thing[RECT_INDEX])[1])
    bestY = None
    bestYCost = None
    for i in range(1, len(things)):
        side1 = buildTreeNode(yThings[:i])
        side2 = buildTreeNode(yThings[i:])
        cost = rectArea(side1[RECT_INDEX]) * log(i) + rectArea(
            side2[RECT_INDEX]) * log(len(things) - i)
        if bestYCost is None or cost < bestYCost:
            bestYCost = cost
            bestY = i

    # Decide which way to split
    if bestXCost < bestYCost:
        return buildTreeNode([
            buildBinaryTreeFromLeaves(xThings[:bestX]),
            buildBinaryTreeFromLeaves(xThings[bestX:])])
    return buildTreeNode([
        buildBinaryTreeFromLeaves(yThings[:bestY]),
        buildBinaryTreeFromLeaves(yThings[bestY:])])


def buildPolygon(points):
    return (POLYGON_KEY, boundingRectOfPoints(points)) + tuple(points)


def buildOneWayPlatform(points):
    return (LEDGE_KEY, boundingRectOfPoints(points)) + tuple(points)


def boundingRectOfPoints(points):
    x0, y0 = x1, y1 = points[0]
    for x, y in points[1:]:
        x0 = min(x0, x)
        y0 = min(y0, y)
        x1 = max(x1, x)
        y1 = max(y1, y)
    return (x0, y0, x1, y1)


def rectUnion(rects):
    points = []
    for x0, y0, x1, y1 in rects:
        points.append((x0, y0))
        points.append((x1, y1))
    return boundingRectOfPoints(points)


def rectCentre(rect):
    x0, y0, x1, y1 = rect
    return ((x0 + x1) / 2, (y0 + y1) / 2)


def rectArea(rect):
    x0, y0, x1, y1 = rect
    return (x1 - x0) * (y1 - y0)


def buildTreeNode(children):
    children = [child for child in children if child[KEY_INDEX] != EMPTY_KEY]
    if not children:
        return buildEmptyNode()
    if len(children) == 1:
        return children[0]

    boundingRect = rectUnion(child[RECT_INDEX] for child in children)
    return (NODE_KEY, boundingRect) + tuple(children)


def buildEmptyNode():
    return (EMPTY_KEY,)


BLOCK_TYPE = b't'
SYMMETRICAL = b's'
BLOCKED = b'b'
CONTENTS = b'c'

def packBlock(blockType, symmetrical, blocked, tree):
    return {
        BLOCK_TYPE: blockType,
        SYMMETRICAL: symmetrical,
        BLOCKED: blocked,
        CONTENTS: tree,
    }


class BlockLayout(object):
    def __init__(self, data):
        self.blockType = data[BLOCK_TYPE]
        self.symmetrical = data[SYMMETRICAL]
        self.blocked = data[BLOCKED]
        self.tree = data[CONTENTS]
