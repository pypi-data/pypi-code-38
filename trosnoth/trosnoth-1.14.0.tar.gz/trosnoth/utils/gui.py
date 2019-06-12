import logging

log = logging.getLogger(__name__)


def align(
        node, left=None, right=None, top=None, bottom=None,
        midX=None, midZ=None, x=None, z=None):
    '''
    Aligns the position of the given DirectGUI element based on the given
    parameters.

    midX and midZ specify the location of the centre of the element, while x
    and z specify the location of the origin of the element.
    '''
    if sum([
            left is not None, right is not None,
            midX is not None, x is not None]) > 1:
        raise TypeError('may only give one of left, right, midX and x')
    if sum([
            top is not None, bottom is not None,
            midZ is not None, z is not None]) > 1:
        raise TypeError('may only give one of top, bottom, midZ and z')

    xScale, yScale, zScale = node.getScale()
    lLeft, lRight, lBottom, lTop = node.guiItem.getFrame()

    if left is not None:
        node.setX(left - lLeft * xScale)
    elif right is not None:
        node.setX(right - lRight * xScale)
    elif x is not None:
        node.setX(x)
    elif midX is not None:
        node.setX(midX - 0.5 * xScale * (lRight + lLeft))

    if top is not None:
        if bottom is not None:
            raise TypeError('may only specify one of top and bottom')
        node.setZ(top - lTop * zScale)
    elif bottom is not None:
        node.setZ(bottom - lBottom * zScale)
    elif z is not None:
        node.setZ(z)
    elif midZ is not None:
        node.setZ(midZ - 0.5 * xScale * (lTop + lBottom))
