from shapely.geometry import Point


class ShapelyPoint:
    @staticmethod
    def from_latlong(latitude, longitude):
        return Point(longitude, latitude)


class LatLongPoint:
    @staticmethod
    def from_shapely_point(point: Point):
        return {
            "latitude": point.y,
            "longitude": point.x,
        }
