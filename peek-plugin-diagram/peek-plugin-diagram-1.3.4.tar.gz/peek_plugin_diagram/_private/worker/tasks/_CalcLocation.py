from collections import namedtuple

import logging
from typing import Optional, List

from peek_plugin_diagram._private.tuples.location_index.DispKeyLocationTuple import \
    DispKeyLocationTuple
from peek_plugin_diagram._private.worker.tasks._CalcGridForDisp import _calcBounds

logger = logging.getLogger(__name__)

CoordSetIdGridKeyTuple = namedtuple("CoordSetIdGridKeyTuple", ["coordSetId", "gridKey"])
DispData = namedtuple('DispData', ['json', 'levelOrder', 'layerOrder'])


def makeLocationJson(disp, geomArray: List[float]) -> Optional[str]:
    if geomArray is None:
        logger.critical("geomJson is None : %s ", disp)

    minx, miny, maxx, maxy = _calcBounds(geomArray)

    # Find the center point
    x = (minx + maxx) / 2
    y = (miny + maxy) / 2

    location = DispKeyLocationTuple(coordSetId=disp.coordSetId, dispId=disp.id, x=x, y=y)
    return location.toLocationJson()


def dispKeyHashBucket(modelSetKey: str, dispKey: str) -> str:
    """ Disp Key Hash Bucket

    This method create an int from 0 to 255, representing the hash bucket for this
    key.

    This is simple, and provides a reasonable distribution

    :param modelSetKey:
    :param dispKey:

    :return:

    """
    if not modelSetKey:
        raise Exception("modelSetKey is None or zero length")

    if not dispKey:
        raise Exception("dispKey is None or zero length")

    hash = 0
    for char in dispKey:
        hash = ((hash << 5) - hash) + ord(char)
        hash = hash | 0  # This is in the javascript code.

    hash = hash & 1023  # 1024 buckets

    return "%s:%s" % (modelSetKey, hash)
