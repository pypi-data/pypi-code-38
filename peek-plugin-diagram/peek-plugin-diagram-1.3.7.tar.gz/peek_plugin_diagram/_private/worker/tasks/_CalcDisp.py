import logging
from typing import List, Dict

import ujson
from peek_plugin_diagram._private.storage.ModelSet import ModelCoordSet

logger = logging.getLogger(__name__)


def _scaleDispGeomWithCoordSet(points: List[float],
                               coordSet: ModelCoordSet) -> List[float]:
    return _scaleDispGeom(points,
                          coordSet.multiplierX,
                          coordSet.multiplierY,
                          coordSet.offsetX,
                          coordSet.offsetY)


def _scaleDispGeom(points: List[float],
                   mx: float, my: float, ox: float, oy: float) -> List[float]:
    newGeom: List[float] = []

    for xi in range(0, len(points), 2):
        x = points[xi] * mx + ox
        y = points[xi + 1] * my + oy

        newGeom += [x, y]

    return newGeom


def _createHashId(dispDict: Dict) -> str:
    # Copy the input dict and pop the ID (we don't hash it)
    hashIdDict = dispDict.copy()

    # Delete the
    del hashIdDict['id']

    # Delete the branch id
    if 'bi' in hashIdDict: del hashIdDict['bi']

    # Delete the branch stage
    if 'bs' in hashIdDict: del hashIdDict['bs']

    # Delete the hash id
    if 'hid' in hashIdDict: del hashIdDict['hid']

    # Delete the replaces hash id
    if 'rid' in hashIdDict: del hashIdDict['rid']

    # Delete the group id
    if 'gi' in hashIdDict: del hashIdDict['gi']

    # Hash the actual content of the disp, and convert the integer to a string
    hashId = hash(ujson.dumps(hashIdDict, sort_keys=True))
    hashIdStr = __num_encode(hashId)

    # Return the hash
    return hashIdStr


import string

ALPHABET = string.ascii_uppercase + string.ascii_lowercase + \
           string.digits + '-_'
ALPHABET_REVERSE = dict((c, i) for (i, c) in enumerate(ALPHABET))
BASE = len(ALPHABET)
SIGN_CHARACTER = '$'


def __num_encode(n):
    if n < 0:
        return SIGN_CHARACTER + __num_encode(-n)
    s = []
    while True:
        n, r = divmod(n, BASE)
        s.append(ALPHABET[r])
        if n == 0: break
    return ''.join(reversed(s))


def __num_decode(s):
    if s[0] == SIGN_CHARACTER:
        return -__num_decode(s[1:])
    n = 0
    for c in s:
        n = n * BASE + ALPHABET_REVERSE[c]
    return n
