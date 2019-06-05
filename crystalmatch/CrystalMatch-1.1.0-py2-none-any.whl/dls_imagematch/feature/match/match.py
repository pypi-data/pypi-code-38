from CrystalMatch.dls_util.shape import Point


class FeatureMatch:
    """ Wrapper for the match and keypoint objects produced by the OpenCV feature matching routines. Makes
    it easier to use and pass around this data.
    """
    def __init__(self, match, feature1, feature2, detector):
        self._match = match
        self._feature1 = feature1
        self._feature2 = feature2
        self._detector = detector
        self._offset1 = Point(0, 0)
        self._offset2 = Point(0, 0)
        self._point2_projected = None
        self._included_in_transformation = True

    def method(self):
        return self._detector.detector()

    def reprojection_error(self):
        if self._point2_projected is not None:
            return self.point2().distance_to(self._point2_projected)
        else:
            return 1e6

    def is_in_transformation(self):
        return self._included_in_transformation

    def distance(self):
        return self._match.distance * self._detector.extractor_distance_factor()

    def point1(self):
        return self.image_point1() + self._offset1

    def point2(self):
        return self.image_point2() + self._offset2

    def point2_projected(self):
        return self._point2_projected

    def image_point1(self):
        return self._feature1.point()

    def image_point2(self):
        return self._feature2.point()

    def set_offsets(self, offset1, offset2):
        self._offset1 = offset1
        self._offset2 = offset2

    def set_point2_projected(self, point):
        self._point2_projected = point

    def set_in_transformation(self, in_transformation):
        self._included_in_transformation = in_transformation

    @staticmethod
    def from_cv2_matches(cv2_matches, features1, features2, detector):
        func = FeatureMatch.from_cv2_match
        single_matches = [func(match, features1, features2, detector) for match in cv2_matches]

        # Filter out matches whose keypoint distances are too large
        filtered = []
        for match in single_matches:
            if match.distance() < detector.keypoint_limit():
                filtered.append(match)

        return filtered

    @staticmethod
    def from_cv2_match(cv2_match, features1, features2, detector):
        f1 = features1[cv2_match.queryIdx]
        f2 = features2[cv2_match.trainIdx]
        cv2_match = FeatureMatch(cv2_match, f1, f2, detector)
        return cv2_match
