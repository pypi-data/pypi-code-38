from typing import Tuple


class Point(object):
    """A 2d point.
    Has x and y."""

    def __init__(self,  # type: Point
                 x,  # type: float
                 y  # type: float
                 ):
        self.x = x
        self.y = y

    def midpoint(self, other):
        # type: (Point, Point) -> Point
        """Return a point between two points."""

        return Point(
            (self.x + other.x) / 2.0,
            (self.y + other.y) / 2.0
        )

    def flatten(self):
        # type: (Point) -> Tuple[float, float]
        """Flattens a point into (x,y) coords, respectively."""
        return self.x, self.y
