from CrystalMatch.dls_util.shape import Polygon


class Transformation:
    """ Abstract base class for different types of transformation. """
    def __init__(self):
        pass

    def transform_points(self, points):
        raise NotImplementedError()

    def transform_image(self, image, output_size):
        raise NotImplementedError()

    def transform_polygon(self, polygon):
        vertices = polygon.vertices()
        transformed = self.transform_points(vertices)
        return Polygon(transformed)
