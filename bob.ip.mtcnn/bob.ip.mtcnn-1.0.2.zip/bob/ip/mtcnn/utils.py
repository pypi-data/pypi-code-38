import numpy
from bob.ip.facedetect import BoundingBox


def rectangle2bounding_box2(raw_bounding_boxes):
    """
    Converts a bob.ip.facedetect.BoundingBox
    """

    def convert_one(bb):
        assert len(bb)==5
#        topleft = (bb[1], bb[0])
        topleft = (numpy.max([0, bb[1]]), numpy.max([0, bb[0]]))
        size = (bb[3] - bb[1], bb[2] - bb[0])
        return BoundingBox(topleft, size)

    # If it is only one
    if raw_bounding_boxes.ndim == 1:
        return convert_one(raw_bounding_boxes)
    else:
        bounding_boxes = []
        for b in raw_bounding_boxes:
            bounding_boxes.append(convert_one(b))

        return bounding_boxes



# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
