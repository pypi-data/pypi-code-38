import numpy
from bob.ip.facedetect import BoundingBox
import dlib


def bounding_box_2_rectangle(bb):
    """
    Converrs a bob.ip.facedetect.BoundingBox to dlib.rectangle
    """

    assert isinstance(bb, BoundingBox)
    return dlib.rectangle(bb.topleft[1], bb.topleft[0],
                          bb.bottomright[1], bb.bottomright[0])


def rectangle_2_bounding_box(rectangle):
    """
    Converts dlib.rectangle to bob.ip.facedetect.BoundingBox 
    """

    assert isinstance(rectangle, dlib.rectangle)

    top  = numpy.max( [0, rectangle.top()] )
    left = numpy.max( [0, rectangle.left()])
    height = numpy.min( [top,  rectangle.height()] )
    width  = numpy.min( [left, rectangle.width() ] )

    return BoundingBox((top, left),
                       (height, width))
    


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
