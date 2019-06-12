#!/usr/bin/env python3

'''
Migrates a Trosnoth map block from the old .block JSON-like file format to
the new .trosblock format.

Note that this will be obsoleted after we move to using room-based tiling
rather than map blocks.
'''

import os.path
import sys
import traceback

from trosnoth.model.mapLayout import BLOCK_FILES
from trosnoth.model.maptree import buildMapTree, packBlock
from trosnoth.utils.unrepr import unrepr


EDGE_PATHS = {
    ('top', True): [
        ((0, 60), (0, 0), (1024, 0), (1024, 60)),
        ((384, 384), (128, 384)),
        ((896, 384), (640, 384)),
    ],
    ('top', False): [
        ((0, 60), (0, 0), (60, 0)),
        ((256, 0), (768, 0)),
        ((964, 0), (1024, 0), (1024, 60)),
        ((384, 384), (128, 384)),
        ((896, 384), (640, 384)),
    ],
    ('btm', True): [
        ((1024, 324), (1024, 384), (0, 384), (0, 324)),
        ((128, 0), (384, 0)),
        ((640, 0), (896, 0)),
    ],
    ('btm', False): [
        ((60, 384), (0, 384), (0, 324)),
        ((768, 384), (256, 384)),
        ((1024, 324), (1024, 384), (964, 384)),
        ((128, 0), (384, 0)),
        ((640, 0), (896, 0)),
    ],
    ('fwd', True): [
        ((452, 0), (512, 0), (512, 60)),
        ((60, 384), (0, 384), (0, 324)),
    ],
    ('fwd', False): [
        ((452, 0), (512, 0), (512, 60)),
        ((60, 384), (0, 384), (0, 324)),
    ],
    ('bck', True): [
        ((0, 60), (0, 0), (60, 0)),
        ((512, 324), (512, 384), (452, 384))
    ],
    ('bck', False): [
        ((0, 60), (0, 0), (60, 0)),
        ((512, 324), (512, 384), (452, 384))
    ],
}


def main():
    filenames = sys.argv[1:]
    if not filenames:
        print('Please specify at least one .block file')
        sys.exit(1)

    for filename in filenames:
        try:
            migrate(filename)
        except Exception:
            traceback.print_exc()


def migrate(filename):
    print(filename)
    with open(filename, 'r') as f:
        data = unrepr(f.read())
    #  (['platforms', 'obstacles'])
    blockType = BLOCK_FILES[data['blockType']]
    symmetrical = data.get('symmetrical', False)
    blocked = data['blocked']

    polygons = []
    chains = data['obstacles'] + EDGE_PATHS[blockType, blocked]
    while chains:
        chain = chains.pop(0)
        if chain[0] == chain[-1]:
            polygons.append(chain[:-1])
            continue

        for other in chains:
            if chain[0] == other[-1]:
                break
        else:
            print('  WARNING: Ignoring unclosed obstacle: %r' % (chain,))
            continue
        chains.remove(other)
        chains.append(other + chain[1:])

    convexPolygons = convexify(polygons)
    platforms = [((x, y), (x + w, y)) for (x, y), w in data['platforms']]
    blockContents = buildMapTree(convexPolygons, platforms)

    output = packBlock(blockType, symmetrical, blocked, blockContents)

    base, ext = os.path.splitext(filename)
    with open(base + '.trosblock', 'w') as f:
        f.write(repr(output))

    # # DEBUG:
    # data2 = dict(data)
    # data2['obstacles'] = [p + (p[0],) for p in convexPolygons]
    # with open(base + '-debug.block', 'w') as f:
    #     f.write(repr(data2))


def convexify(polygons):
    # Uses Hertel-Mehlhorn algorithm
    result = []

    for polygon in polygons:
        # Check if the polygon is already convex
        for i, p1 in enumerate(polygon):
            p0 = polygon[i - 1]
            p2 = polygon[0] if i + 1 == len(polygon) else polygon[i + 1]
            if isReflex(p0, p1, p2):
                break
        else:
            # Already convex
            result.append(polygon)
            continue

        pending = triangulate(polygon)
        while pending:
            poly1 = pending.pop(0)
            for i, p1 in enumerate(poly1):
                p2 = poly1[i + 1 - len(poly1)]

                for j, poly2 in enumerate(pending):
                    for k, q1 in enumerate(poly2):
                        q2 = poly2[k + 1 - len(poly2)]
                        if p1 == q2 and p2 == q1:
                            break
                    else:
                        continue
                    break
                else:
                    continue

                # p1 -> p2 matches q1 -> q2
                p0 = poly1[i - 1]
                p3 = poly1[i + 2 - len(poly1)]
                q0 = poly2[k - 1]
                q3 = poly2[k + 2 - len(poly2)]
                if not isConvex(p0, p1, q3):
                    continue
                if not isConvex(q0, p2, p3):
                    continue

                # Join this edge
                pending.pop(j)
                pending.insert(
                    0, poly1[:i] + poly2[k + 1:] + poly2[:k] + poly1[i + 1:])

                break
            else:
                result.append(poly1)
    return result


def triangulate(polygon):
    points = list(polygon)
    if len(points) <= 3:
        return [points]

    result = []

    while len(points) > 3:
        for i, p1 in enumerate(points):
            tritest = False
            p0 = points[i - 1]
            p2 = points[i + 1 - len(points)]
            if not isConvex(p0, p1, p2):
                continue

            ignore = (p0, p1, p2)
            for q in points:
                if q in ignore:
                    continue
                if inTriangle(p0, p1, p2, q):
                    break
            else:
                # Found ear!
                break
        else:
            assert False, 'Polygon is inside out!'

        result.append((p0, p1, p2))
        del points[i]

    result.append(tuple(points))

    return result


def inTriangle(a, b, c, p):
    L = [0, 0, 0]
    eps = 0.0000001
    # calculate barycentric coefficients for point p
    # eps is needed as error correction since for very small distances denom->0
    L[0] = ((b[1] - c[1]) * (p[0] - c[0]) + (c[0] - b[0]) * (p[1] - c[1])) \
           / (((b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])) + eps)
    L[1] = ((c[1] - a[1]) * (p[0] - c[0]) + (a[0] - c[0]) * (p[1] - c[1])) \
           / (((b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])) + eps)
    L[2] = 1 - L[0] - L[1]
    # check if p lies in triangle (a, b, c)
    for x in L:
        if x > 1 or x < 0:
            return False
    return True


def isConvex(p1, p2, p3):
    v = (p3[1] - p1[1]) * (p2[0] - p1[0]) - (p3[0] - p1[0]) * (p2[1] - p1[1])
    if v > 0:
        return True
    return False


def isReflex(p1, p2, p3):
    v = (p3[1] - p1[1]) * (p2[0] - p1[0]) - (p3[0] - p1[0]) * (p2[1] - p1[1])
    if v < 0:
        return True
    return False


if __name__ == '__main__':
    main()
