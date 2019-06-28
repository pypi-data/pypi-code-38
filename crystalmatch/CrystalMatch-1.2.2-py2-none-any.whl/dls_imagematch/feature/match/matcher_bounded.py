from __future__ import division

from CrystalMatch.dls_imagematch.feature.match.matcher import FeatureMatcher
from CrystalMatch.dls_imagematch.feature.match.match import FeatureMatch


class BoundedFeatureMatcher(FeatureMatcher):
    """ Specialization of feature matcher which allows user to specify sub regions of the two images.
    When performing the matching operations, only features in these regions will be considered. """
    def __init__(self, image1, image2, detector_config, image1_rect, image2_rect):
        FeatureMatcher.__init__(self, image1, image2, detector_config)

        if image1_rect is None:
            image1_rect = image1.bounds()

        if image2_rect is None:
            image2_rect = image2.bounds()

        self.image1 = image1.crop(image1_rect)
        self.image2 = image2.crop(image2_rect)

        self.image1_offset = image1_rect.top_left()
        self.image2_offset = image2_rect.top_left()

    def _matches_from_raw(self, raw_matches, keypoints1, keypoints2, method):
        matches = FeatureMatch.from_cv2_matches(raw_matches, keypoints1, keypoints2, method)
        for match in matches:
            match.set_offsets(self.image1_offset, self.image2_offset)

        return matches
