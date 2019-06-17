import numpy as np


def coordinates_to_width_height(coordinates: np.array) -> np.array:
    """
    Transform a bounding box of the form (x0, y0, x1, y1) into a bounding box
    of the form (x, y, w, h)
    Args:
        coordinates: A numpy array containing a bounding box of the form [x0, y0, x1, y1]

    Returns:
        A numpy array containing a bounding box of the form [x, y, w, h]
    """
    pass


def width_height_to_coordinates(xywh: np.array) -> np.array:
    """
    Transform a bounding box of the form (x, y, w, h)into a bounding box
    of the form (x0, y0, x1, y1)
    Args:
        xywh: A numpy array containing a bounding box of the form [x, y, w, h]

    Returns:
        A numpy array containing a bounding box of the form [x0, y0, x1, y1]
    """
    return np.array(
        [xywh[0], xywh[1], xywh[0] + xywh[2], xywh[1] + xywh[3]]
    )
