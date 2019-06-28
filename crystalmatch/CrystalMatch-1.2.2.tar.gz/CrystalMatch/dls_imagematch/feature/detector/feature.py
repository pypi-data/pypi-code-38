from CrystalMatch.dls_util.shape import Point


class Feature:
    def __init__(self, keypoint, descriptor):
        self._keypoint = keypoint
        self._descriptor = descriptor

    def point(self):
        """ The image coordinates of the feature. """
        return Point(self._keypoint.pt[0], self._keypoint.pt[1])

    def size(self):
        """ The diameter of the meaningful keypoint neighborhood. """
        return self._keypoint.size

    def angle(self):
        """ Computed orientation of the keypoint (-1 if not applicable). Its possible values are in a range
        [0,360) degrees. It is measured relative to image coordinate system (y-axis is directed downward),
        ie in clockwise. """
        return self._keypoint.angle

    def strength(self):
        return self._keypoint.response

    def keypoint(self):
        return self._keypoint

    def descriptor(self):
        return self._descriptor
