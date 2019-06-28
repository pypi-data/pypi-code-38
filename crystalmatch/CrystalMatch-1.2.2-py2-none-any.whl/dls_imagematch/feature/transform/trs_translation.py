from CrystalMatch.dls_util.imaging import Image
from CrystalMatch.dls_imagematch.feature.transform.transformation import Transformation


class Translation(Transformation):
    def __init__(self, translation):
        Transformation.__init__(self)
        self._translation = translation

    def translation(self):
        return self._translation

    def transform_points(self, points):
        transformed = [p - self._translation for p in points]
        return transformed

    def inverse_transform_points(self, points):
        transformed = [p + self._translation for p in points]
        return transformed
