from ..helpers.point import Point, CenterPosition


class Roi:
    """ A class to manage ROIs in DICOM images

    Args:
        center : The coordinates for the center position (x-, y-, and z-index) of the ROI

    Attributes:
        Center : The coordinates for the center position (x-, y-, and z-index) of the ROI

    """
    def __init__(self, center: CenterPosition):
        if not isinstance(center, Point) and not isinstance(center, dict):
            raise TypeError("The center must be given as a point or a dict")

        if isinstance(center, Point):
            self.Center = center
        else:
            if 'x' not in center.keys() or 'y' not in center.keys() or 'z' not in center.keys():
                raise ValueError(("The center dict must be on the form dict(x: Union[float, int], y: Union[float, int],"
                                  " z: Optional[Union[float, int]}"))
            z = center.get('z')
            if z is not None:
                z = float(z)
            self.Center = Point(x=float(center.get('x')), y=float(center.get('y')), z=z)

        if sum([self.Center.x is None, self.Center.y is None]) > 0:
            raise ValueError("At least the x and y positions of the center must be specified")
