#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Base detection parser class
#
import numpy as np
from .._base import *

__all__ = ['ParserType', 'DetectionParser']


class DetectionParser(Parser):
    """ This is a generic detections parser class.
    Custom parsers should inherit from this class and overwrite the :func:`~brambox.io.detection._base.DetectionParser.serialize` and
    :func:`~brambox.io.detection._base.DetectionParser.deserialize` functions, as well as the necessary parameters.
    """
    def __init__(self):
        super().__init__()
        self.data = {
            'image': [],
            'class_label': [],
            'id': [],
            'x_top_left': [],
            'y_top_left': [],
            'width': [],
            'height': [],
            'confidence': [],
        }

    def append(self, image, class_label, x_top_left, y_top_left, width, height, confidence, id=None):
        """ Append a detection to the data.

        Args:
            image (string): Image identifier
            class_label (string): Class label
            x_top_left (number): X pixel coordinate of the top left corner of the bounding box
            y_top_left (number): Y pixel coordinate of the top left corner of the bounding box
            width (number): Width of the bounding box in pixels
            height (number): Height of the bounding box in pixels
            confidence (number): Confidence value of the detection
            id (number, optional): unique id of the bounding box
        """
        self.images.add(image)
        self.data['image'].append(image)
        self.data['class_label'].append(class_label)
        self.data['id'].append(id if id is not None else np.nan)
        self.data['x_top_left'].append(x_top_left)
        self.data['y_top_left'].append(y_top_left)
        self.data['width'].append(width)
        self.data['height'].append(height)
        self.data['confidence'].append(confidence)
