#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Base annotation parser class
#
import numpy as np
from .._base import *

__all__ = ['ParserType', 'AnnotationParser']


class AnnotationParser(Parser):
    """ This is a generic annotations parser class.
    Custom parsers should inherit from this class and overwrite the :func:`~brambox.io.annotation._base.AnnotationParser.serialize` and
    :func:`~brambox.io.annotation._base.AnnotationParser.deserialize` functions, as well as the necessary parameters.
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
            'occluded': [],
            'truncated': [],
            'lost': [],
            'difficult': [],
            'ignore': [],
        }

    def append(self, image, class_label, x_top_left, y_top_left, width, height,
               id=None, occluded=0.0, truncated=0.0, lost=False, difficult=False, ignore=False):
        """ Append an annotation to the data.

        Args:
            image (string): Image identifier
            class_label (string): Class label
            x_top_left (number): X pixel coordinate of the top left corner of the bounding box
            y_top_left (number): Y pixel coordinate of the top left corner of the bounding box
            width (number): Width of the bounding box in pixels
            height (number): Height of the bounding box in pixels
            id (number, optional): unique id of the bounding box
            occluded (number, optional): occlusion fraction
            truncated (number, optional): truncation fraction
            lost (boolean, optional): Whether the annotation is considered to be lost
            difficult (boolean, optional): Whether the annotation is considered to be difficult
            ignore (boolean, optional): Whether to ignore this annotation in certain metrics and statistics
        """
        self.images.add(image)
        self.data['image'].append(image)
        self.data['class_label'].append(class_label)
        self.data['id'].append(id if id is not None else np.nan)
        self.data['x_top_left'].append(x_top_left)
        self.data['y_top_left'].append(y_top_left)
        self.data['width'].append(width)
        self.data['height'].append(height)
        self.data['occluded'].append(occluded)
        self.data['truncated'].append(truncated)
        self.data['lost'].append(lost)
        self.data['difficult'].append(difficult)
        self.data['ignore'].append(ignore)
