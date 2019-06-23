import logging
import math

import logging
from typing import Dict, List

from peek_plugin_diagram._private.storage.Display import DispText, \
    DispTextStyle, DispEllipse, DispGroup, DispGroupPointer
from peek_plugin_diagram._private.storage.ModelSet import ModelCoordSet, \
    ModelCoordSetGridSize

logger = logging.getLogger(__name__)


def makeGridKeysForDisp(coordSet: ModelCoordSet,
                        disp, geomJson,
                        textStyleById: Dict[int, DispTextStyle]) -> List[str]:
    points = geomJson

    if geomJson is None:
        logger.critical("geomJson is None : %s ", disp)
        return []

    # If it's a text shape with no text, ignore it
    if isinstance(disp, DispText) and not disp.text:
        return []

    gridKeys = []
    for gridSize in coordSet.gridSizes:
        # CHECK Declutter
        if isinstance(disp, DispGroup) and disp.level is None:
            # Skip the check if the DispGroup has no level. It will be in all levels.
            pass

        elif 0.0 > (min(gridSize.max, (disp.level.maxZoom - 0.00001))
                      - max(gridSize.min, disp.level.minZoom + 0.00001)):
            continue

        if (isinstance(disp, DispText)
            and _isTextTooSmall(disp, gridSize, textStyleById)):
            continue

        # If this is just a point shape/geom, then add it and continue
        if isinstance(disp, DispEllipse):
            minx, miny, maxx, maxy = _calcEllipseBounds(disp, points[0], points[1])

        elif len(points) == 2:  # 2 = [x, y]

            # This should be a text
            if not isinstance(disp, DispText) \
                    and not isinstance(disp, DispGroup) \
                    and not isinstance(disp, DispGroupPointer):
                logger.debug("TODO Determine size for disp type %s", disp.tupleType())

            # Texts on the boundaries of grids could be a problem
            # They will seem them if the pan over just a little.
            gridKeys.append(gridSize.makeGridKey(int(points[0] / gridSize.xGrid),
                                                 int(points[1] / gridSize.yGrid)))
            continue

        else:
            # Else, All other shapes
            # Get the bounding box
            minx, miny, maxx, maxy = _calcBounds(points)

        # If the size is too small to see at the max zoom, then skip it
        size = math.hypot(maxx - minx, maxy - miny)
        largestSize = size * gridSize.max
        if largestSize < gridSize.smallestShapeSize:
            continue

        # Round the grid X min/max
        minGridX = int(minx / gridSize.xGrid)
        maxGridX = int(maxx / gridSize.xGrid) + 1

        # Round the grid Y min/max
        minGridY = int(miny / gridSize.yGrid)
        maxGridY = int(maxy / gridSize.yGrid) + 1

        # Iterate through and create the grids.
        for gridX in range(minGridX, maxGridX):
            for gridY in range(minGridY, maxGridY):
                gridKeys.append(gridSize.makeGridKey(gridX, gridY))

    return gridKeys


def _pointToPixel(point: float) -> float:
    return point * 96 / 72


def _isTextTooSmall(disp, gridSize: ModelCoordSetGridSize,
                    textStyleById: Dict[int, DispTextStyle]) -> bool:
    """ Is Text Too Small

    This method calculates the size that the text will appear on the diagram at max zoom
    for the provided gird.

    We'll only work this out based on the height

    NOTE: This must match how it's rendered PeekDispRenderDelegateText.ts
    """

    fontStyle = textStyleById[disp.textStyleId]

    if disp.textHeight:
        lineHeight = disp.textHeight
    else:
        fontSize = fontStyle.fontSize * fontStyle.scaleFactor
        lineHeight = _pointToPixel(fontSize)

    if fontStyle.scalable:
        largestSize = lineHeight * gridSize.max
    else:
        largestSize = lineHeight

    return largestSize < gridSize.smallestTextSize


def _calcEllipseBounds(disp, x, y):
    """ Calculate the bounds of an ellipse

    """
    # NOTE: To do this accurately we should look at the start and end angles.
    # in the interest simplicity we're not going to.
    # We'll potentially include SMALLEST_SHAPE_SIZE / 2 as well, no big deal.

    minx = x - disp.xRadius
    maxx = x + disp.xRadius

    miny = y - disp.yRadius
    maxy = y + disp.yRadius

    return minx, miny, maxx, maxy


def _calcBounds(points: List[float]):
    minx = None
    maxx = None
    miny = None
    maxy = None

    for index, val in enumerate(points):
        isY = bool(index % 2)

        if isY:
            if miny is None or val < miny:
                miny = val

            if maxy is None or maxy < val:
                maxy = val

        else:
            if minx is None or val < minx:
                minx = val

            if maxx is None or maxx < val:
                maxx = val

    return minx, miny, maxx, maxy
